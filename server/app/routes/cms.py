from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.database import get_db
from app.dependencies import require_admin
from app.models import User
from app.services.cms_service import CMSService
from app.schemas.cms import (
    CMSPageResponse, CMSPageListResponse, CMSPageCreate, CMSPageUpdate,
    CMSSectionResponse, CMSSectionCreate, CMSSectionUpdate
)
from app.utils.response import ResponseFormatter

router = APIRouter(prefix="/cms", tags=["CMS"])

# --- Public Routes ---

@router.get("/pages/{slug}", response_model=ResponseFormatter[CMSPageResponse])
async def get_page_public(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a page by slug (Public view)"""
    service = CMSService(db)
    page = await service.get_page_by_slug(slug)
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # In production, we might filter `is_published` unless it's a preview mode
    # For now, we return it but frontend should handle draft status if needed
    
    return ResponseFormatter.create_success(data=page)


# --- Admin Routes (Pages) ---

@router.get("/admin/pages", response_model=ResponseFormatter[List[CMSPageListResponse]])
async def list_pages_admin(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all pages (Admin)"""
    service = CMSService(db)
    pages = await service.list_pages()
    return ResponseFormatter.create_success(data=pages)

@router.post("/admin/pages", response_model=ResponseFormatter[CMSPageResponse])
async def create_page_admin(
    page_data: CMSPageCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new page"""
    service = CMSService(db)
    page = await service.create_page(page_data)
    return ResponseFormatter.create_success(data=page, message="Page created successfully")

@router.put("/admin/pages/{page_id}", response_model=ResponseFormatter[CMSPageResponse])
async def update_page_admin(
    page_id: str,
    updates: CMSPageUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update page metadata"""
    service = CMSService(db)
    page = await service.update_page(page_id, updates)
    return ResponseFormatter.create_success(data=page, message="Page updated successfully")

@router.delete("/admin/pages/{page_id}")
async def delete_page_admin(
    page_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a page"""
    service = CMSService(db)
    await service.delete_page(page_id)
    return ResponseFormatter.create_success(message="Page deleted successfully")


# --- Admin Routes (Sections) ---

@router.post("/admin/pages/{page_id}/sections", response_model=ResponseFormatter[CMSSectionResponse])
async def add_section_admin(
    page_id: str,
    section_data: CMSSectionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Add a section to a page"""
    service = CMSService(db)
    section = await service.add_section(page_id, section_data)
    return ResponseFormatter.create_success(data=section, message="Section added")

@router.put("/admin/sections/{section_id}", response_model=ResponseFormatter[CMSSectionResponse])
async def update_section_admin(
    section_id: str,
    updates: CMSSectionUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a section content/settings"""
    service = CMSService(db)
    section = await service.update_section(section_id, updates)
    return ResponseFormatter.create_success(data=section, message="Section updated")

@router.delete("/admin/sections/{section_id}")
async def delete_section_admin(
    section_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a section"""
    service = CMSService(db)
    await service.delete_section(section_id)
    return ResponseFormatter.create_success(message="Section deleted")

@router.put("/admin/pages/{page_id}/reorder-sections")
async def reorder_sections_admin(
    page_id: str,
    payload: List[dict] = Body(..., description="List of objects with 'id' and 'order_index'"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Bulk reorder sections"""
    service = CMSService(db)
    await service.reorder_sections(page_id, payload)
    return ResponseFormatter.create_success(message="Sections reordered")
