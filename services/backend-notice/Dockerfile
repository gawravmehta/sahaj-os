FROM python:3.11

WORKDIR /usr/src/application

COPY requirements.txt ./
RUN pip install --only-binary=all -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3332" ,"--reload", "--timeout-keep-alive", "300"]