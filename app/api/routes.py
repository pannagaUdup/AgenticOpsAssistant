from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_llm_provider, get_request_router
from app.db.session import get_db_session
from app.llm.errors import LLMProviderError
from app.llm.provider import LLMProvider
from app.repositories.account_repository import get_account_by_external_id
from app.schemas.account import AccountRead
from app.schemas.ai import InvestigationRequest, InvestigationState
from app.services.investigation import InvestigationService
from app.services.router import RequestRouter
from app.tools.read_tools import build_read_tool_registry

router = APIRouter(prefix="/api/v1", tags=["accounts"])
logger = structlog.get_logger(__name__)


@router.get(
    "/accounts/{external_id}",
    response_model=AccountRead,
)
async def get_account(
    external_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AccountRead:
    account = await get_account_by_external_id(session, external_id)

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {external_id} not found",
        )

    return account


@router.post("/investigations", response_model=InvestigationState, tags=["investigations"])
async def investigate(
    request: InvestigationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    provider: Annotated[LLMProvider, Depends(get_llm_provider)],
    router: Annotated[RequestRouter, Depends(get_request_router)],
) -> InvestigationState:
    """Run one bounded investigation and return its trace for debugging."""
    logger.info("investigation_started", account_id=request.account_id, question=request.question)
    service = InvestigationService(
        provider=provider,
        tool_registry=build_read_tool_registry(session),
        router=router,
    )
    try:
        state = await service.investigate(request)
    except LLMProviderError as exc:
        logger.error("investigation_provider_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The model provider is temporarily unavailable. "
                "Check provider credentials or billing."
            ),
        ) from exc
    logger.info(
        "investigation_completed",
        investigation_id=state.investigation_id,
        intent=state.routing.intent.value if state.routing else None,
        tool_calls=len(state.tool_calls),
        completed=state.completed,
    )
    return state
