# 🚀 SmartQueue AI - Quick Start Guide

## Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Application
```bash
# Windows
start.bat

# Or manually:
# Terminal 1 - Backend
cd app
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd "al smart queue frontend"
python -m http.server 3000
```

### Step 3: Open Your Browser
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Connection Test: http://localhost:3000/test-connection.html

## What's Been Integrated

✅ **API Client Library** (`js/api.js`)
- Complete wrapper for all backend endpoints
- Automatic error handling
- WebSocket support for real-time updates

✅ **Healthcare Queue** (`healthcare.html`)
- Connected to `/api/healthcare/token` endpoint
- Real-time queue status
- AI-predicted wait times

✅ **Banking Queue** (`banking.html`)
- Connected to `/api/banking/token` endpoint
- Service-based routing
- Premium customer support

✅ **Token Display** (`token.html`)
- Real-time position updates via WebSocket
- Token download functionality
- Live wait time predictions

✅ **Configuration** (`js/config.js`)
- Centralized API endpoint configuration
- Easy to update for production

## Test the Integration

### Option 1: Use the Test Page
1. Open http://localhost:3000/test-connection.html
2. Click "Run All Tests"
3. Verify all tests pass ✓

### Option 2: Manual Testing
1. Go to http://localhost:3000/healthcare.html
2. Fill out the form
3. Submit to create a token
4. See your token with real-time updates

## File Structure

```
📁 Project Root
├── 📄 start.bat                    # Quick start script
├── 📄 requirements.txt             # Python dependencies
├── 📄 INTEGRATION_GUIDE.md         # Detailed integration docs
├── 📄 QUICK_START.md              # This file
│
├── 📁 app/                         # Backend (FastAPI)
│   ├── 📄 main.py                 # Main application
│   ├── 📁 routers/                # API endpoints
│   ├── 📁 services/               # Business logic
│   └── 📁 database/               # Database setup
│
└── 📁 al smart queue frontend/    # Frontend
    ├── 📄 index.html              # Landing page
    ├── 📄 healthcare.html         # Healthcare queue ✓ API
    ├── 📄 banking.html            # Banking queue
    ├── 📄 token.html              # Token display ✓ API
    ├── 📄 test-connection.html    # API test page
    │
    └── 📁 js/
        ├── 📄 config.js           # API configuration
        ├── 📄 api.js              # API client library
        ├── 📄 healthcare-form.js  # Healthcare logic
        ├── 📄 banking-form.js     # Banking logic
        └── 📄 token-display.js    # Token display logic
```

## API Endpoints Available

### Healthcare
- `POST /api/healthcare/token` - Create token
- `GET /api/healthcare/queue` - Get queue status

### Banking
- `POST /api/banking/token` - Create token
- `GET /api/banking/queue` - Get queue status

### Tokens
- `GET /api/tokens/{id}` - Get token details
- `GET /api/queues/position/{id}` - Get position

### WebSocket
- `WS /ws/{client_id}` - Real-time updates

## Common Issues & Solutions

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Install missing dependencies
pip install -r requirements.txt
```

### Frontend won't load
```bash
# Try a different port
python -m http.server 3001

# Update config.js if needed
```

### CORS errors
- Ensure backend is running first
- Check that `allow_origins=["*"]` is in main.py
- Clear browser cache

### API calls failing
1. Open http://localhost:8000/docs
2. Test endpoints directly in Swagger UI
3. Check browser console for errors
4. Verify API_CONFIG.BASE_URL in config.js

## Next Steps

### To Complete:
1. ✅ Healthcare form - DONE
2. ⏳ Banking form - Add API integration
3. ⏳ Tracking page - Real-time tracking
4. ⏳ Admin dashboard - Queue management
5. ⏳ Authentication - Login/register

### To Enhance:
- Add proper notifications (toast messages)
- Implement user authentication
- Add QR code generation
- SMS/Email notifications
- Deploy to production

## Quick Commands

```bash
# Start backend only
cd app && uvicorn main:app --reload

# Start frontend only
cd "al smart queue frontend" && python -m http.server 3000

# View API documentation
start http://localhost:8000/docs

# Test API connection
start http://localhost:3000/test-connection.html

# Check backend logs
# Look at the terminal where uvicorn is running
```

## Resources

- 📖 Full Integration Guide: `INTEGRATION_GUIDE.md`
- 📚 API Reference: `al smart queue frontend/API_REFERENCE.md`
- 🔧 Backend API Docs: http://localhost:8000/docs
- 🧪 Connection Test: http://localhost:3000/test-connection.html

## Support

If something isn't working:
1. Check both terminals for error messages
2. Open browser DevTools (F12) → Console tab
3. Visit the test page to diagnose issues
4. Check that both servers are running

## Success Checklist

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] Test page shows all tests passing
- [ ] Can create healthcare token
- [ ] Token page shows real-time updates
- [ ] WebSocket connection working

Once all checked, you're ready to go! 🎉
