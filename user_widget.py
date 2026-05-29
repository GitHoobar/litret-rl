"""Widget that renders a user's email."""

from user_api import fetch_user


def render_user(uid):
    """Render the user's email."""
    user = fetch_user(uid, include_email=True)
    return user["email"]
