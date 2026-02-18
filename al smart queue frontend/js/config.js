// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000',
    ENDPOINTS: {
        // Auth
        LOGIN: '/api/auth/login',
        REGISTER: '/api/auth/register',
        
        // Tokens
        CREATE_TOKEN: '/api/tokens',
        GET_TOKEN: '/api/tokens',
        UPDATE_TOKEN: '/api/tokens',
        
        // Healthcare
        HEALTHCARE_TOKEN: '/api/healthcare/token',
        HEALTHCARE_QUEUE: '/api/healthcare/queue',
        
        // Banking
        BANKING_TOKEN: '/api/banking/token',
        BANKING_QUEUE: '/api/banking/queue',
        
        // Queues
        QUEUE_STATUS: '/api/queues/status',
        QUEUE_POSITION: '/api/queues/position',
        
        // Analytics
        ANALYTICS: '/api/analytics',
        
        // Admin
        ADMIN_DASHBOARD: '/api/admin/dashboard',
        ADMIN_QUEUES: '/api/admin/queues'
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}
