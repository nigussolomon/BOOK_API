FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./ /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt
