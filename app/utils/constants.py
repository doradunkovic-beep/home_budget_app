import os

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./budget.db")

# Initial balance (1000 by default, if not provided or invalid value)
try:
	INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "1000.00"))
except ValueError:
	INITIAL_BALANCE = 1000.00

# Auth constants 
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
try:
	ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except ValueError:
	ACCESS_TOKEN_EXPIRE_MINUTES = 60


PREDEFINED_CATEGORIES = ["Food", "Car", "Accommodation", "Bills"]