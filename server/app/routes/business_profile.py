"""
Business Profile management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.business_profile import (
    BusinessProfileResponse,
    BusinessProfileUpdateRequest,
    FileUploadRequest,
)
from app.services.business_profile_service import BusinessProfileService
from app.services.drive_service import DriveService
from app.exceptions import UserNotFound
from app.utils.response import ResponseFormatter
from app.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/profile", response_model=dict)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's business profile
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Business profile details
    """
    try:
        profile = await BusinessProfileService.get_profile(
            user_id=current_user["id"],
            db=db,
        )
        
        return ResponseFormatter.success(
            message="Profile retrieved",
            data={
                "id": profile.id,
                "user_id": profile.user_id,
                "name": profile.name,
                "registered_name": profile.registered_name,
                "email": profile.email,
                "phone": profile.phone,
                "gstin": profile.gstin,
                "profile_photo_url": profile.profile_photo_url,
                "company_logo_url": profile.company_logo_url,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            },
        )
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile",
        )


@router.put("/profile", response_model=dict)
async def update_profile(
    request: BusinessProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update business profile
    
    Args:
        request: Profile update request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated profile details
    """
    try:
        updates = request.dict(exclude_unset=True)
        
        profile = await BusinessProfileService.update_profile(
            user_id=current_user["id"],
            updates=updates,
            db=db,
        )
        
        await db.commit()
        
        return ResponseFormatter.success(
            message="Profile updated successfully",
            data={
                "id": profile.id,
                "name": profile.name,
                "registered_name": profile.registered_name,
                "email": profile.email,
                "phone": profile.phone,
                "gstin": profile.gstin,
                "profile_photo_url": profile.profile_photo_url,
                "company_logo_url": profile.company_logo_url,
            },
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )


@router.post("/profile-photo", response_model=dict)
async def upload_profile_photo(
    file_request: FileUploadRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Set profile photo from Google Drive URL
    
    Args:
        file_request: File upload request with Drive URL
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated profile with photo URL
    """
    try:
        profile = await BusinessProfileService.set_profile_photo(
            user_id=current_user["id"],
            photo_url=file_request.drive_url,
            db=db,
        )
        
        await db.commit()
        
        return ResponseFormatter.success(
            message="Profile photo updated",
            data={"profile_photo_url": profile.profile_photo_url},
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating profile photo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile photo",
        )


@router.post("/company-logo", response_model=dict)
async def upload_company_logo(
    file_request: FileUploadRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Set company logo from Google Drive URL
    
    Args:
        file_request: File upload request with Drive URL
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated profile with logo URL
    """
    try:
        profile = await BusinessProfileService.set_company_logo(
            user_id=current_user["id"],
            logo_url=file_request.drive_url,
            db=db,
        )
        
        await db.commit()
        
        return ResponseFormatter.success(
            message="Company logo updated",
            data={"company_logo_url": profile.company_logo_url},
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating company logo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update company logo",
        )
