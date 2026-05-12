# Standard API Response Format

A reusable, standardized response format for all API endpoints in the inventory management system.

## Files

- **`response.py`** - Core response models (Pydantic)
- **`common.py`** - Helper functions and error codes
- **`response_examples.py`** - Usage examples for all scenarios

## Quick Start

### Import

```python
from app.schemas import success_response, error_response, ErrorCode
```

### Success Response

```python
@router.get("/users/{user_id}")
def get_user(user_id: int):
    user = {"id": user_id, "name": "John Doe"}
    return success_response(
        message="User retrieved successfully",
        data=user
    )
```

**Response:**
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "id": 1,
    "name": "John Doe"
  }
}
```

### Error Response

```python
@router.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id < 1:
        return error_response(
            code=ErrorCode.NOT_FOUND,
            message="User not found"
        )
    
    return success_response(message="Success", data={...})
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
```

## Available Error Codes

```python
from app.schemas import ErrorCode

ErrorCode.VALIDATION_ERROR      # Invalid input data
ErrorCode.NOT_FOUND             # Resource not found
ErrorCode.UNAUTHORIZED          # Authentication failed
ErrorCode.FORBIDDEN             # Access denied
ErrorCode.CONFLICT              # Resource already exists
ErrorCode.INTERNAL_ERROR        # Server error
ErrorCode.BAD_REQUEST           # Malformed request
ErrorCode.ALREADY_EXISTS        # Duplicate resource
ErrorCode.INVALID_OPERATION     # Operation not allowed
ErrorCode.DATABASE_ERROR        # Database failure
```

## Response Schemas

### SuccessResponse
```python
{
  "success": True,              # Always true
  "message": str,               # Operation message
  "data": Optional[Any]         # Response data
}
```

### ErrorResponse
```python
{
  "success": False,             # Always false
  "error": {
    "code": str,                # Error code identifier
    "message": str              # Readable message
  }
}
```

## Usage Patterns

### 1. List/Paginated Responses

```python
@router.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    items = [...]
    return success_response(
        message=f"Retrieved {len(items)} items",
        data={
            "items": items,
            "total": len(items),
            "skip": skip,
            "limit": limit
        }
    )
```

### 2. Create/POST Responses

```python
@router.post("/users")
def create_user(user_data: UserCreate):
    # Validation
    if User.exists(user_data.email):
        return error_response(
            code=ErrorCode.ALREADY_EXISTS,
            message="Email already registered"
        )
    
    user = User.create(user_data)
    return success_response(
        message="User created successfully",
        data=user
    )
```

### 3. Update/PUT Responses

```python
@router.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate):
    user = User.get(user_id)
    if not user:
        return error_response(
            code=ErrorCode.NOT_FOUND,
            message=f"User {user_id} not found"
        )
    
    user.update(user_data)
    return success_response(
        message="User updated successfully",
        data=user
    )
```

### 4. Delete/DELETE Responses

```python
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    user = User.get(user_id)
    if not user:
        return error_response(
            code=ErrorCode.NOT_FOUND,
            message=f"User {user_id} not found"
        )
    
    user.delete()
    return success_response(
        message="User deleted successfully",
        data=None
    )
```

### 5. Validation Error Responses

```python
@router.post("/items")
def create_item(name: str, price: float):
    errors = []
    
    if not name or len(name) < 3:
        errors.append("Name must be at least 3 characters")
    
    if price <= 0:
        errors.append("Price must be greater than 0")
    
    if errors:
        return error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="; ".join(errors)
        )
    
    item = Item.create(name=name, price=price)
    return success_response(
        message="Item created successfully",
        data=item
    )
```

## Advanced: Using with Generic Responses

```python
from app.schemas import ApiResponse
from typing import List

@router.get("/users", response_model=ApiResponse[List[User]])
def list_users():
    users = User.all()
    return ApiResponse.success_response(
        message="Users retrieved",
        data=users
    )

@router.get("/users/{user_id}", response_model=ApiResponse[User])
def get_user(user_id: int):
    user = User.get(user_id)
    if not user:
        return ApiResponse.error_response(
            code="NOT_FOUND",
            message="User not found"
        )
    return ApiResponse.success_response(
        message="User retrieved",
        data=user
    )
```

## Best Practices

1. **Always use standardized responses** - Consistency across the API
2. **Use appropriate error codes** - Helps clients handle errors properly
3. **Provide meaningful messages** - Make debugging easier for frontend developers
4. **Include data in success** - Whenever applicable, return the created/updated resource
5. **Be specific with errors** - Don't use generic "Internal Error" messages
6. **Include pagination info** - For list endpoints, include `total`, `skip`, `limit`
7. **Document responses** - Use docstrings and examples

## See Also

- [response_examples.py](response_examples.py) - Complete usage examples
- [response.py](response.py) - Core Pydantic models
- [common.py](common.py) - Helper functions and error codes
