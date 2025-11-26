FROM python:3.11.10-alpine3.20
WORKDIR /usr/src/application
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3302" ,"--reload", "--timeout-keep-alive", "300"]
