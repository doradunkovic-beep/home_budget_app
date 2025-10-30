from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from typing import Optional, List
from fastapi import Query, status

from .. import models, schemas
from ..database import get_db
from ..utils.auth import get_current_user

from ..utils.expense_utils import create_expense_in_db, get_expenses_for_user, update_expense_in_db, delete_expense_in_db, get_expense_summary_util


router = APIRouter(prefix="/expenses", tags=["Expenses"])

# Example POST /expenses/
@router.post("/", response_model=schemas.ExpenseOut)
def create_expense(expense: schemas.ExpenseCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    """Create a new expense for the current user."""
    return create_expense_in_db(db, expense.title, expense.amount, expense.description, expense.date, expense.category_id, current_user.id)


@router.get("/", response_model=List[schemas.ExpenseOut])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    category_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None)
):
    """Get an existing expense."""
    return get_expenses_for_user(db, current_user.id, category_id, start_date, end_date, min_amount, max_amount)

@router.put("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(expense_id: int, expense_data: schemas.ExpenseCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    """Update an existing expense."""
    return update_expense_in_db(db, expense_id, current_user.id, expense_data.title, expense_data.amount, expense_data.description, expense_data.date, expense_data.category_id)

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    """Delete an existing expense."""
    return delete_expense_in_db(db, expense_id, current_user.id)

@router.get("/summary")
def get_expense_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    period: str = Query("month", enum=["month", "quarter", "year"])
):
    """Get expenses summary."""
    return get_expense_summary_util(db, current_user.id, period)