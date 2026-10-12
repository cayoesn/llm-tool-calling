import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.schemas.tool import ToolCall, ToolResult, ToolExecutionStatus
from app.execution.router import ToolRouter


@pytest.mark.asyncio
async def test_tool_router_dag_execution_order():
    """Verifica se ferramentas com dependências respeitam o ordenamento topológico."""
    mock_engine = MagicMock()

    call_a = ToolCall(call_id="call_a", tool_name="fetch_data", arguments={"query": "users"})
    call_b = ToolCall(call_id="call_b", tool_name="aggregate", arguments={"factor": 2}, depends_on=["call_a"])

    execution_order = []

    async def mock_execute(call):
        execution_order.append(call.call_id)
        return ToolResult(
            call_id=call.call_id,
            tool_name=call.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            output=f"result_{call.call_id}",
            execution_time=0.01,
        )

    mock_engine.execute_tool = AsyncMock(side_effect=mock_execute)
    router = ToolRouter(execution_engine=mock_engine)

    results = await router.dispatch([call_b, call_a])  # Passa em ordem inversa

    assert len(results) == 2
    assert execution_order == ["call_a", "call_b"]
    assert results[0].call_id == "call_b"
    assert results[1].call_id == "call_a"
    assert results[0].status == ToolExecutionStatus.SUCCESS
    assert results[1].status == ToolExecutionStatus.SUCCESS


@pytest.mark.asyncio
async def test_tool_router_dag_failure_skip_propagation():
    """Verifica se a falha em um nó pai propaga status SKIPPED para os nós filhos."""
    mock_engine = MagicMock()

    call_a = ToolCall(call_id="call_a", tool_name="database_query", arguments={"sql": "SELECT *"})
    call_b = ToolCall(call_id="call_b", tool_name="export_csv", arguments={}, depends_on=["call_a"])

    async def mock_execute(call):
        if call.call_id == "call_a":
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                status=ToolExecutionStatus.FAILED,
                output=None,
                error="DB Connection Timeout",
                execution_time=0.01,
            )
        return ToolResult(
            call_id=call.call_id,
            tool_name=call.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            output="ok",
            execution_time=0.01,
        )

    mock_engine.execute_tool = AsyncMock(side_effect=mock_execute)
    router = ToolRouter(execution_engine=mock_engine)

    results = await router.dispatch([call_a, call_b])

    assert len(results) == 2
    res_a = next(r for r in results if r.call_id == "call_a")
    res_b = next(r for r in results if r.call_id == "call_b")

    assert res_a.status == ToolExecutionStatus.FAILED
    assert res_b.status == ToolExecutionStatus.SKIPPED
    assert "Dependência anterior falhou" in res_b.error


@pytest.mark.asyncio
async def test_tool_router_dag_cycle_detection():
    """Verifica detecção e prevenção de deadlock em ciclos de dependência."""
    mock_engine = MagicMock()
    router = ToolRouter(execution_engine=mock_engine)

    call_a = ToolCall(call_id="call_a", tool_name="tool_1", arguments={}, depends_on=["call_b"])
    call_b = ToolCall(call_id="call_b", tool_name="tool_2", arguments={}, depends_on=["call_a"])

    results = await router.dispatch([call_a, call_b])

    assert len(results) == 2
    assert all(r.status == ToolExecutionStatus.FAILED for r in results)
    assert any("Ciclo detectado" in r.error for r in results)
