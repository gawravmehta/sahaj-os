FROM python:3.11.10-alpine3.20

WORKDIR /usr/src/application

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev linux-headers

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3301", "--reload", "--timeout-keep-alive", "300"]
