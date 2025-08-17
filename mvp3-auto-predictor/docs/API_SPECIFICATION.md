# API Specification

## **VCT Predictor - RESTful API Documentation**

This document provides comprehensive API specifications for the VCT Predictor application, including endpoint details, request/response formats, and usage examples.

---

## 📋 **API Overview**

- **Base URL**: `https://vctpredictorapp-production.up.railway.app`
- **Protocol**: HTTPS
- **Content Type**: `application/json`
- **Authentication**: None (public API)
- **Rate Limiting**: Basic rate limiting implemented

---

## **Core Endpoints**

### **1. Main Application Interface**

#### **GET /** - Main Application Page
Returns the main HTML interface for the VCT Predictor application.

**Request:**
```http
GET /
```

**Response:**
- **Content-Type**: `text/html`
- **Body**: HTML page with team selection and prediction interface

**Example:**
```bash
curl -X GET https://vctpredictorapp-production.up.railway.app/
```

---

### **2. Match Prediction Submission**

#### **POST /** - Submit Match Prediction
Submit a match prediction request with two selected teams.

**Request:**
```http
POST /
Content-Type: application/x-www-form-urlencoded

team1=<team1_id>&team2=<team2_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team1` | string | Yes | ID of the first team |
| `team2` | string | Yes | ID of the second team |

**Response:**
- **Content-Type**: `text/html`
- **Body**: HTML page with prediction result or error message

**Example:**
```bash
curl -X POST https://vctpredictorapp-production.up.railway.app/ \
  -d "team1=1&team2=2"
```

**Validation Rules:**
- Both teams must be selected
- Teams must be different
- Teams must be from the same group
- Teams must exist in the database

---

## **API Endpoints**

### **3. System Health Status**

#### **GET /api/health** - Get System Health
Retrieve the current health status of the scraper and system.

**Request:**
```http
GET /api/health
```

**Response:**
```json
{
    "status": "success",
    "message": "Health data from database",
    "last_run": "2025-08-16T21:30:00Z",
    "success_count": 15,
    "total_runs": 15,
    "success_rate": 100.0
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Current system status (`success`, `error`, `running`, `initializing`) |
| `message` | string | Human-readable status message |
| `last_run` | string | ISO 8601 timestamp of last scraper run |
| `success_count` | integer | Number of successful scraper runs |
| `total_runs` | integer | Total number of scraper runs |
| `success_rate` | float | Success rate percentage |

**Status Values:**
- `success` - Scraper completed successfully
- `error` - Scraper encountered an error
- `running` - Scraper currently executing
- `initializing` - System initializing, no data yet
- `unknown` - Status cannot be determined

**Example:**
```bash
curl -X GET https://vctpredictorapp-production.up.railway.app/api/health
```

---

### **4. Manual Scraper Execution**

#### **POST /api/run-scraper** - Trigger Data Update
Manually trigger the VCT data scraper to fetch updated tournament information.

**Request:**
```http
POST /api/run-scraper
Content-Type: application/json
```

**Response:**
```json
{
    "success": true,
    "message": "Scraper completed successfully",
    "teams_count": 12
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the scraper executed successfully |
| `message` | string | Human-readable result message |
| `teams_count` | integer | Number of teams found and stored |

**Error Response:**
```json
{
    "success": false,
    "error": "Detailed error message"
}
```

**Example:**
```bash
curl -X POST https://vctpredictorapp-production.up.railway.app/api/run-scraper \
  -H "Content-Type: application/json"
```

---

### **5. Database Reset (Admin)**

#### **POST /api/reset-database** - Clear Team Data
Clear all team data from the database while preserving table structure.

**Request:**
```http
POST /api/reset-database
Content-Type: application/json
```

**Response:**
```json
{
    "success": true,
    "message": "Database reset successfully! All team data cleared."
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Failed to reset database: Database connection error"
}
```

**Example:**
```bash
curl -X POST https://vctpredictorapp-production.up.railway.app/api/reset-database \
  -H "Content-Type: application/json"
```

**Warning**: This operation will delete ALL team data and cannot be undone.

---

### **6. Complete Database Reset (Admin)**

#### **POST /api/reset-database-complete** - Complete Database Reset
Completely reset the database by dropping and recreating all tables.

**Request:**
```http
POST /api/reset-database-complete
Content-Type: application/json
```

**Response:**
```json
{
    "success": true,
    "message": "Database completely reset! All tables recreated."
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Failed to completely reset database: Table drop error"
}
```

**Example:**
```bash
curl -X POST https://vctpredictorapp-production.up.railway.app/api/reset-database-complete \
  -H "Content-Type: application/json"
```

**Warning**: This operation will DROP and RECREATE all tables, losing ALL data permanently.

---

## **Data Models**

### **Team Data Structure**

```json
{
    "id": 1,
    "group_name": "Alpha",
    "team": "Sentinels",
    "record": "5-0",
    "map_diff": "10/2",
    "round_diff": "104/78",
    "delta": 26.0,
    "last_updated": "2025-08-16T21:30:00Z"
}
```

**Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique team identifier |
| `group_name` | string | Tournament group (Alpha/Omega) |
| `team` | string | Team name |
| `record` | string | Win-loss record (e.g., "5-0") |
| `map_diff` | string | Map difference (e.g., "10/2") |
| `round_diff` | string | Round difference (e.g., "104/78") |
| `delta` | float | Performance delta score |
| `last_updated` | string | ISO 8601 timestamp of last update |

---

## 🔒 **Error Handling**

### **HTTP Status Codes**

| Status Code | Description |
|-------------|-------------|
| `200` | Success - Request completed successfully |
| `400` | Bad Request - Invalid input parameters |
| `404` | Not Found - Endpoint or resource not found |
| `500` | Internal Server Error - Server-side error |
| `503` | Service Unavailable - Service temporarily unavailable |

### **Error Response Format**

```json
{
    "success": false,
    "error": "Detailed error message",
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2025-08-16T22:00:00Z"
}
```

**Error Codes:**
- `VALIDATION_ERROR` - Input validation failed
- `DATABASE_ERROR` - Database operation failed
- `SCRAPER_ERROR` - Data scraping failed
- `SYSTEM_ERROR` - General system error

---

## **Usage Examples**

### **JavaScript/Fetch API**

#### **Get System Health**
```javascript
fetch('/api/health')
    .then(response => response.json())
    .then(data => {
        console.log('System Status:', data.status);
        console.log('Success Rate:', data.success_rate + '%');
    })
    .catch(error => console.error('Error:', error));
```

#### **Trigger Scraper**
```javascript
fetch('/api/run-scraper', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Scraper completed:', data.message);
        console.log('Teams found:', data.teams_count);
    } else {
        console.error('Scraper failed:', data.error);
    }
})
.catch(error => console.error('Error:', error));
```

#### **Reset Database**
```javascript
if (confirm('Are you sure you want to reset the database?')) {
    fetch('/api/reset-database', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Database reset:', data.message);
            location.reload(); // Refresh page
        } else {
            console.error('Reset failed:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}
```

### **Python/Requests**

#### **Get System Health**
```python
import requests

response = requests.get('https://vctpredictorapp-production.up.railway.app/api/health')
if response.status_code == 200:
    health_data = response.json()
    print(f"Status: {health_data['status']}")
    print(f"Success Rate: {health_data['success_rate']}%")
else:
    print(f"Error: {response.status_code}")
```

#### **Trigger Scraper**
```python
import requests

response = requests.post('https://vctpredictorapp-production.up.railway.app/api/run-scraper')
if response.status_code == 200:
    result = response.json()
    if result['success']:
        print(f"Scraper completed: {result['message']}")
        print(f"Teams found: {result['teams_count']}")
    else:
        print(f"Scraper failed: {result['error']}")
else:
    print(f"Error: {response.status_code}")
```

---

## **Rate Limiting**

### **Current Limits**
- **Health Endpoint**: 100 requests per hour
- **Scraper Endpoint**: 10 requests per hour
- **Reset Endpoints**: 5 requests per hour
- **Main Interface**: No limits

### **Rate Limit Response**
When rate limit is exceeded:
```json
{
    "success": false,
    "error": "Rate limit exceeded. Please try again later.",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "retry_after": 3600
}
```

---

## **Additional Resources**

### **Related Documentation**
- [Technical Architecture](TECHNICAL_ARCHITECTURE.md)
- [Project Portfolio](PROJECT_PORTFOLIO.md)
- [Railway Deployment](RAILWAY_DEPLOYMENT.md)

### **Live Endpoints**
- **Health Status**: [https://vctpredictorapp-production.up.railway.app/api/health](https://vctpredictorapp-production.up.railway.app/api/health)
- **Main Application**: [https://vctpredictorapp-production.up.railway.app/](https://vctpredictorapp-production.up.railway.app/)

---

*This API specification provides comprehensive documentation for all endpoints and usage patterns. For implementation details, refer to the technical architecture documentation.*
