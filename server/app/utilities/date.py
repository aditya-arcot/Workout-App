from datetime import datetime


def get_utc_timestamp_str(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
