FROM python:3.9-slim

RUN apt-get update
RUN apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-jpn
RUN apt-get clean

ENV PYTHONDONTWRITEBYTECODE 1

RUN python3 -m pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app
ENTRYPOINT watchmedo auto-restart --directory=./ --pattern="*.py" --recursive -- celery -A tasks worker --concurrency=4 --loglevel=info --logfile=logs/celery.log
