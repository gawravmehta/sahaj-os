
# 📊 Data Veda

A lightweight Go-based HTTP API that reads data elements and purposes from CSV files and exposes them over REST endpoints.

---

## 🚀 Features

- Parses `data_elements.csv` and `purposes.csv`
- Exposes JSON APIs for both datasets
- Built using Go standard library (no external dependencies)

---

## 📂 Project Structure

```
data-veda/
├── main.go
├── data_elements.csv
├── purposes.csv
├── go.mod
└── README.md
```

---

## 🛠 Requirements

- Go 1.22+ installed → [Download Go](https://go.dev/dl/)
- Terminal / PowerShell

---

## ▶️ How to Run

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/data-veda.git
cd data-veda
```

### Step 2: Run the Application (no build)

```bash
go run main.go
```

### Step 3: Or Build and Run

```bash
go build -o data-veda
./data-veda      # On Linux/macOS
.\data-veda.exe  # On Windows PowerShell
```

---

## 🌐 API Endpoints

| Method | Endpoint             | Description                       |
|--------|----------------------|-----------------------------------|
| GET    | `/data-elements`     | Returns all data elements         |
| GET    | `/purposes`          | Returns all purposes              |

Test using your browser or `curl`:
```bash
curl http://localhost:8080/data-elements
curl http://localhost:8080/purposes
```

---

## 📋 Example CSV Format

### `data_elements.csv`

```
ID,Name,Description,Category,DataType,IsSensitive,IsRequired
DE-001,User ID,Unique identifier for a user,Personal Data,string,TRUE,TRUE
...
```

### `purposes.csv`

```
ID,Name,Description,LegalBasis,IsNecessary
PUR-001,Website Analytics,Collecting data for website performance analysis,Legitimate Interest,FALSE
...
```

---
