"""Base repository with CRUD operations and tenant filtering."""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository implementing CRUD operations with tenant filtering.
    
    Provides:
    - get: Retrieve single record by ID
    - get_multi: Retrieve multiple records with pagination
    - create: Create new record
    - update: Update existing record
    - delete: Soft delete record
    - All operations support optional tenant filtering
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def get(self, id: int, tenant_id: Optional[int] = None) -> Optional[ModelType]:
        """
        Get single record by ID with optional tenant filter.
        
        Args:
            id: Record ID
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            Model instance or None if not found
        """
        query = select(self.model).where(
            and_(
                self.model.id == id,
                self.model.is_deleted == False,
            )
        )
        
        # Add tenant filter if model has tenant_id and tenant_id is provided
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.where(self.model.tenant_id == tenant_id)
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            tenant_id: Optional tenant ID for filtering
            filters: Optional dictionary of field:value filters
            
        Returns:
            List of model instances
        """
        query = select(self.model).where(self.model.is_deleted == False)
        
        # Add tenant filter if model has tenant_id and tenant_id is provided
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.where(self.model.tenant_id == tenant_id)
        
        # Add additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        query = query.offset(skip).limit(limit)
        result = self.db.execute(query)
        return list(result.scalars().all())

    def count(
        self,
        tenant_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Count records with optional filtering.
        
        Args:
            tenant_id: Optional tenant ID for filtering
            filters: Optional dictionary of field:value filters
            
        Returns:
            Count of matching records
        """
        from sqlalchemy import func
        
        query = select(func.count(self.model.id)).where(self.model.is_deleted == False)
        
        # Add tenant filter if model has tenant_id and tenant_id is provided
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.where(self.model.tenant_id == tenant_id)
        
        # Add additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        result = self.db.execute(query)
        return result.scalar_one()

    def create(self, obj_in: Dict[str, Any], tenant_id: Optional[int] = None) -> ModelType:
        """
        Create new record.
        
        Args:
            obj_in: Dictionary of field values
            tenant_id: Optional tenant ID to set
            
        Returns:
            Created model instance
        """
        # Add tenant_id if model supports it and tenant_id is provided
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            obj_in["tenant_id"] = tenant_id
        
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        id: int,
        obj_in: Dict[str, Any],
        tenant_id: Optional[int] = None,
    ) -> Optional[ModelType]:
        """
        Update existing record.
        
        Args:
            id: Record ID
            obj_in: Dictionary of field values to update
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            Updated model instance or None if not found
        """
        db_obj = self.get(id=id, tenant_id=tenant_id)
        if db_obj is None:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int, tenant_id: Optional[int] = None) -> bool:
        """
        Soft delete record.
        
        Args:
            id: Record ID
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get(id=id, tenant_id=tenant_id)
        if db_obj is None:
            return False
        
        db_obj.soft_delete()
        self.db.commit()
        return True

    def hard_delete(self, id: int, tenant_id: Optional[int] = None) -> bool:
        """
        Permanently delete record from database.
        
        Args:
            id: Record ID
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get(id=id, tenant_id=tenant_id)
        if db_obj is None:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def restore(self, id: int, tenant_id: Optional[int] = None) -> Optional[ModelType]:
        """
        Restore a soft-deleted record.
        
        Args:
            id: Record ID
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            Restored model instance or None if not found
        """
        # Query including deleted records
        query = select(self.model).where(self.model.id == id)
        
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.where(self.model.tenant_id == tenant_id)
        
        result = self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        
        if db_obj is None:
            return None
        
        db_obj.restore()
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
