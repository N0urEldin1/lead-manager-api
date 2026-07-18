from fastapi import HTTPException


def error_404():
    status_code = 404
    raise HTTPException(status_code=status_code, detail={
        "status_code": status_code, "error_details": "Item does not exist"})
