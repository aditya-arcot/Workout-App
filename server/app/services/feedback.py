import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database.feedback import Feedback
from app.models.schemas.feedback import CreateFeedbackRequest
from app.models.schemas.user import UserPublic
from app.services.github import GitHubService
from app.services.storage import store_files

logger = logging.getLogger(__name__)

FEEDBACK_DIR = settings.DATA_DIR / "feedback"


async def create_feedback(
    user: UserPublic,
    payload: CreateFeedbackRequest,
    db: AsyncSession,
    github_svc: GitHubService,
):
    logger.info(
        f"Received feedback from user {user.username} with title: {payload.title}"
    )

    stored_files = await store_files(payload.files, FEEDBACK_DIR)
    feedback = Feedback(
        user_id=user.id,
        type=payload.type,
        url=payload.url,
        title=payload.title,
        description=payload.description,
        files=stored_files,
    )

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    await github_svc.create_feedback_issue(feedback)

    logger.info(f"Stored feedback from user {user.username} with id: {feedback.id}")
