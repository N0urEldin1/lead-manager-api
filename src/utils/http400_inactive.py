from fastapi import HTTPException, status


def error_400_inactive():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Inactive user",
    )
