"""Simple script to create admin user."""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.db.database import async_engine, local_session
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_admin_user():
    """Create admin user if it doesn't exist."""
    async with local_session() as session:
        try:
            # Check if admin user exists
            result = await session.execute(
                select(User).where(User.email == settings.ADMIN_EMAIL)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"Admin user {settings.ADMIN_EMAIL} already exists.")
                # Check if it's a superuser
                if existing_user.is_superuser:
                    print("User is already a superuser.")
                else:
                    # Update to superuser
                    existing_user.is_superuser = True
                    await session.commit()
                    print("Updated user to superuser.")
            else:
                # Create new admin user
                admin_user = User(
                    name=settings.ADMIN_NAME,
                    email=settings.ADMIN_EMAIL,
                    hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                    is_superuser=True
                )
                session.add(admin_user)
                await session.commit()
                print(f"Admin user {settings.ADMIN_EMAIL} created successfully!")
                print(f"Email: {settings.ADMIN_EMAIL}")
                print(f"Password: {settings.ADMIN_PASSWORD}")
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_admin_user())

