from sqlalchemy import func
from datetime import datetime
import calendar
from decimal import Decimal

from .. import models


def get_period_range(period: str):
    now = datetime.utcnow()

    if period == "month":
        start = datetime(now.year, now.month, 1)
        _, last_day = calendar.monthrange(now.year, now.month)
        end = datetime(now.year, now.month, last_day, 23, 59, 59)

    elif period == "quarter":
        quarter = (now.month - 1) // 3 + 1
        start_month = 3 * (quarter - 1) + 1
        start = datetime(now.year, start_month, 1)
        end_month = start_month + 2
        _, last_day = calendar.monthrange(now.year, end_month)
        end = datetime(now.year, end_month, last_day, 23, 59, 59)

    elif period == "year":
        start = datetime(now.year, 1, 1)
        end = datetime(now.year, 12, 31, 23, 59, 59)
    else:
        raise ValueError("Invalid period")

    return start, end


def get_income_total(db, user_id: int, start: datetime, end: datetime):
    """Return total income for user between start and end (0 if None)."""
    total = (
        db.query(func.sum(models.Income.amount))
        .filter(models.Income.user_id == user_id)
        .filter(models.Income.date.between(start, end))
        .scalar()
    ) or 0
    return total


def get_expense_total(db, user_id: int, start: datetime, end: datetime):
    """Return total expenses for user between start and end (0 if None)."""
    total = (
        db.query(func.sum(models.Expense.amount))
        .filter(models.Expense.user_id == user_id)
        .filter(models.Expense.date.between(start, end))
        .scalar()
    ) or 0
    return total


def get_expense_by_category(db, user_id: int, start: datetime, end: datetime):
    """Return list of expense totals grouped by category name."""
    rows = (
        db.query(models.Category.name, func.sum(models.Expense.amount))
        .join(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .filter(models.Expense.date.between(start, end))
        .group_by(models.Category.id)
        .all()
    )
    return [{"category": c, "total": total} for c, total in rows]


def get_income_by_title(db, user_id: int, start: datetime, end: datetime):
    """Return list of income totals grouped by title."""
    rows = (
        db.query(models.Income.title, func.sum(models.Income.amount))
        .filter(models.Income.user_id == user_id)
        .filter(models.Income.date.between(start, end))
        .group_by(models.Income.title)
        .all()
    )
    return [{"title": t, "total": total} for t, total in rows]


def compute_balance_at(db, user_id: int, timestamp: datetime):
    """Compute the balance at a given timestamp.
    Balance is calculated as: initial_balance + sum(incomes <= timestamp) - sum(expenses <= timestamp).
    Uses the stored `User.balance` as the initial balance (the configured initial value).
    Returns Decimal(0) if user not found.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    initial_balance = Decimal(user.balance) if user and hasattr(user, "balance") else Decimal("0")

    income_sum = (
        db.query(func.sum(models.Income.amount))
        .filter(models.Income.user_id == user_id)
        .filter(models.Income.date <= timestamp)
        .scalar()
    ) or 0

    expense_sum = (
        db.query(func.sum(models.Expense.amount))
        .filter(models.Expense.user_id == user_id)
        .filter(models.Expense.date <= timestamp)
        .scalar()
    ) or 0

    try:
        income_dec = Decimal(income_sum)
    except Exception:
        income_dec = Decimal(str(income_sum))
    try:
        expense_dec = Decimal(expense_sum)
    except Exception:
        expense_dec = Decimal(str(expense_sum))

    return initial_balance + income_dec - expense_dec


def get_current_balance(db, user_id: int):
    """Return the current balance (up to now)."""
    return compute_balance_at(db, user_id, datetime.utcnow())


def get_financial_summary(db, user_id: int, period: str = "month"):
    start, end = get_period_range(period)

    income_total = get_income_total(db, user_id, start, end)
    expense_total = get_expense_total(db, user_id, start, end)

    income_by_title = get_income_by_title(db, user_id, start, end)
    expense_by_category = get_expense_by_category(db, user_id, start, end)

    net_savings = income_total - expense_total

    balance_start = compute_balance_at(db, user_id, start)
    balance_end = compute_balance_at(db, user_id, end)

    return {
        "period": period,
        "period_start": start,
        "period_end": end,
        "income_total": income_total,
        "expense_total": expense_total,
        "net_savings": net_savings,
        "balance_start": balance_start,
        "balance_end": balance_end,
        "income_by_category": income_by_title,
        "expense_by_category": expense_by_category,
    }
