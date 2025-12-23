from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database.access_request import AccessRequest


async def get_access_requests(db: AsyncSession):
    result = await db.execute(
        select(AccessRequest).order_by(AccessRequest.created_at.desc())
    )
    return result.scalars().all()
