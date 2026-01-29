import logging
from typing import Literal

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from app.models.database.access_request import AccessRequest
from app.models.database.user import User
from app.models.enums import AccessRequestStatus
from app.models.errors import AccessRequestStatusError, NotFound
from app.models.schemas.access_request import AccessRequestPublic
from app.models.schemas.user import UserPublic

logger = logging.getLogger(__name__)


status_priority = case(
    (AccessRequest.status == "pending", 1),
    (AccessRequest.status == "approved", 2),
    (AccessRequest.status == "rejected", 3),
)


async def get_access_requests(db: AsyncSession) -> list[AccessRequestPublic]:
    logger.info("Getting access requests")

    result = await db.execute(
        select(AccessRequest)
        .options(selectinload(AccessRequest.reviewer))
        .order_by(status_priority)
        .order_by(AccessRequest.updated_at.desc())
        .order_by(AccessRequest.id.desc())
    )
    return [
        AccessRequestPublic.model_validate(ar, from_attributes=True)
        for ar in result.scalars().all()
    ]


async def update_access_request_status(
    access_request_id: int,
    status: Literal[AccessRequestStatus.APPROVED, AccessRequestStatus.REJECTED],
    db: AsyncSession,
    user: UserPublic,
) -> None:
    logger.info(f"Updating access request {access_request_id} to status {status}")

    access_request = (
        await db.execute(
            select(AccessRequest).where(AccessRequest.id == access_request_id)
        )
    ).scalar_one_or_none()

    if not access_request:
        logger.error(f"Access request {access_request_id} not found")
        raise NotFound()

    if access_request.status != AccessRequestStatus.PENDING:
        raise AccessRequestStatusError()

    access_request.status = status
    access_request.reviewed_at = func.now()
    access_request.reviewed_by = user.id
    await db.commit()

    # TODO send email


async def get_users(db: AsyncSession) -> list[UserPublic]:
    logger.info("Getting users")

    result = await db.execute(
        select(User)
        .order_by(User.username.asc())
        .order_by(User.updated_at.desc())
        .order_by(User.id.desc())
    )
    return [
        UserPublic.model_validate(user, from_attributes=True)
        for user in result.scalars().all()
    ]
