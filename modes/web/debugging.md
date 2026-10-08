# Debugging & Error Handling
- Comprehensive error boundary components on frontend.
- Centralized error middleware on backend with structured JSON error responses:
  `{"status": "error", "code": "RESOURCE_NOT_FOUND", "message": "...", "details": []}`
- No raw stack traces exposed to client in production mode.
