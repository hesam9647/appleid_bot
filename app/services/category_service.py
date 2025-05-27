from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from app.database import ProductCategory

class CategoryService:
    def __init__(self, session: Session):
        self.session = session

    async def create_category(
        self,
        name: str,
        description: str = None,
        parent_id: int = None
    ) -> ProductCategory:
        category = ProductCategory(
            name=name,
            description=description,
            parent_id=parent_id
        )
        self.session.add(category)
        await self.session.commit()
        return category

    async def get_categories(self, parent_id: Optional[int] = None) -> List[ProductCategory]:
        query = select(ProductCategory).where(
            ProductCategory.is_active == True
        )
        
        if parent_id is not None:
            query = query.where(ProductCategory.parent_id == parent_id)
        else:
            query = query.where(ProductCategory.parent_id.is_(None))
            
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_category_tree(self) -> List[dict]:
        categories = await self.get_categories()
        tree = []
        
        for category in categories:
            cat_dict = {
                'id': category.id,
                'name': category.name,
                'subcategories': await self.get_categories(category.id)
            }
            tree.append(cat_dict)
            
        return tree
