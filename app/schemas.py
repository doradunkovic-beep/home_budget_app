from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    """
    Shared fields for user schemas.
    :param username: User's username. Limit to characters set for simplicity and standardisation.
    :param email: User's email address for registration.
    """
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr

class UserCreate(UserBase):
    """
    Input model for creating a user.
    Password is required and constrained to avoid excessively long input.
    """
    password: str = Field(..., min_length=6, max_length=72)


class UserLogin(BaseModel):
    """
    Schema used for user login (authentication).
    Only requires username and password.
    """
    username: str
    password: str = Field(..., min_length=6, max_length=72)

class UserOut(UserBase):
    """
    Model for user data returned by the API.
    Does not include the password field.
    :param id: DB ID of the user.
    :param balance: Current user's balance.
    """
    id: int
    balance: Decimal

    class Config:
        orm_mode = True
        json_encoders = {Decimal: lambda v: str(v)}

# Token schemas
class Token(BaseModel):
    """
    JWT token response returned after successful authentication.
    :param access_token: The JWT.
    :param token_type: Type of the token (e.g. "bearer").
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Data extracted from a token.
    :param username: Username contained in the token or None.
    """
    username: str | None = None

# Category schemas
class CategoryBase(BaseModel):
    """
    Shared fields for category schemas.
    :param name: Category name.
    :param description: Optional category description.
    """
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    """Schema used when creating a new category. Inherits from CategoryBase."""
    pass

class CategoryOut(CategoryBase):
    """
    Category representation returned by the API.
    :param id: Database ID of the category.
    """
    id: int

    class Config:
        orm_mode = True

# Expense schemas
class ExpenseBase(BaseModel):
    """Shared fields for expense schemas.
    :param title: Expense title.
    :param amount: Expense amount.
    :param description: Optional description.
    :param date: When the expense occurred.
    :param category_id: ID of the category for the expense.
    """
    title: str
    amount: Decimal
    description: str | None = None
    date: datetime | None = None
    category_id: int

class ExpenseCreate(ExpenseBase):
    """Schema used when creating a new expense. Inherits from ExpenseBase."""
    pass

class ExpenseOut(ExpenseBase):
    """
    Expense representation returned by the API.
    :param id: Database ID of the expense.
    """
    id: int

    class Config:
        orm_mode = True
        json_encoders = {Decimal: lambda v: str(v)}

# Income schemas
class IncomeBase(BaseModel):
    """Shared fields for income schemas.
    :param title: Income title.
    :param amount: Income amount.
    :param description: Optional description.
    :param date: When the income occurred.
    """
    title: str
    amount: Decimal
    description: str | None = None
    date: datetime | None = None

class IncomeCreate(IncomeBase):
    """Schema used when creating a new income. Inherits from IncomeBase."""
    pass

class IncomeOut(IncomeBase):
    """
    Income representation returned by the API.
    :param id: Database ID of the income.
    """
    id: int

    class Config:
        orm_mode = True
        json_encoders = {Decimal: lambda v: str(v)}
