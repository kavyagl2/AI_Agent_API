from fastapi.responses import JSONResponse

def json_response(content: dict, status_code: int) -> JSONResponse:
    """
    Utility function for standardized JSON responses.
    """
    return JSONResponse(content=content, status_code=status_code)
