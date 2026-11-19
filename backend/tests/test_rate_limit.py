
import uuid

import pytest
from fastapi import HTTPException

from app.core.rate_limit import (
    check_rate_limit,
    redis_client,
)


def test_rate_limit_exceeded():
    key = f"auth:test:{uuid.uuid4()}"

    try:
        check_rate_limit(key, limit=2, window_seconds=60)
        check_rate_limit(key, limit=2, window_seconds=60)

        with pytest.raises(HTTPException) as exc:
            check_rate_limit(
                key,
                limit=2,
                window_seconds=60,
            )

        assert exc.value.status_code == 429
        assert "Retry-After" in exc.value.headers

    finally:
        redis_client.delete(key)
