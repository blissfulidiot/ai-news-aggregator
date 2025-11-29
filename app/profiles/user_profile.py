"""User profile management"""

from typing import Optional
from app.database.connection import get_db_session
from app.database.repository import UserSettingsRepository


class UserProfile:
    """User profile manager"""
    
    @staticmethod
    def get_profile(email: str) -> Optional[dict]:
        """
        Get user profile by email
        
        Args:
            email: User's email address
            
        Returns:
            Dictionary with profile data or None if not found
        """
        db_gen = get_db_session()
        db = next(db_gen)
        try:
            user = UserSettingsRepository.get_by_email(db, email)
            if not user:
                return None
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name or "",
                "background": user.background or "",
                "interests": user.interests or "",
                "system_prompt": user.system_prompt
            }
        finally:
            db.close()
    
    @staticmethod
    def create_or_update(email: str, name: Optional[str] = None, 
                         background: Optional[str] = None,
                         interests: Optional[str] = None,
                         system_prompt: Optional[str] = None) -> dict:
        """
        Create or update user profile
        
        Args:
            email: User's email (required)
            name: User's name
            background: User's background/profession
            interests: User's interests
            system_prompt: Custom system prompt
            
        Returns:
            Dictionary with updated profile data
        """
        db_gen = get_db_session()
        db = next(db_gen)
        try:
            user = UserSettingsRepository.get_by_email(db, email)
            
            if user:
                # Update existing user
                update_data = {}
                if name is not None:
                    update_data["name"] = name
                if background is not None:
                    update_data["background"] = background
                if interests is not None:
                    update_data["interests"] = interests
                if system_prompt is not None:
                    update_data["system_prompt"] = system_prompt
                
                UserSettingsRepository.update(db, user.id, **update_data)
                db.refresh(user)
            else:
                # Create new user
                user = UserSettingsRepository.create(
                    db,
                    email=email,
                    name=name,
                    background=background,
                    interests=interests,
                    system_prompt=system_prompt
                )
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name or "",
                "background": user.background or "",
                "interests": user.interests or "",
                "system_prompt": user.system_prompt
            }
        finally:
            db.close()

