from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError
from passlib.context import CryptContext

from settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class Authenticator:
    __pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    __secret_key = settings.SECRET
    __algorithm = settings.ALGORITHM
    __expire_time = settings.EXPIRE_TIME

    @classmethod
    async def get_current_user(cls, token:  Annotated[str, Depends(oauth2_scheme)]):
        credentials_exceptions = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, cls.__secret_key, algorithms=[cls.__algorithm]
            )
            return {
                "user_id": payload["user_id"],
                "city": payload["city"],
            }
        except JWTError:
            raise credentials_exceptions

