# SmartQueue AI - Frontend API Reference

## Quick Start

### 1. Include Required Scripts
```html
<script src="js/config.js"></script>
<script src="js/api.js"></script>
```

### 2. Use the API Client
```javascript
// The global 'api' object is automatically available
const response = await api.createHealthcareToken(tokenData);
```

## API Client Methods

### Healthcare

#### Create Healthcare Token
```javascript
const tokenData = {
    name: "John Doe",
    phone: "1234567890",
    department: "opd",
    doctor: "dr-sharma",
    priority: "normal",
    age: 35,
    gender: "male",
    reason: "General checkup"
};

const response = await api.createHealthcareToken(tokenData);
// Returns: { token_id, position, estimated_wait_time, ... }
```

#### Get Healthcare Queue Status
```javascript
// All departments
const queues = await api.getHealthcareQueue();

// Specific department
const opdQueue = await api.getHealthcareQueue('opd');
```

### Banking

#### Create Banking Token
```javascript
const tokenData = {
    name: "Jane Smith",
    phone: "9876543210",
    service: "deposit",
    accountType: "savings",
    isPremium: false
};

const response = await api.createBankingToken(tokenData);
// Returns: { token_id, position, estimated_wait_time, ... }
```

#### Get Banking Queue Status
```javascript
// All services
const queues = await api.getBankingQueue();

// Specific service
const depositQueue = await api.getBankingQueue('deposit');
```

### Token Management

#### Get Token Details
```javascript
const token = await api.getToken('H-OPD-123');
// Returns: { id, status, position, estimated_wait, ... }
```

#### Get Token Position
```javascript
const position = await api.getTokenPosition('H-OPD-123');
// Returns: { position, estimated_wait, ahead_count, ... }
```

#### Update Token Status
```javascript
await api.updateTokenStatus('H-OPD-123', 'completed');
// Status: 'waiting', 'called', 'serving', 'completed', 'cancelled'
```

### WebSocket (Real-time Updates)

#### Connect to WebSocket
```javascript
const tokenId = 'H-OPD-123';

api.connectWebSocket(tokenId, (message) => {
    console.log('Received:', message);
    
    if (message.type === 'position_update') {
        updatePosition(message.position);
        updateWaitTime(message.estimated_wait);
    }
    
    if (message.type === 'your_turn') {
        showNotification('Your turn!');
    }
});
```

#### Disconnect WebSocket
```javascript
api.disconnectWebSocket();
```

### Authentication (Optional)

#### Login
```javascript
const response = await api.login('username', 'password');
// Returns: { access_token, token_type }
// Token is automatically stored and used for subsequent requests
```

#### Register
```javascript
const userData = {
    username: "johndoe",
    email: "john@example.com",
    password: "securepass123",
    role: "user"
};

await api.register(userData);
```

### Analytics

#### Get Analytics Data
```javascript
// Last 24 hours
const analytics = await api.getAnalytics('24h');

// Other options: '7d', '30d', '90d'
const weeklyAnalytics = await api.getAnalytics('7d');
```

### Admin APIs

#### Get Admin Dashboard
```javascript
const dashboard = await api.getAdminDashboard();
// Returns: { total_tokens, active_queues, avg_wait_time, ... }
```

#### Get All Queues
```javascript
const queues = await api.getAdminQueues();
```

#### Call Next Token
```javascript
const queueId = 'healthcare-opd-1';
const nextToken = await api.callNextToken(queueId);
// Returns: { token_id, customer_name, ... }
```

## Error Handling

### Try-Catch Pattern
```javascript
try {
    const response = await api.createHealthcareToken(tokenData);
    console.log('Success:', response);
} catch (error) {
    console.error('Error:', error.message);
    alert('Failed to create token: ' + error.message);
}
```

### Common Error Responses
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Configuration

### Change API URL
Edit `js/config.js`:
```javascript
const API_CONFIG = {
    BASE_URL: 'http://your-api-url.com',
    WS_URL: 'ws://your-api-url.com'
};
```

## Data Formats

### Healthcare Token Response
```json
{
    "token_id": "H-OPD-123",
    "position": 5,
    "estimated_wait_time": 15,
    "department": "opd",
    "priority": "normal",
    "status": "waiting",
    "created_at": "2026-02-16T10:30:00"
}
```

### Banking Token Response
```json
{
    "token_id": "B-DEP-045",
    "position": 3,
    "estimated_wait_time": 8,
    "service_type": "deposit",
    "is_premium": false,
    "status": "waiting",
    "created_at": "2026-02-16T10:30:00"
}
```

### Queue Status Response
```json
{
    "queue_id": "healthcare-opd-1",
    "department": "opd",
    "current_token": "H-OPD-120",
    "waiting_count": 12,
    "avg_wait_time": 15,
    "status": "active"
}
```

### WebSocket Message Types
```json
{
    "type": "position_update",
    "token_id": "H-OPD-123",
    "position": 4,
    "estimated_wait": 12
}

{
    "type": "your_turn",
    "token_id": "H-OPD-123",
    "counter": "Counter 3"
}

{
    "type": "queue_update",
    "queue_id": "healthcare-opd-1",
    "waiting_count": 11
}
```

## Best Practices

1. **Always handle errors** - Use try-catch blocks
2. **Show loading states** - Disable buttons during API calls
3. **Validate input** - Check data before sending to API
4. **Use WebSocket for real-time** - Better than polling
5. **Store tokens locally** - Use localStorage for persistence
6. **Disconnect WebSocket** - Clean up when leaving page

## Example: Complete Token Creation Flow

```javascript
document.getElementById('submit-btn').addEventListener('click', async (e) => {
    e.preventDefault();
    
    // 1. Validate input
    const name = document.getElementById('name').value.trim();
    if (!name) {
        alert('Please enter your name');
        return;
    }
    
    // 2. Show loading state
    const btn = e.target;
    btn.disabled = true;
    btn.textContent = 'Creating Token...';
    
    try {
        // 3. Call API
        const response = await api.createHealthcareToken({
            name: name,
            phone: document.getElementById('phone').value,
            department: selectedDepartment,
            doctor: selectedDoctor,
            priority: selectedPriority
        });
        
        // 4. Store token data
        localStorage.setItem('currentToken', JSON.stringify({
            id: response.token_id,
            position: response.position,
            estimatedWait: response.estimated_wait_time,
            timestamp: Date.now()
        }));
        
        // 5. Navigate to token page
        window.location.href = 'token.html';
        
    } catch (error) {
        // 6. Handle errors
        console.error('Error:', error);
        alert('Failed to create token. Please try again.');
        
        // 7. Reset button
        btn.disabled = false;
        btn.textContent = 'Get My Token';
    }
});
```

## Testing

### Test Backend Connection
```javascript
// Check if backend is running
fetch('http://localhost:8000/')
    .then(r => r.json())
    .then(data => console.log('Backend:', data))
    .catch(err => console.error('Backend not running:', err));
```

### Test API Client
```javascript
// Open browser console and run:
api.getHealthcareQueue()
    .then(data => console.log('Queue data:', data))
    .catch(err => console.error('API error:', err));
```
