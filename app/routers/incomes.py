from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from typing import Optional, List
from fastapi import Query, status

from .. import models, schemas
from ..database import get_db
from ..utils.auth import get_current_user

from ..utils.income_utils import create_income_in_db, get_incomes_for_user, update_income_in_db, delete_income_in_db, get_income_summary_util


router = APIRouter(prefix="/incomes", tags=["Incomes"])

# Example POST /incomes/
@router.post("/", response_model=schemas.IncomeOut)
def create_income(income: schemas.IncomeCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    """Create a new income for the current user."""
    return create_income_in_db(db, income.title, income.amount, income.description, income.date,current_user.id)


@router.get("/", response_model=List[schemas.IncomeOut])
def get_incomes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None)
):
    """Get incomes for the current user."""
    return get_incomes_for_user(db, current_user.id, start_date, end_date, min_amount, max_amount)

@router.put("/{income_id}", response_model=schemas.IncomeOut)
def update_income(income_id: int, income_data: schemas.IncomeCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    """Update an existing income for the current user."""
    return update_income_in_db(db, income_id, current_user.id, income_data.title, income_data.amount, income_data.description, income_data.date)

@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: int,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    """Delete an existing income for the current user."""
    return delete_income_in_db(db, income_id, current_user.id)

@router.get("/summary")
def get_income_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    period: str = Query("month", enum=["month", "quarter", "year"])
):
    """Get income summary for the current user."""
    return get_income_summary_util(db, current_user.id, period)