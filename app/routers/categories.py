from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..utils.auth import get_current_user
from ..utils.category_utils import create_category_in_db, get_category_for_user, get_categories_for_user, update_category_in_db, delete_category_in_db

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    """Create a new expense category."""
    return create_category_in_db(db, category.name, category.description, current_user.id)

@router.get("/", response_model=List[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    """Get user's categories."""
    return get_categories_for_user(db, current_user.id)

@router.get("/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    """Get user's category by ID."""
    return get_category_for_user(db, category_id, current_user.id)

@router.put("/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, category_data: schemas.CategoryCreate,
                    db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    """Update an existing category."""
    return update_category_in_db(db, category_id, current_user.id, category_data.name, category_data.description)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    """Delete a category."""
    return delete_category_in_db(db, category_id, current_user.id)
