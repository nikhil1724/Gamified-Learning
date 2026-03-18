import threading
import time

from models import User


LEADERBOARD_CACHE_TTL_SECONDS = 8
LEADERBOARD_LIMIT = 10
LEADERBOARD_DELTA_MAX_CHANGES = 4

_cache_lock = threading.Lock()
_cached_rows = []
_cache_expires_at = 0.0
_last_broadcast_rows = []
_last_broadcast_version = 0


def _compute_leaderboard(limit: int = LEADERBOARD_LIMIT) -> list[dict]:
    users = (
        User.query.filter_by(role="student")
        .order_by(User.xp_points.desc(), User.coins.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "rank": index + 1,
            "id": user.id,
            "name": user.name,
            "level": user.level,
            "xp_points": user.xp_points,
            "coins": user.coins,
        }
        for index, user in enumerate(users)
    ]


def get_cached_leaderboard(force_refresh: bool = False) -> list[dict]:
    global _cached_rows
    global _cache_expires_at

    now = time.time()
    if not force_refresh and now < _cache_expires_at and _cached_rows:
        return _cached_rows

    with _cache_lock:
        now = time.time()
        if not force_refresh and now < _cache_expires_at and _cached_rows:
            return _cached_rows

        _cached_rows = _compute_leaderboard(limit=LEADERBOARD_LIMIT)
        _cache_expires_at = now + LEADERBOARD_CACHE_TTL_SECONDS
        return _cached_rows


def invalidate_leaderboard_cache() -> None:
    global _cache_expires_at

    with _cache_lock:
        _cache_expires_at = 0.0


def broadcast_leaderboard_update() -> None:
    global _last_broadcast_rows
    global _last_broadcast_version

    invalidate_leaderboard_cache()
    rows = get_cached_leaderboard(force_refresh=True)

    previous_by_id = {row["id"]: row for row in _last_broadcast_rows}
    current_by_id = {row["id"]: row for row in rows}

    changed_rows = [
        row
        for row in rows
        if row["id"] not in previous_by_id or previous_by_id[row["id"]] != row
    ]
    removed_ids = [user_id for user_id in previous_by_id if user_id not in current_by_id]

    _last_broadcast_version += 1
    version = _last_broadcast_version
    _last_broadcast_rows = rows

    from socketio_service import socketio

    if not changed_rows and not removed_ids:
        return

    if len(changed_rows) + len(removed_ids) <= LEADERBOARD_DELTA_MAX_CHANGES:
        socketio.emit(
            "leaderboard:update",
            {
                "mode": "delta",
                "version": version,
                "changed": changed_rows,
                "removed_ids": removed_ids,
            },
        )
        return

    socketio.emit(
        "leaderboard:update",
        {
            "mode": "full",
            "version": version,
            "rows": rows,
        },
    )


def build_full_leaderboard_payload() -> dict:
    global _last_broadcast_rows
    global _last_broadcast_version

    rows = get_cached_leaderboard()
    _last_broadcast_rows = rows
    _last_broadcast_version += 1

    return {
        "mode": "full",
        "version": _last_broadcast_version,
        "rows": rows,
    }
