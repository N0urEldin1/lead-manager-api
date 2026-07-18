from fastapi import HTTPException, status


def error_400():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists",
    )
