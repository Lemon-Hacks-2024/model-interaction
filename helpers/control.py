from fastapi import Request, HTTPException, status
from settings import settings


async def header_control(request: Request):
    if settings.mode:
        return
    ac_token = request.headers.get("x-access-token", None)
    if ac_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"Missing x-access-token"},
        )
    if ac_token != settings.ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"Invalid x-access-token"},
        )

