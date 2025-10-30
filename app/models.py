from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from .database import Base
from .utils.constants import INITIAL_BALANCE


class User(Base):
    __tablename__ = "users"
    """
    Represents a user account.
    :param id: Primary key, user ID.
    :param username: Username (max 30 chars).
    :param email: User's email address (max 254 chars).
    :param password_hash: Hashed password.
    :param balance: User's account balance.
    """
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True, nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    balance = Column(Numeric(12, 2), default=Decimal(str(INITIAL_BALANCE)))

    # relationships
    categories = relationship("Category", back_populates="owner")
    expenses = relationship("Expense", back_populates="owner")
    incomes = relationship("Income", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    """
    An expense category.
    :param id: Primary key, category ID.
    :param name: Category name (max 100 chars).
    :param description: Optional longer description.
    :param user_id: Foreign key, to reference user's category.
    """
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    owner = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")


class Expense(Base):
    __tablename__ = "expenses"
    """
    Record of expenses.
    :param id: Primary key, expense ID.
    :param title: Short title for the expense (max 150 chars).
    :param amount: Expense amount.
    :param description: Optional description (max 500 chars).
    :param date: Timestamp when the expense occurred; defaults to UTC now.
    :param category_id: Foreign key to Category (category of expense).
    :param user_id: Foreign key to User (owner of the expense).
    """
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(500), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    owner = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")


class Income(Base):
    __tablename__ = "incomes"
    """
    Record of incomes.
    :param id: Primary key, income ID.
    :param title: Short title for the income (max 150 chars).
    :param amount: Income amount.
    :param description: Optional description (max 500 chars).
    :param date: Timestamp when the income occurred; defaults to UTC now.
    :param user_id: Foreign key to User (owner of the income).
    """

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    # relationships
    user = relationship("User", back_populates="incomes")
