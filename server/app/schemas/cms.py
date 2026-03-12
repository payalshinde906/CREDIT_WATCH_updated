from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Shared Schemas ---

class CMSSectionBase(BaseModel):
    type: str
    order_index: int = 0
    is_visible: bool = True
    content: Dict[str, Any] = {}

class CMSSectionCreate(CMSSectionBase):
    pass

class CMSSectionUpdate(BaseModel):
    type: Optional[str]
    order_index: Optional[int]
    is_visible: Optional[bool]
    content: Optional[Dict[str, Any]]

class CMSSectionResponse(CMSSectionBase):
    id: str
    page_id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Page Schemas ---

class CMSPageBase(BaseModel):
    slug: str
    title: str
    is_published: bool = False
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

class CMSPageCreate(CMSPageBase):
    pass

class CMSPageUpdate(BaseModel):
    slug: Optional[str]
    title: Optional[str]
    is_published: Optional[bool]
    seo_title: Optional[str]
    seo_description: Optional[str]

class CMSPageResponse(CMSPageBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    sections: List[CMSSectionResponse] = []

    class Config:
        from_attributes = True

class CMSPageListResponse(BaseModel):
    id: str
    slug: str
    title: str
    is_published: bool
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
