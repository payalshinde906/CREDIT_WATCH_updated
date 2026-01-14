import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import selectinload
from app.models import CMSPage, CMSSection
from app.schemas.cms import CMSPageCreate, CMSPageUpdate, CMSSectionCreate, CMSSectionUpdate
from app.exceptions import NotFoundException, BadRequestException

class CMSService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Page Methods ---

    async def get_page_by_slug(self, slug: str) -> Optional[CMSPage]:
        stmt = select(CMSPage).options(selectinload(CMSPage.sections)).where(CMSPage.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pages(self) -> List[CMSPage]:
        stmt = select(CMSPage).order_by(CMSPage.updated_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_page(self, page_data: CMSPageCreate) -> CMSPage:
        # Check slug uniqueness
        existing = await self.get_page_by_slug(page_data.slug)
        if existing:
            raise BadRequestException(f"Page with slug '{page_data.slug}' already exists")

        new_page = CMSPage(
            id=str(uuid.uuid4()),
            **page_data.dict()
        )
        self.db.add(new_page)
        await self.db.commit()
        await self.db.refresh(new_page)
        return new_page

    async def update_page(self, page_id: str, updates: CMSPageUpdate) -> CMSPage:
        stmt = select(CMSPage).where(CMSPage.id == page_id)
        result = await self.db.execute(stmt)
        page = result.scalar_one_or_none()
        
        if not page:
            raise NotFoundException("Page not found")

        update_data = updates.dict(exclude_unset=True)
        if "slug" in update_data and update_data["slug"] != page.slug:
             # Check if new slug taken
             existing = await self.get_page_by_slug(update_data["slug"])
             if existing and existing.id != page_id:
                 raise BadRequestException(f"Slug '{update_data['slug']}' is already in use")

        for key, value in update_data.items():
            setattr(page, key, value)

        await self.db.commit()
        await self.db.refresh(page)
        return page

    async def delete_page(self, page_id: str):
        stmt = select(CMSPage).where(CMSPage.id == page_id)
        result = await self.db.execute(stmt)
        page = result.scalar_one_or_none()
        if not page:
            raise NotFoundException("Page not found")
        
        await self.db.delete(page)
        await self.db.commit()

    # --- Section Methods ---

    async def add_section(self, page_id: str, section_data: CMSSectionCreate) -> CMSSection:
        # Verify page exists
        stmt = select(CMSPage).where(CMSPage.id == page_id)
        result = await self.db.execute(stmt)
        if not result.scalar_one_or_none():
            raise NotFoundException("Page not found")

        section = CMSSection(
            id=str(uuid.uuid4()),
            page_id=page_id,
            **section_data.dict()
        )
        self.db.add(section)
        await self.db.commit()
        await self.db.refresh(section)
        return section

    async def update_section(self, section_id: str, updates: CMSSectionUpdate) -> CMSSection:
        stmt = select(CMSSection).where(CMSSection.id == section_id)
        result = await self.db.execute(stmt)
        section = result.scalar_one_or_none()
        
        if not section:
            raise NotFoundException("Section not found")

        update_data = updates.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(section, key, value)

        await self.db.commit()
        await self.db.refresh(section)
        return section

    async def delete_section(self, section_id: str):
        stmt = select(CMSSection).where(CMSSection.id == section_id)
        result = await self.db.execute(stmt)
        section = result.scalar_one_or_none()
        
        if not section:
            raise NotFoundException("Section not found")
            
        await self.db.delete(section)
        await self.db.commit()

    async def reorder_sections(self, page_id: str, section_orders: List[Dict[str, Any]]):
        """
        section_orders: List of { "id": "section_id", "order_index": 1 }
        """
        # Batch update is tricky in ORM, but we can iterate. 
        # For efficiency, we verify they belong to the page.
        
        for item in section_orders:
            stmt = update(CMSSection).\
                where(CMSSection.id == item['id']).\
                where(CMSSection.page_id == page_id).\
                values(order_index=item['order_index'])
            await self.db.execute(stmt)
            
        await self.db.commit()
