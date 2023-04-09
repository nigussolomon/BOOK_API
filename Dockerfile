FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./ /app
RUN pip install --no-cache-dir -r /app/requirements.txt
