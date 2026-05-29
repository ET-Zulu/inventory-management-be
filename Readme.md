# 📦 Inventory Management Backend

A robust, production-ready backend system for managing inventory with full transaction tracking, vendor management, stock alerts, and bulk operations. Built to ensure **accuracy, traceability, and atomic consistency** in all inventory movements.

**Tech Stack:** FastAPI • SQLModel • PostgreSQL • Alembic

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Core Features](#-core-features)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Database Migrations](#-database-migrations)
- [Contributing](#-contributing)
- [Code Style](#-code-style)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Overview

This system provides a centralized inventory management platform that:

* ✅ Tracks stock levels in real time
* ✅ Records all inventory movements as immutable transactions
* ✅ Prevents invalid stock states (e.g., negative inventory)
* ✅ Supports vendor and category management
* ✅ Provides low-stock alerts and reorder reporting
* ✅ Supports bulk import/export via CSV
* ✅ Enforces strict role-based access control (RBAC)
* ✅ Standardized API response format across all endpoints

---

## 🧱 Core Features

### 📦 Item Management

* Create, update, retrieve, and soft-delete items
* Unique **SKU enforcement (case-insensitive)**
* Automatic UUID generation
* Track:
  * Quantity on hand
  * Pricing (cost & selling)
  * Category, vendor, and location/bin
* Quantity is **never directly updated** (transaction-only system)

### 🔁 Inventory Transactions

* Every stock change is recorded as a transaction:
  * Inbound (stock-in)
  * Outbound (stock-out)
  * Adjustments
* Immutable ledger (append-only)
* Each transaction includes:
  * item_id & user_id
  * quantity change (+ / -)
  * before & after quantities
  * reason/notes

### 👥 User & Access Management

* Role-based access control (RBAC):
  * **ADMIN** - Full system access
  * **OPERATOR** - Can perform transactions
  * **VIEWER** - Read-only access
* Invite token system for user onboarding
* Secure password hashing

### 🏢 Vendor Management

* Create and manage vendors
* Track vendor contact info and lead times
* Associate items with vendors

### 📂 Category Management

* Organize items into categories
* Track category status (active/inactive)

### 📥 Bulk Import

* Import items via CSV
* Track import status (pending, processing, success, failed)
* Records processed count

---

## 📁 Project Structure

```
inventory_backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   ├── router.py           # API router setup
│   │   └── v1/
│   │       └── endpoints/      # API endpoint files
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── db/
│   │   └── postgran.py         # Database connection
│   ├── model/                  # SQLModel definitions
│   │   ├── enums.py            # Enum types
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── vendor.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   ├── invite_token.py
│   │   └── bulk_import.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── response.py         # Standard response schemas
│   │   ├── common.py           # Common utilities
│   │   └── *_examples.py       # Usage examples
│   ├── services/               # Business logic
│   └── utils/                  # Utilities & helpers
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── Readme.md                   # This file
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.104+ |
| ORM | SQLModel |
| Database | PostgreSQL 15 |
| Migrations | Alembic |
| Async | Uvicorn |
| Validation | Pydantic |
| Testing | Pytest |

---

## 🎯 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip & virtualenv

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inventory_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

---



## 📚 API Documentation

### Automatic Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Standard Response Format

#### Success Response
```json
{
  "success": true,
  "message": "Operation completed",
  "data": {
    "id": "uuid",
    "name": "Example"
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Readable explanation"
  }
}
```

For more details, see [app/schemas/RESPONSE_FORMAT.md](app/schemas/RESPONSE_FORMAT.md)

---

## 🗄 Database Migrations

### Generate New Migration

After modifying models, generate a migration:

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### View Migration Status

```bash
alembic current
alembic history
```

### Reset Database (Development Only)

```powershell
# On Windows
.\reset_db.ps1

# On Unix/Mac
python reset_db.py
```

---

## 🤝 Contributing

We welcome contributions from all team members! Please follow these guidelines to ensure code quality and consistency.

### Getting Started with Contributing

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Test your changes**
   ```bash
   pytest
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new feature description"
   ```

5. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI-related)

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions
- `chore/` - Dependency updates, maintenance

Example: `feature/add-bulk-import`, `fix/inventory-calculation`, `docs/api-endpoints`

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style changes (formatting, missing semicolons, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Build process, dependencies, etc.

Example:
```
feat: add inventory transaction filtering

Allow users to filter transactions by date range and transaction type.
Implements pagination for large result sets.

Closes #42
```

### Pull Request Process

1. Ensure all tests pass: `pytest`
2. Update documentation if needed
3. Request review from team members
4. Address review comments
5. Merge once approved

---

## 📝 Code Style

### Python Style Guide (PEP 8)

We follow PEP 8 with these guidelines:

- Line length: 100 characters (soft limit)
- Use type hints for function arguments and returns
- Use docstrings for modules, classes, and functions
- Use descriptive variable names

### Type Hints

```python
from typing import List, Optional

def get_items(skip: int = 0, limit: int = 10) -> List[Item]:
    """Get items with pagination."""
    pass
```

### Docstrings

```python
def create_transaction(item_id: UUID, quantity: int) -> Transaction:
    """
    Create a new inventory transaction.
    
    Args:
        item_id: The UUID of the item
        quantity: The quantity change
        
    Returns:
        The created transaction
        
    Raises:
        ValueError: If quantity is invalid
    """
    pass
```

### Naming Conventions

- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Private**: `_leading_underscore`
- **Protected**: `__double_leading_underscore` (sparingly)

### Code Organization

```python
# Imports
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# Constants
DEFAULT_PAGE_SIZE = 10

# Classes
class User(SQLModel, table=True):
    """User model."""
    pass

# Functions
def validate_email(email: str) -> bool:
    """Validate email format."""
    pass
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Structure

Tests should be placed in the `tests/` directory, organized by module:

```
tests/
├── test_auth.py
├── test_health.py
├── test_interview.py
└── conftest.py
```

---

## 🔧 Troubleshooting

### Issue: "type already exists" error

**Solution:**
```bash
# Reset migrations and database
.\reset_db.ps1  # Windows
# or
python reset_db.py
```

### Issue: Database connection failed

**Check:**
1. PostgreSQL service is running
2. DATABASE_URL in `.env` is correct
3. Database credentials are valid

```bash
# Test connection with psql
psql -U postgres -h localhost -d inventory_db
```

### Issue: Migrations not applying

```bash
# Check current migration state
alembic current

# Check migration history
alembic history

# Regenerate migrations
alembic revision --autogenerate -m "fix: migration issue"
```

### Issue: Port 8000 already in use

```bash
# Find and kill process using port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in .env
```

---

## 📞 Support & Questions

- For bugs: Create an issue with detailed reproduction steps
- For questions: Use GitHub Discussions or contact team lead
- For security issues: Email maintainers privately

---

## 📄 License

This project is part of group development. All rights reserved.

---

## 👥 Team

This is a group project developed collaboratively. For questions about specific features or contributions, contact the respective team member.

---

## 🔗 Related Documentation

- [API Response Format Guide](app/schemas/RESPONSE_FORMAT.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Alembic Documentation](https://alembic.sqlalchemy.org)

---

Last Updated: May 12, 2026
