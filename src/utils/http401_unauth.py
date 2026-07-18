from fastapi import HTTPException, status


def error_401_unauthorized():
    # status_code = 401
    # raise HTTPException(status_code=status_code, detail={
    #     "status_code": status_code, "error_details": "Unauthorized. Incorrect username or password"})

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized. Please login to access this resource",
        headers={"WWW-Authenticate": "Bearer"},
    )
