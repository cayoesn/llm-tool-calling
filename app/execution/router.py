import asyncio
import graphlib
import logging
from typing import List, Dict, Any, Set
from app.execution.engine import ExecutionEngine
from app.schemas.tool import ToolCall, ToolResult, ToolExecutionStatus

logger = logging.getLogger(__name__)


class ToolRouter:
    """Enterprise Tool Router with DAG Topological Scheduling.
    
    Permite executar grafos de chamadas de ferramentas com dependências explícitas (DAG),
    executando nós independentes em ondas paralelas concorrentes via asyncio.gather e
    propagando cancelamentos (fail-fast / skip) para nós descendentes se uma dependência falhar.
    """

    def __init__(self, execution_engine: ExecutionEngine):
        self.execution_engine = execution_engine

    async def dispatch(self, tool_calls: List[ToolCall], parallel: bool = True) -> List[ToolResult]:
        """Despacha chamadas de ferramentas respeitando dependências via DAG Scheduler."""
        if not tool_calls:
            return []

        # Se houver qualquer dependência declarada em depends_on, usar o escalonador DAG
        has_dependencies = any(bool(call.depends_on) for call in tool_calls)
        if has_dependencies:
            return await self.dispatch_dag(tool_calls)

        if parallel:
            return await self._dispatch_parallel(tool_calls)
        else:
            return await self._dispatch_sequential(tool_calls)

    async def dispatch_dag(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Executa chamadas de ferramentas organizadas em um Grafo Acíclico Dirigido (DAG).
        
        Nós independentes no mesmo nível topológico são executados concorrentemente.
        """
        calls_by_id: Dict[str, ToolCall] = {call.call_id: call for call in tool_calls}
        results_by_id: Dict[str, ToolResult] = {}
        failed_ids: Set[str] = set()

        # Monta grafo de dependências: dependência -> dependente
        graph_dict: Dict[str, Set[str]] = {call.call_id: set() for call in tool_calls}
        for call in tool_calls:
            for dep_id in call.depends_on:
                if dep_id in calls_by_id:
                    graph_dict[call.call_id].add(dep_id)

        try:
            ts = graphlib.TopologicalSorter(graph_dict)
            ts.prepare()
        except graphlib.CycleError as e:
            logger.error(f"Cycle detected in tool execution DAG: {e}")
            return [
                ToolResult(
                    call_id=call.call_id,
                    tool_name=call.tool_name,
                    status=ToolExecutionStatus.FAILED,
                    output=None,
                    error=f"Ciclo detectado no grafo de dependências: {e}",
                    execution_time=0.0
                )
                for call in tool_calls
            ]

        while ts.is_active():
            ready_nodes = ts.get_ready()
            if not ready_nodes:
                break

            tasks_to_run = []
            skipped_nodes = []

            for node_id in ready_nodes:
                tool_call = calls_by_id[node_id]
                # Verifica se alguma dependência falhou
                active_deps = set(tool_call.depends_on)
                failed_deps = active_deps.intersection(failed_ids)

                if failed_deps:
                    skipped_result = ToolResult(
                        call_id=node_id,
                        tool_name=tool_call.tool_name,
                        status=ToolExecutionStatus.SKIPPED,
                        output=None,
                        error=f"Dependência anterior falhou: {list(failed_deps)}",
                        execution_time=0.0
                    )
                    results_by_id[node_id] = skipped_result
                    failed_ids.add(node_id)
                    skipped_nodes.append(node_id)
                else:
                    tasks_to_run.append((node_id, self.execution_engine.execute_tool(tool_call)))

            for node_id in skipped_nodes:
                ts.done(node_id)

            if tasks_to_run:
                # Executa todos os nós independentes da onda corrente concorrentemente
                node_ids = [item[0] for item in tasks_to_run]
                coros = [item[1] for item in tasks_to_run]
                batch_results = await asyncio.gather(*coros)

                for node_id, result in zip(node_ids, batch_results):
                    results_by_id[node_id] = result
                    if result.status != ToolExecutionStatus.SUCCESS:
                        failed_ids.add(node_id)
                    ts.done(node_id)

        # Retorna na ordem original de tool_calls
        return [results_by_id.get(call.call_id) for call in tool_calls if call.call_id in results_by_id]

    async def _dispatch_parallel(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        tasks = [self.execution_engine.execute_tool(call) for call in tool_calls]
        return list(await asyncio.gather(*tasks))

    async def _dispatch_sequential(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        results = []
        for call in tool_calls:
            result = await self.execution_engine.execute_tool(call)
            results.append(result)
        return results
