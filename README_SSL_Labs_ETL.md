# SSL Labs ETL Connector — Software Architecture Assignment  

## Overview  
This project is a **custom Python ETL (Extract → Transform → Load) pipeline** built for the [SSL Labs API](https://api.ssllabs.com/api/v3/).  
It performs a live SSL/TLS scan on a domain, enriches the results with additional risk analysis, and stores them in a **MongoDB collection** for further security auditing.  

### API Overview

- **Important Query Parameters:**
| Parameter | Description |
|-----------|-------------|
| `host`    | The domain to scan (required). |
| `publish` | If set to `off`, results are private; `on` makes them public. |
| `all`     | If set to `done`, returns full details when scan is complete. |

- **Behavior:**  
The API is asynchronous — initial requests may return:  
- `status: "DNS"` → resolving DNS  
- `status: "IN_PROGRESS"` → scan running  
- `status: "READY"` → results ready  
- `status: "ERROR"` → scan failed  

- **Rate Limits:**  
~60 requests/hour per IP. Returns `429 Too Many Requests` if exceeded.

- **Response Structure Highlights:**
- `host`: scanned domain  
- `status`: scan status  
- `endpoints[]`: array of endpoint objects  
  - `ipAddress`, `grade`, `details.protocols[]`, `details.cert.notAfter`, `details.suites[]`  
- Used in transformation to derive risk category, expiry days, and security flags.

---
## Features
- **Extraction**:
  - Calls the SSL Labs `analyze` endpoint for a given domain.
  - Handles **asynchronous scans** (polling until `"READY"`).
  - Retries on **network errors** and **rate limits** (`429 Too Many Requests`).
- **Transformation**:
  - Maps SSL Labs grades (`A+`, `B`, etc.) to **risk categories** (`low`, `medium`, `high`, `critical`).
  - Calculates **days until certificate expiry**.
  - Detects **weak ciphers** (e.g., RC4, <128-bit).
  - Flags **OCSP stapling** status and supported TLS protocols.
  - Determines the **worst risk** across all scanned endpoints.
- **Loading**:
  - Inserts enriched data into MongoDB (`ssllabs_raw`).
  - Prevents insertion of **invalid/error scans**.
  - Optional: Logs failed scans into `ssllabs_errors`.

---

## Project Structure
```
/ssl-labs-etl/
├── etl_connector.py    # Main runner with validation logic
├── extract.py          # Extract phase (API polling, retries, rate-limit handling)
├── transform.py        # Transform phase (data enrichment & risk mapping)
├── load.py             # Load phase (MongoDB insertion)
├── .env                # Local environment config (DB credentials)
├── README.md           # Assignment Instructions
├── README_SSL_Labs_ETL.md           # This file
└── requirements.txt    # Python dependencies
```

---

## Setup Instructions

### 1. Clone the Repository

### 2. Create `.env` File
Create a `.env` file in the project root:
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=security_scans
```
> **Note:** No API key is required for SSL Labs.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
---
### 4. Start MongoDB Connection

## Running the Connector
Run the script:
```bash
python etl_connector.py
```
You’ll be prompted for a domain:
```
Enter a domain: www.google.com
```
Example output:
```
[INFO] Scan status: IN_PROGRESS. Polling again in 10s...
[SUCCESS] Ingested SSL Labs data for www.google.com into ssllabs_raw
```

---

## Output Screenshots

### **1. Successful Run**
![alt text](image-1.png)

---

### **2. MongoDB Insert Validation**
![alt text](image-3.png)
![alt text](image-2.png)

---

### **3. Rate Limit Handling**
(uncomment line 13 in extract.py)
![alt text](image-4.png)

---

### **4. Invalid Domain Handling**
![alt text](image-5.png)

---

### **5. Network Error Handling**
(Disconnect internet and run)
![alt text](image-6.png)

## References
- [SSL Labs API Documentation](https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs.md)
- [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/)
- [Requests Library](https://docs.python-requests.org/en/latest/)
