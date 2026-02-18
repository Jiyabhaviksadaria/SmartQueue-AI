# SmartQueue AI - Frontend & Backend Integration Guide

## Overview
This guide explains how to run your SmartQueue AI application with the frontend connected to the FastAPI backend.

## Prerequisites
- Python 3.8+
- Modern web browser
- Terminal/Command Prompt

## Backend Setup

### 1. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt python-multipart websockets scikit-learn pandas numpy
```

### 2. Start the Backend Server
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`

### 3. Verify Backend is Running
Open your browser and visit:
- API Docs: `http://localhost:8000/docs`
- Root endpoint: `http://localhost:8000/`

You should see the Swagger UI documentation with all available endpoints.

## Frontend Setup

### 1. Serve the Frontend
You have several options:

#### Option A: Python HTTP Server (Recommended)
```bash
cd "al smart queue frontend"
python -m http.server 3000
```

#### Option B: Node.js HTTP Server
```bash
cd "al smart queue frontend"
npx http-server -p 3000
```

#### Option C: VS Code Live Server
- Install "Live Server" extension in VS Code
- Right-click on `index.html` → "Open with Live Server"

The frontend will be available at: `http://localhost:3000`

### 2. Configure API Endpoint (if needed)
If your backend is running on a different port, edit:
```javascript
// al smart queue frontend/js/config.js
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',  // Change this if needed
    WS_URL: 'ws://localhost:8000'
};
```

## Testing the Integration

### 1. Create a Healthcare Token
1. Open `http://localhost:3000/healthcare.html`
2. Select a department (e.g., OPD)
3. Choose a doctor
4. Select priority level
5. Fill in patient details
6. Click "Get My Token"

### 2. Create a Banking Token
1. Open `http://localhost:3000/banking.html`
2. Select a service (e.g., Cash Deposit)
3. Choose account type
4. Fill in customer details
5. Click "Get My Token"

### 3. Track Your Token
1. After creating a token, you'll be redirected to the token page
2. Click "Track My Queue" to see real-time updates
3. The position and wait time will update automatically via WebSocket

## API Endpoints Used

### Healthcare
- `POST /api/healthcare/token` - Create healthcare token
- `GET /api/healthcare/queue` - Get healthcare queue status

### Banking
- `POST /api/banking/token` - Create banking token
- `GET /api/banking/queue` - Get banking queue status

### Tokens
- `GET /api/tokens/{token_id}` - Get token details
- `GET /api/queues/position/{token_id}` - Get queue position

### WebSocket
- `WS /ws/{client_id}` - Real-time updates

## File Structure

```
al smart queue frontend/
├── index.html              # Landing page
├── healthcare.html         # Healthcare queue form (API integrated)
├── banking.html           # Banking queue form
├── token.html             # Token display (API integrated)
├── tracking.html          # Queue tracking
├── admin.html             # Admin dashboard
├── js/
│   ├── config.js          # API configuration
│   ├── api.js             # API client library
│   ├── healthcare-form.js # Healthcare form logic
│   ├── banking-form.js    # Banking form logic
│   ├── token-display.js   # Token display with WebSocket
│   └── main.js            # Shared utilities
└── css/                   # Stylesheets

app/
├── main.py               # FastAPI application
├── models.py             # Database models
├── schemas.py            # Pydantic schemas
├── routers/              # API endpoints
│   ├── healthcare.py
│   ├── banking.py
│   ├── tokens.py
│   └── ...
└── services/             # Business logic
```

## Features Implemented

✅ Healthcare token creation with API
✅ Banking token creation with API
✅ Real-time queue position updates via WebSocket
✅ AI-predicted wait times
✅ Token display and download
✅ CORS enabled for cross-origin requests
✅ Error handling and loading states

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:
1. Ensure the backend is running
2. Check that CORS middleware is enabled in `app/main.py`
3. Verify the frontend is accessing the correct backend URL

### WebSocket Connection Failed
- Check that the backend WebSocket endpoint is running
- Verify the WS_URL in `config.js` matches your backend
- The app will fall back to polling if WebSocket fails

### API Requests Failing
1. Check backend is running: `http://localhost:8000/docs`
2. Open browser DevTools → Network tab to see request details
3. Check console for error messages
4. Verify the API endpoint URLs in `config.js`

### Database Errors
If you see database errors:
```bash
# Delete the database and let it recreate
rm smartqueue.db
# Restart the backend
```

## Next Steps

### To Complete Integration:
1. ✅ Healthcare form - DONE
2. ⏳ Banking form - Update `banking.html` to use API
3. ⏳ Tracking page - Add real-time tracking
4. ⏳ Admin dashboard - Connect to admin APIs
5. ⏳ Authentication - Add login/register functionality

### To Enhance:
- Add proper error notifications (toast messages)
- Implement authentication and user sessions
- Add QR code generation for tokens
- Implement SMS/email notifications
- Add admin controls for queue management
- Deploy to production server

## Running in Production

### Backend
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
Serve the `al smart queue frontend` folder using:
- Nginx
- Apache
- Vercel/Netlify
- Any static file hosting service

Update `config.js` with your production API URL.

## Support
For issues or questions, check:
- Backend API docs: `http://localhost:8000/docs`
- Browser console for frontend errors
- Backend logs for API errors
