from fastapi import FastAPI

from .database import Base, engine
from .routers import users, categories, expenses, incomes, finance

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Home Budget API", version="1.0")

app.include_router(users.router)
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(incomes.router)
app.include_router(finance.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Home Budget API!"}
