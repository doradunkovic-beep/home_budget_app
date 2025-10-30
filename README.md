# home_budget_app
a simple Home Budget application

## Environment variables

The application reads a few configuration values from environment variables. 

Required variables:

- `SECRET_KEY` - secret used to sign JWT tokens (no default recommended in production).
- `ALGORITHM` - JWT algorithm (default: `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES` - token lifetime in minutes (default: `60`).
- `INITIAL_BALANCE` - initial ledger balance assigned to new users (default: `1000.00`).
- `DATABASE_URL` - SQLAlchemy database URL (default: `sqlite:///./budget.db`).

Example (Windows cmd.exe):

```
set SECRET_KEY=your-very-secret-key
set INITIAL_BALANCE=1000.00
set ACCESS_TOKEN_EXPIRE_MINUTES=60
set DATABASE_URL=sqlite:///./budget.db
```

