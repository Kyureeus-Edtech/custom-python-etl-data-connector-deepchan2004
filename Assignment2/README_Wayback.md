# Wayback Machine ETL Connector — Software Architecture Assignment  

## Overview  
This project is a **custom Python ETL (Extract → Transform → Load)** pipeline built for the [Internet Archive Wayback Machine API](https://archive.org/help/wayback_api.php).  
It retrieves website archival snapshots, analyzes their historical coverage, detects content types (HTML, images, etc.), and stores normalized results in **MongoDB** for further analysis and auditing.  

---

## API Overview  

The **Wayback Machine** provides three public API endpoints for accessing website snapshot history.  
This ETL integrates **vall the three key endpoints**:  

| Endpoint | Purpose |
|-----------|----------|
| `/wayback/available` | Fetches the most recent available snapshot for a given URL. |
| `/cdx/search/cdx` | Returns a full list of archived snapshots (timestamp, MIME type, status code, etc.). |
| `/save/<url>` | Creates a new snapshot (optional, only if no archive exists). |

---

### Endpoint Behavior

- **/wayback/available**  
  - Input: `url=https://example.com`  
  - Output: Latest archived snapshot metadata  
  - Used for: Checking if the target page exists in the archive.

- **/cdx/search/cdx**  
  - Input: `url=https://example.com&output=json`  
  - Output: List of historical snapshots with timestamps, MIME type, etc.  
  - Used for: Analyzing content evolution and image availability.

- **/save/<url>**  
  - Input: Full page URL  
  - Output: Redirect to created archive snapshot  
  - Used for: Creating new archive entries if missing. 

---

### Rate Limits  
While the Wayback Machine API doesn’t have strict published rate limits, it may throttle or return `429 Too Many Requests` if abused.  
Your ETL implements **exponential backoff** and safe retry logic.  

| Status Code | Meaning | Handling |
|--------------|----------|-----------|
| `200` | Success | Process response |
| `429` | Rate-limited | Wait and retry |
| `523` | Origin unreachable | Skip |
| `403/404` | Forbidden / Not found | Skip |
| `5xx` | Server-side error | Retry |

---

## Features  

### **Extraction**
- Connects to `/available`, `/cdx`, and optionally `/save` endpoints.  
- Handles **timeouts**, **network errors**, and **rate limits** gracefully.  
- Supports **automatic retry with exponential backoff**.  

### **Transformation**
- Converts raw JSON and CDX history into structured MongoDB-ready documents.  
- Extracts:
  - `latest_snapshot_url`
  - `latest_snapshot_timestamp`
  - Total and image-only snapshot counts
  - MIME type diversity (HTML, image/png, etc.)
- Converts timestamps (`20240512104500`) → ISO datetime.
- Adds audit fields: `source`, `fetched_at`, `last_updated`.

### **Loading**
- Inserts or updates documents in MongoDB collection (`wayback_raw`).  
- Prevents duplicates using upsert (`url` as unique key).  
- Adds `created_at` / `last_updated` timestamps automatically.  
- Handles connection pooling safely via environment configuration.

---

## Project Structure

/wayback-etl/
├── extract.py # Handles API calls, retries, rate limits, network errors
├── transform.py # Normalizes and enriches JSON response
├── load.py # Upserts structured data into MongoDB
├── etl_connector.py # Main driver script (validation + ETL orchestration)
├── .env # MongoDB connection details
├── README.md # This file
└── requirements.txt # Dependencies


---

## Setup Instructions  

### 1. Clone Repository  

### 2. Create `.env` file 

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=archive_insights
```
### 3. pip install the dependencies
pip install -r requirements.txt

### 4. Start MongoDB Connection

## Running the Connector
Run the script:
```bash
python3 etl_connector.py
```
You’ll be prompted for a URL:
```
Enter a domain: https://youtube.com
```
### 5. Output Screenshots

The output screenshots have been added in the project folder.

## References
- [SSL Labs API Documentation](https://archive.org/help/wayback_api.php)
- [CDX API Documentation](https://github.com/internetarchive/wayback/wayback-cdx-server)
- [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/)
- [Requests Library](https://docs.python-requests.org/en/latest/)