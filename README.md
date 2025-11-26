# PathoAi FastAPI Service - Beginner Friendly Guide

## 📁 Project Structure (Easy to Understand)

```
app/
├── main.py                 # Main app file - starts the server
├── core/
│   └── config.py          # Settings from .env file
├── db/
│   └── mongo.py           # MongoDB connection code
├── models/
│   └── usage_limit.py     # Data model (what data looks like)
└── routers/
    └── usage_limit.py     # API endpoints (routes)
```

## 🔧 Setup Instructions

### 1. **Install Python Packages**

All packages are already installed! But if you need to reinstall:

```bash
pip install -r requirements.txt
```

**What each package does:**

- `fastapi` - Web framework to create API
- `uvicorn` - Server to run the app
- `motor` - Talk to MongoDB from Python
- `pydantic` - Validate data
- `python-dotenv` - Read .env file

### 2. **Create `.env` File** ✅ (Already created!)

The `.env` file is already set up with default values:

```properties
# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=pathoai

# App Settings
APP_NAME=PathoAi API
DEBUG=True
```

**Change these values if your MongoDB is different!**

## 🚀 How to Run

### Make sure MongoDB is running first!

Then run:

```bash
uvicorn app.main:app --reload
```

The `--reload` flag means the server restarts automatically when you change code.

## 📚 Open the API

Once the server is running, open your browser:

- **Interactive Docs** (Test API here): `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`

## 📝 API Endpoints

### 1. **Root Endpoint**

```
GET /
```

Shows welcome message and useful links.

### 2. **Health Check**

```
GET /health
```

Returns: `{"status": "healthy"}`

### 3. **Get All Usage Limits** ⭐

```
GET /modelLimit
```

Returns a list of all usage limit records from MongoDB.

Example Response:

```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "date": "2025-11-26",
    "jrUsed": 10,
    "srUsed": 5,
    "jrLimit": 100,
    "srLimit": 50
  }
]
```

## 📖 File Explanations (Simple!)

### `app/main.py` - Main Application File

- Creates the FastAPI app
- Connects to MongoDB when app starts
- Disconnects when app stops
- Registers all routes

### `app/core/config.py` - Settings

- Reads the `.env` file
- Stores MongoDB connection info
- Stores app settings

### `app/db/mongo.py` - Database Connection

- `connect_to_mongo()` - Connects to MongoDB
- `close_mongo_connection()` - Disconnects from MongoDB
- `get_database()` - Returns the database to use

### `app/models/usage_limit.py` - Data Model

- Defines what a "UsageLimit" record looks like
- Has fields: id, date, jrUsed, srUsed, jrLimit, srLimit

### `app/routers/usage_limit.py` - API Routes

- `get_all_usage_limits()` - Gets all records from database
- Returns them as a list of UsageLimit objects

## 🐛 Troubleshooting

### Error: "Cannot connect to MongoDB"

- Make sure MongoDB is running
- Check the `MONGODB_URI` in `.env` file

### Error: "Module not found"

- Run: `pip install -r requirements.txt`

### Error: "Port 8000 already in use"

- Run on different port: `uvicorn app.main:app --reload --port 8001`

## 💡 Key Concepts

- **FastAPI**: Web framework for building APIs
- **MongoDB**: NoSQL database
- **Motor**: Async MongoDB driver for Python
- **Async/Await**: Non-blocking code execution
- **Pydantic**: Data validation library

## ✨ Next Steps

Try to:

1. Add a new endpoint that gets usage limit by date
2. Add a POST endpoint to create new usage limits
3. Add error handling for missing records
