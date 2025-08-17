# Technical Architecture Documentation

## **VCT Predictor - System Architecture & Implementation**

This document provides a comprehensive technical overview of the VCT Predictor application, including system design, data flow, and implementation details.

## **Table of Contents**

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Data Flow](#data-flow)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Security Implementation](#security-implementation)
7. [Performance Optimization](#performance-optimization)
8. [Deployment Architecture](#deployment-architecture)

## **System Overview**

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│                    Presentation Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   HTML5     │  │    CSS3     │  │   JavaScript ES6+   │ │
│  │ Templates   │  │   Styling   │  │   Dynamic Logic     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Flask     │  │   Routes    │  │   Business Logic    │ │
│  │ Framework   │  │   Handler   │  │   Services          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Data Access Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ PostgreSQL  │  │   SQLite    │  │   Data Models       │ │
│  │ Production  │  │ Development │  │   & Schemas         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Railway   │  │   Gunicorn  │  │   Background Tasks  │ │
│  │   Platform  │  │   WSGI      │  │   & Scheduling      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Core Components**

1. **Frontend Interface** - Responsive web application
2. **Backend API** - Flask-based RESTful services
3. **Data Processing** - Automated scraping and analysis
4. **Database Layer** - Persistent data storage
5. **Infrastructure** - Cloud deployment and scaling

## **Architecture Patterns**

### **MVC Pattern Implementation**

```
Model (Data Layer)
├── Database Models
├── Data Access Objects
└── Business Logic Services

View (Presentation Layer)
├── HTML Templates
├── CSS Styling
└── JavaScript Components

Controller (Application Layer)
├── Route Handlers
├── Request Processing
└── Response Generation
```

### **Service-Oriented Architecture**

- **Scraper Service** - Data collection and processing
- **Predictor Service** - Match outcome analysis
- **Database Service** - Data persistence and retrieval
- **Health Service** - System monitoring and status

### **Repository Pattern**

```python
class MatchDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.is_postgres = db_path.startswith('postgresql://')
    
    def get_all_teams_with_stats(self):
        # Data access implementation
        pass
    
    def insert_match_data(self, data):
        # Data insertion implementation
        pass
```

## **Data Flow**

### **Data Collection Pipeline**

```
External Sources → Scraper Service → Data Validation → Database Storage
     ↓                    ↓              ↓              ↓
  VLR.gg            BeautifulSoup4   Schema Check   PostgreSQL
Tournament APIs     Cloudscraper     Data Cleaning   SQLite (Dev)
```

### **Prediction Workflow**

```
User Input → Team Selection → Data Retrieval → Algorithm Processing → Result Display
    ↓            ↓              ↓              ↓              ↓
Team IDs    Validation    Team Stats    Win Rate Calc   Prediction UI
```

### **Health Monitoring Flow**

```
System Status → Health Check → Database Query → Status Update → UI Refresh
     ↓            ↓              ↓              ↓              ↓
Background   Scheduled     Health Data    Status Calc    Real-time
  Tasks      Monitoring    Retrieval      & Formatting     Updates
```

## **Database Design**

### **Core Tables**

#### **group_standings**
```sql
CREATE TABLE group_standings (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(50) NOT NULL,
    team VARCHAR(100) NOT NULL,
    record VARCHAR(20) NOT NULL,
    map_diff VARCHAR(20) NOT NULL,
    round_diff VARCHAR(20) NOT NULL,
    delta REAL NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_name, team)
);
```

#### **scraper_health**
```sql
CREATE TABLE scraper_health (
    id SERIAL PRIMARY KEY,
    last_run TIMESTAMP,
    status VARCHAR(50) DEFAULT 'unknown',
    success_count INTEGER DEFAULT 0,
    total_runs INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **data_updates**
```sql
CREATE TABLE data_updates (
    id SERIAL PRIMARY KEY,
    update_date DATE NOT NULL,
    matches_added INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Database Relationships**

```
group_standings (1) ←→ (1) scraper_health
       ↓
data_updates (1) ←→ (N) group_standings
```

### **Indexing Strategy**

```sql
-- Performance optimization indexes
CREATE INDEX idx_group_standings_group ON group_standings(group_name);
CREATE INDEX idx_group_standings_team ON group_standings(team);
CREATE INDEX idx_scraper_health_status ON scraper_health(status);
CREATE INDEX idx_scraper_health_updated ON scraper_health(updated_at);
```

## **API Design**

### **RESTful Endpoint Structure**

```
GET    /                    # Main application interface
POST   /                    # Match prediction submission
GET    /api/health          # System health status
POST   /api/run-scraper     # Manual data update trigger
POST   /api/reset-database  # Database reset (admin)
POST   /api/reset-database-complete  # Complete database reset
```

### **Response Format Standards**

#### **Success Response**
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        "teams_count": 12,
        "last_updated": "2025-08-16T22:00:00Z"
    }
}
```

#### **Error Response**
```json
{
    "success": false,
    "error": "Detailed error message",
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2025-08-16T22:00:00Z"
}
```

### **Health Endpoint Response**
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

## **Security Implementation**

### **Input Validation**

```python
def validate_team_selection(team1_id, team2_id):
    """Validate team selection for prediction"""
    if not team1_id or not team2_id:
        raise ValidationError("Both teams must be selected")
    
    if team1_id == team2_id:
        raise ValidationError("Teams must be different")
    
    return True
```

### **SQL Injection Prevention**

```python
# Parameterized queries prevent SQL injection
cursor.execute("""
    SELECT * FROM group_standings 
    WHERE group_name = %s AND team = %s
""", (group_name, team_name))
```

### **XSS Prevention**

```python
# Content sanitization in templates
{{ team.team|escape }}  # Jinja2 auto-escaping
{{ prediction_result.predicted_winner|safe }}  # Safe content only
```

### **Rate Limiting**

```python
# Basic rate limiting implementation
from functools import wraps
import time

def rate_limit(max_requests=100, window=3600):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Rate limiting logic
            return f(*args, **kwargs)
        return wrapped
    return decorator
```

## **Performance Optimization**

### **Database Optimization**

1. **Connection Pooling**
   ```python
   # Efficient database connection management
   def get_connection(self):
       if not hasattr(self, '_connection_pool'):
           self._connection_pool = []
       # Connection pool logic
   ```

2. **Query Optimization**
   ```python
   # Optimized team retrieval with proper indexing
   def get_all_teams_with_stats(self):
       cursor.execute("""
           SELECT id, group_name, team, record, map_diff, 
                  round_diff, delta, last_updated
           FROM group_standings 
           ORDER BY group_name, delta DESC
       """)
   ```

### **Caching Strategy**

```python
# Simple in-memory caching for frequently accessed data
class CacheManager:
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def get(self, key):
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return data
        return None
```

### **Background Task Processing**

```python
# Non-blocking background tasks
def start_background_scraper(app):
    def run_scraper():
        while True:
            try:
                # Scraper logic
                time.sleep(86400)  # 24 hours
            except Exception as e:
                logger.error(f"Background scraper error: {e}")
    
    thread = threading.Thread(target=run_scraper, daemon=True)
    thread.start()
```

## **Deployment Architecture**

### **Railway Platform Configuration**

```json
{
    "build": {
        "builder": "nixpacks"
    },
    "deploy": {
        "startCommand": "gunicorn wsgi:app",
        "healthcheckPath": "/api/health",
        "healthcheckTimeout": 300,
        "restartPolicyType": "ON_FAILURE"
    }
}
```

### **Environment Configuration**

```python
# Production configuration
class ProductionConfig(BaseConfig):
    FLASK_ENV = 'production'
    DEBUG = False
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

### **WSGI Configuration**

```python
# wsgi.py - Production entry point
from app import create_app

app = create_app('production')

if __name__ == "__main__":
    app.run()
```

### **Process Management**

```bash
# Procfile - Railway process definition
web: gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

## **Monitoring & Observability**

### **Health Check Endpoints**

- **System Health**: `/api/health`
- **Database Status**: Database connection verification
- **Scraper Status**: Last run time and success rate
- **Performance Metrics**: Response times and throughput

### **Logging Strategy**

```python
import logging

# Structured logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started successfully")
```

### **Error Tracking**

```python
# Comprehensive error handling
try:
    result = perform_operation()
except DatabaseError as e:
    logger.error(f"Database operation failed: {e}")
    return jsonify({"error": "Database error"}), 500
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return jsonify({"error": str(e)}), 400
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return jsonify({"error": "Internal server error"}), 500
```

## **Future Enhancements**

### **Planned Improvements**

1. **Machine Learning Integration**
   - TensorFlow/PyTorch models for predictions
   - Historical data training and validation
   - A/B testing for algorithm improvements

2. **Real-time Updates**
   - WebSocket connections for live data
   - Push notifications for match results
   - Live tournament streaming integration

3. **Advanced Analytics**
   - Player performance metrics
   - Team chemistry analysis
   - Tournament bracket predictions

4. **Mobile Application**
   - React Native mobile app
   - Offline data synchronization
   - Push notification system

### **Scalability Considerations**

1. **Microservices Architecture**
   - Separate services for different functionalities
   - API gateway for request routing
   - Service discovery and load balancing

2. **Database Scaling**
   - Read replicas for performance
   - Sharding for large datasets
   - Redis caching layer

3. **CDN Integration**
   - Static asset distribution
   - Geographic load balancing
   - Edge computing capabilities

---


