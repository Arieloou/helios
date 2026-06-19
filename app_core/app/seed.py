"""
Database Seeder for Helios app_core.
Creates default admin user if no users exist.

Usage:
    & ".venv\Scripts\python.exe" -m app.seed
"""

import logging

from app import create_app
from app.models.base import db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

# Default admin credentials
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "adminpassword"
DEFAULT_ADMIN_EMAIL = "admin@helios.local"


def seed_admin_user():
    """Create default admin user if no users exist in the database."""
    existing_users = User.query.count()
    if existing_users > 0:
        logger.info(f"Database already has {existing_users} user(s). Skipping seed.")
        return False

    logger.info("No users found. Creating default admin user...")
    result = AuthService.create_user(
        username=DEFAULT_ADMIN_USERNAME,
        password=DEFAULT_ADMIN_PASSWORD,
        email=DEFAULT_ADMIN_EMAIL,
        role=UserRole.ADMIN,
    )

    if result["success"]:
        logger.info(
            f"Admin user created successfully: "
            f"username='{DEFAULT_ADMIN_USERNAME}', role='admin'"
        )
        return True
    else:
        logger.error(f"Failed to create admin user: {result['error']}")
        return False


def run_seed():
    """Run the seeder within Flask app context."""
    app = create_app()
    with app.app_context():
        seed_admin_user()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    print("[Seeder] Starting Helios database seeder...")
    run_seed()
    print("[Seeder] Done.")
