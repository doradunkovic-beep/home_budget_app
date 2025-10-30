from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer, String, label

from .. import models


def create_expense_in_db(db: Session, title: str, amount, description: Optional[str], date: Optional[datetime], category_id: int, user_id: int):
    """
    Create a new Expense for the given user.
    """
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    new_expense = models.Expense(
        title=title,
        amount=amount,
        description=description,
        date=date or datetime.utcnow(),
        category_id=category_id,
        user_id=user_id,
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


def get_expenses_for_user(db: Session, user_id: int, category_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
    min_amount: Optional[float] = None, max_amount: Optional[float] = None):
    """
    Return expenses for a user with optional filtering
    """
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)

    if category_id is not None:
        query = query.filter(models.Expense.category_id == category_id)
    if start_date is not None:
        query = query.filter(models.Expense.date >= start_date)
    if end_date is not None:
        query = query.filter(models.Expense.date <= end_date)
    if min_amount is not None:
        query = query.filter(models.Expense.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(models.Expense.amount <= max_amount)

    return query.all()


def get_expense_for_user(db: Session, expense_id: int, user_id: int):
    """
    Return a single expense owned by the user or raise 404.
    """
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    
    return expense


def update_expense_in_db(db: Session, expense_id: int, user_id: int, title: str, amount, description: Optional[str], date: Optional[datetime], category_id: int):
    """
    Update an expense. Verifies expense and category ownership. Raises 404 when missing.
    """
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    expense.title = title
    expense.amount = amount
    expense.description = description
    expense.date = date or expense.date
    expense.category_id = category_id
    db.commit()
    db.refresh(expense)

    return expense


def delete_expense_in_db(db: Session, expense_id: int, user_id: int):
    """
    Delete an expense owned by the user. Raises 404 when missing.
    """
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    
    db.delete(expense)
    db.commit()

    return


def get_expense_summary_util(db: Session, user_id: int, period: str = "month"):
    """
    Return summary data: total per category and total per period (month/quarter/year).
    """
    category_totals = (
        db.query(models.Category.name, func.sum(models.Expense.amount))
        .join(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .group_by(models.Category.id)
        .all()
    )

    if period == "month":
        period_total = (
            db.query(func.strftime("%Y-%m", models.Expense.date), func.sum(models.Expense.amount))
            .filter(models.Expense.user_id == user_id)
            .group_by(func.strftime("%Y-%m", models.Expense.date))
            .all()
        )
    elif period == "quarter":
        quarter_label = label(
            "quarter",
            (func.strftime("%Y", models.Expense.date) + "-" +
            ((func.strftime("%m", models.Expense.date).cast(Integer)-1)/3 + 1).cast(String))
        )

        period_total = (
            db.query(quarter_label, func.sum(models.Expense.amount))
            .filter(models.Expense.user_id == user_id)
            .group_by(quarter_label)
            .all()
        )
    else:  # year
        period_total = (
            db.query(func.strftime("%Y", models.Expense.date), func.sum(models.Expense.amount))
            .filter(models.Expense.user_id == user_id)
            .group_by(func.strftime("%Y", models.Expense.date))
            .all()
        )

    return {
        "total_per_category": [{"category": c, "total": t} for c, t in category_totals],
        "total_per_period": [{"period": p, "total": t} for p, t in period_total],
    }
