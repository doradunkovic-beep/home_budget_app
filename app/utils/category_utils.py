from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..utils.constants import PREDEFINED_CATEGORIES


def create_category_in_db(db: Session, name: str, description: Optional[str], user_id: int):
    """Create a new Category for the given user.
    :param db: SQLAlchemy session.
    :name name: Category name.
    :param description: Category description.
    :param user_id: Owner user's id.
    """
    normalised_name = name.strip()

    existing = db.query(models.Category).filter(models.Category.user_id == user_id, models.Category.name == normalised_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

    new_category = models.Category(name=normalised_name, description=description, user_id=user_id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def get_categories_for_user(db: Session, user_id: int):
    """Return all categories belonging to a user."""
    return db.query(models.Category).filter(models.Category.user_id == user_id).all()


def get_category_for_user(db: Session, category_id: int, user_id: int) -> models.Category:
    """Return a single category owned by user or raise 404."""
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    return category


def update_category_in_db(db: Session, category_id: int, user_id: int, name: str, description: Optional[str]) -> models.Category:
    """Update a category's name/description. Raises 404 if not found."""
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    category.name = name
    category.description = description
    db.commit()
    db.refresh(category)
    return category


def delete_category_in_db(db: Session, category_id: int, user_id: int):
    """Delete a category owned by the user. Raises 404 if not found."""
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    db.delete(category)
    db.commit()


def create_predefined_categories_for_user(db: Session, user_id: int):
    """
    Creates predefined categories for a given (new) user.
    """
    for name in PREDEFINED_CATEGORIES:
        normalised_name = name.strip()
        category = models.Category(name=normalised_name, user_id=user_id)
        db.add(category)
    db.commit()
