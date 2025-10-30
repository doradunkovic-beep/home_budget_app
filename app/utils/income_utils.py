from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer, String, label

from .. import models


def create_income_in_db(db: Session, title: str, amount, description: Optional[str], date: Optional[datetime], user_id: int):
    """
    Create a new income record for the given user.
    """
    new_income = models.Income(
        title=title,
        amount=amount,
        description=description,
        date=date or datetime.utcnow(),
        user_id=user_id,
    )
    db.add(new_income)
    db.commit()
    db.refresh(new_income)

    return new_income


def get_incomes_for_user(db: Session, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
    min_amount: Optional[float] = None, max_amount: Optional[float] = None):
    """
    Return incomes for a user with optional filtering
    """
    query = db.query(models.Income).filter(models.Income.user_id == user_id)

    if start_date is not None:
        query = query.filter(models.Income.date >= start_date)
    if end_date is not None:
        query = query.filter(models.Income.date <= end_date)
    if min_amount is not None:
        query = query.filter(models.Income.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(models.Income.amount <= max_amount)

    return query.all()


def get_income_for_user(db: Session, income_id: int, user_id: int):
    """
    Return a single income owned by the user or raise 404.
    """
    income = db.query(models.Income).filter(
        models.Income.id == income_id,
        models.Income.user_id == user_id
    ).first()

    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="income not found")
    
    return income


def update_income_in_db(db: Session, income_id: int, user_id: int, title: str, amount, description: Optional[str], date: Optional[datetime]):
    """
    Update an income. Verifies income. Raises 404 when missing.
    """
    income = db.query(models.Income).filter(
        models.Income.id == income_id,
        models.Income.user_id == user_id
    ).first()

    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="income not found")

    income.title = title
    income.amount = amount
    income.description = description
    income.date = date or income.date
    db.commit()
    db.refresh(income)

    return income


def delete_income_in_db(db: Session, income_id: int, user_id: int):
    """
    Delete an income owned by the user. Raises 404 when missing.
    """
    income = db.query(models.Income).filter(
        models.Income.id == income_id,
        models.Income.user_id == user_id
    ).first()

    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="income not found")
    
    db.delete(income)
    db.commit()

    return


def get_income_summary_util(db: Session, user_id: int, period: str = "month"):
    """
    Return summary data: total per category and total per period (month/quarter/year).
    """
    if period == "month":
        period_total = (
            db.query(func.strftime("%Y-%m", models.Income.date), func.sum(models.Income.amount))
            .filter(models.Income.user_id == user_id)
            .group_by(func.strftime("%Y-%m", models.Income.date))
            .all()
        )
    elif period == "quarter":
        quarter_label = label(
            "quarter",
            (func.strftime("%Y", models.Income.date) + "-" +
            ((func.strftime("%m", models.Income.date).cast(Integer)-1)/3 + 1).cast(String))
        )

        period_total = (
            db.query(quarter_label, func.sum(models.Income.amount))
            .filter(models.Income.user_id == user_id)
            .group_by(quarter_label)
            .all()
        )
    else:  # year
        period_total = (
            db.query(func.strftime("%Y", models.Income.date), func.sum(models.Income.amount))
            .filter(models.Income.user_id == user_id)
            .group_by(func.strftime("%Y", models.Income.date))
            .all()
        )

    return {
        "total_per_period": [{"period": p, "total": t} for p, t in period_total],
    }