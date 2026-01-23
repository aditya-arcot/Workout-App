import logging
from typing import Any

import httpx

from app.core.config import settings
from app.models.database.feedback import Feedback
from app.models.schemas.feedback import FeedbackType
from app.utilities.date import get_utc_timestamp_str

logger = logging.getLogger(__name__)

GITHUB_API_URL_REPO = (
    f"https://api.github.com/repos/{settings.REPO_OWNER}/{settings.REPO_NAME}"
)

HEADERS = {
    "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


async def create_feedback_issue(
    feedback: Feedback,
):
    logging.info(f"Creating GitHub issue for feedback id: {feedback.id}")

    url = f"{GITHUB_API_URL_REPO}/issues"

    if feedback.type == FeedbackType.feedback:
        title = f"[Feedback] {feedback.title}"
    else:
        title = f"[Feature Request] {feedback.title}"

    body_lines = [
        "### Details",
        f"**Timestamp:** {get_utc_timestamp_str(feedback.created_at)}",
        f"**ID:** {feedback.id}",
        f"**User ID:** {feedback.user_id}",
        f"**URL:** {feedback.url}",
        "",
        "### Description",
        feedback.description,
    ]

    if feedback.files:
        body_lines.extend(
            [
                "",
                "### Attachments",
            ]
        )
        for file in feedback.files:
            body_lines.append(f"- {file.original_name} (`{file.path}`)")

    body = "\n".join(body_lines)

    payload: dict[str, Any] = {
        "title": title,
        "body": body,
        "assignees": [settings.REPO_OWNER],
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()

    logging.info(f"Created GitHub issue for feedback id: {feedback.id}")
