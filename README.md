# Request Dispatcher API

A FastAPI-based request dispatcher that implements round-robin load balancing across 3 workers with request deduplication.

## Features

- **Round-Robin Load Balancing**: Distributes requests evenly across 3 workers
- **Request Deduplication**: Prevents the same request from being processed twice
- **Background Processing**: Uses FastAPI background tasks for async processing
- **Database Storage**: Stores all requests and results using SQLAlchemy
- **Status Tracking**: Track request status (queued, processing, completed, failed)

## Requirements

- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite (default) or other SQL database

## Installation

1. Create a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API server:
```bash
python main.py
# or
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /process-request

Process a new request with round-robin worker assignment.

**Request Body:**
```json
{
  "request_id": "abc123",
  "payload": {
    "some": "data"
  }
}
```

**Response (Success):**
```json
{
  "message": "Request queued for processing",
  "request_id": "abc123",
  "worker_id": 0,
  "status": "queued",
  "created_at": "2024-01-01T12:00:00"
}
```

**Response (Duplicate):**
```json
HTTP 409 Conflict
{
  "detail": {
    "error": "Request already processed or in progress",
    "request_id": "abc123",
    "status": "processing",
    "worker_id": 0,
    "created_at": "2024-01-01T12:00:00"
  }
}
```

## Testing

Run the test script to see round-robin distribution and deduplication in action:

```bash
# Make sure the server is running first
python main.py

# In another terminal, run the tests
python test_dispatcher.py
```

## How It Works

1. **Request Reception**: API receives POST request with `request_id` and `payload`
2. **Deduplication Check**: Checks if `request_id` already exists in database
3. **Worker Assignment**: Uses round-robin algorithm to assign request to next available worker (0 → 1 → 2 → 0...)
4. **Database Storage**: Saves request to database with status "queued"
5. **Background Processing**: Worker processes request asynchronously
6. **Result Storage**: Updates database with processing result and status

## Architecture

```
Request → Deduplication Check → Round-Robin Assignment → Database → Background Processing → Result Storage
```

- **models.py**: SQLAlchemy database models
- **database.py**: Database configuration and connection
- **worker_manager.py**: Round-robin worker assignment and processing logic
- **main.py**: FastAPI application with all endpoints
- **test_dispatcher.py**: Test script to verify functionality