"""Minimal user API contract."""


def fetch_user(user_id):
    """Return the user record for the given id. Has no email field."""
    return {"id": user_id, "name": "unknown"}
