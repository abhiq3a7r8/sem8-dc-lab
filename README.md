# Distributed Computing Lab – Semester 8

This repository contains **gRPC-based Distributed Computing experiments** implemented in Python as part of the **SEM-8 DC Lab**.

The experiments demonstrate:

* Unary RPC
* Server Streaming RPC
* Client Streaming RPC
* Bidirectional Streaming RPC
* Insecure and Secure (TLS) gRPC channels

---

## 📁 Project Structure

```
SEM8-DC-LAB/
│
├── exp1-unary-rpc/
│   ├── greeter_server.py
│   ├── greeter_client.py
│   └── hello.proto
│
├── exp2-grpc-insecure-channel/
│   ├── telemedicine_server.py
│   ├── telemedicine_client.py
│   └── telemedicine.proto
│
├── exp2-grpc-secure-channel/
│   ├── certs/
│   │   ├── ca.crt
│   │   ├── server.crt
│   │   └── (private keys ignored via .gitignore)
│   ├── telemedicine_server_secure.py
│   ├── telemedicine_client_secure.py
│   └── telemedicine.proto
│
├── .gitignore
└── README.md
```

---

## 🧪 Experiment 1: Unary RPC

**Objective:**

* Understand basic gRPC communication using Unary RPC

**Description:**

* A simple Greeter service
* Client sends a request
* Server responds with a greeting

**RPC Type Used:**

* Unary RPC

---

## 🧪 Experiment 2: Telemedicine System (gRPC)

A simulated **Doctor–Patient Telemedicine System** demonstrating all four gRPC communication models.

### 🩺 RPC Mapping

| RPC Type         | Use Case                                    |
| ---------------- | ------------------------------------------- |
| Unary            | Get medical prescription                    |
| Server Streaming | Doctor instructions as logs                 |
| Client Streaming | Patient vitals (Heart rate, SpO2, BP, etc.) |
| Bidirectional    | Live consultation chat                      |

---

## 🔓 Insecure Channel (HTTP/2)

* Uses `grpc.insecure_channel()`
* No encryption
* Suitable for trusted internal networks

**Files:**

* `telemedicine_server.py`
* `telemedicine_client.py`

---

## 🔐 Secure Channel (TLS)

* Uses `grpc.secure_channel()`
* TLS encryption with CA-signed certificates
* Protects patient medical data

**Files:**

* `telemedicine_server_secure.py`
* `telemedicine_client_secure.py`

### Certificate Usage

* `ca.crt` → Certificate Authority (public)
* `server.crt` → Server certificate
* Private keys are intentionally ignored using `.gitignore`

---

## ▶️ How to Run

### 1️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install grpcio grpcio-tools
```

### 2️⃣ Run Insecure Server & Client

```bash
python telemedicine_server.py
python telemedicine_client.py
```

### 3️⃣ Run Secure Server & Client

```bash
python telemedicine_server_secure.py
python telemedicine_client_secure.py
```

---

## 📜 .gitignore Policy

The following are ignored:

* Virtual environment (`venv/`)
* Python cache files (`__pycache__/`)
* gRPC generated files (`*_pb2.py`)
* TLS private keys (`*.key`, `*.csr`, `*.srl`)

Public certificates (`.crt`) are kept for demo purposes.

---

## How to Run

### Fresh Clone on Lab PC (IMPORTANT)

Follow these steps when you clone this repository on a lab computer.

#### 1. Clone the repository

```bash
git clone <your-repository-url>
cd sem8-dc-lab
```

#### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / macOS
# OR
venv\Scripts\activate      # Windows
```

#### 3. Install required libraries

```bash
pip install --upgrade pip
pip install grpcio grpcio-tools
```

#### 4. Generate gRPC Python files (if needed)

If `.pb2.py` files are missing or regenerated:

```bash
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  telemedicine.proto
```

---

### Running Experiment 1 (Unary RPC – Insecure)

```bash
cd exp1-unary-rpc
python greeter_server.py
# open another terminal
python greeter_client.py
```

---

### Running Experiment 2 (All RPC Types – Insecure)

```bash
cd exp2-grpc_insecure_channel
python telemedicine_server.py
# open another terminal
python telemedicine_client.py
```

---

### Running Experiment 2 (All RPC Types – Secure TLS)

```bash
cd exp2-grpc_secure_channel
python telemedicine_server_secure.py
# open another terminal
python telemedicine_client_secure.py
```

> ⚠️ Ensure `certs/` directory is present before running secure server.

---

## Creating TLS Certificates (For Secure gRPC)

If you clone this repository on a lab PC and the `certs/` folder is missing, follow these steps to generate certificates locally.

> These commands use **OpenSSL** (pre-installed on most Linux lab machines).

### Step 1: Create certs directory

```bash
mkdir certs
cd certs
```

### Step 2: Generate CA private key

```bash
openssl genrsa -out ca.key 4096
```

### Step 3: Generate CA certificate

```bash
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 \
  -out ca.crt \
  -subj "/CN=Telemedicine-CA"
```

### Step 4: Generate Server private key

```bash
openssl genrsa -out server.key 4096
```

### Step 5: Create Server CSR

```bash
openssl req -new -key server.key \
  -out server.csr \
  -subj "/CN=localhost"
```

### Step 6: Sign Server Certificate using CA

```bash
openssl x509 -req -in server.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt -days 365 -sha256
```

### Step 7: Go back to project root

```bash
cd ..
```

### Certificate Usage Summary

| File         | Used By              |
| ------------ | -------------------- |
| `ca.crt`     | Client (trust store) |
| `server.crt` | Server (public cert) |
| `server.key` | Server (private key) |

