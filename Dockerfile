FROM python:3.11-slim
LABEL authors="seemyown"

ENV PYTHONBUFFERED 1

RUN mkdir /app

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]