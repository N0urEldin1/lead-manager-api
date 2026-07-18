from fastapi import HTTPException


def error_403():
    status_code = 403
    raise HTTPException(status_code=status_code, detail={
        "status_code": status_code, "error_details": "Forbidden. Access denied"})
