from enum import Enum


class AccessRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class FeedbackType(str, Enum):
    feedback = "feedback"
    feature = "feature"
