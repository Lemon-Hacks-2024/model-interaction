import logging
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, File
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from helpers.cloud_storage import CloudMediaStorageAdapter
from settings import settings
from helpers.control import header_control
from model.recognition import Recognise


logger = logging.getLogger(__name__)


app = FastAPI(
    title="ModelInteraction",
    version="1.0.0",
    debug=settings.mode,
    dependencies=[Depends(header_control)]
)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


class PriceTagRecognised(BaseModel):
    itemName: str
    itemPrice: float
    confidencePercent: float
    category: str


class Model(BaseModel):
    result: PriceTagRecognised
    priceTagHref: str


@app.post(
    "/recognise",
    response_model=Model,
    status_code=status.HTTP_200_OK
)
async def recognize(
        price_tag: bytes = File(...),
        # __user: dict = Depends(Authenticator.get_current_user),
):
    """
    Функция отправки фото для распознавания цены.
    """
    user = "1234565432"  # __user["id"]
    logger.info(f"Запрос от пользователя: {user}")
    file_name = (datetime.now() - datetime.fromtimestamp(0)).total_seconds()
    file_name = (
        f"{int(file_name)}-{user}.png"
    )

    with open(f"temp/{file_name}", "wb") as file:
        file.write(price_tag)

    recogniser = Recognise()

    try:
        result = recogniser.scan_image(
            f"temp/{file_name}",
        )
    except (
            recogniser.RecognisePriceError,
            recogniser.NoSocialError
    ) as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "status": "Failed validate",
                "reason": str(e)
            }
        )

    if not isinstance(result, dict):
        logger.error(f"Пришел тип данных, который не ожидали: "
                     f"{type(result)=} - {result}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        )

    prise_tag_link = CloudMediaStorageAdapter.upload_new_price_tag(
        file=price_tag, file_name=file_name
    )

    result = PriceTagRecognised.model_validate(result)
    response = Model(
        result=result,
        priceTagHref=prise_tag_link,
    )
    return response
