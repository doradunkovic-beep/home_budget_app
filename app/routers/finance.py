from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.auth import get_current_user
from ..utils.summary_utils import get_financial_summary

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.get("/summary")
def financial_summary(
    period: str = Query("month", enum=["month", "quarter", "year"]),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get financial summary."""
    return get_financial_summary(db, current_user.id, period)
