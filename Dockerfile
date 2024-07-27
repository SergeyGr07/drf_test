FROM python:3.10-slim

COPY . /app

WORKDIR /app
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "drf_test.wsgi:application"]
