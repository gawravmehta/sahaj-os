FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod ./

RUN go mod download

COPY . .

RUN CGO_ENABLED=0 go build -ldflags="-w -s" -o data-veda .

FROM scratch

EXPOSE 8080

COPY --from=builder /app/data-veda /data-veda

COPY purposes.csv /purposes.csv
COPY data_elements.csv /data_elements.csv

ENTRYPOINT ["/data-veda"]