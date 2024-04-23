from fastapi import Response
from .response import ApiResponse
from .requests import *

def make_response(response: Response, status: int = 200, message:str = "", data:dict | list | None = None) -> ApiResponse:
    response.status_code = status
    return ApiResponse(status=status, message=message, data=data)