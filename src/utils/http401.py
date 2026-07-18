from fastapi import HTTPException, status


def error_401():
    # status_code = 401
    # raise HTTPException(status_code=status_code, detail={
    #     "status_code": status_code, "error_details": "Unauthorized. Incorrect username or password"})

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized. Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
