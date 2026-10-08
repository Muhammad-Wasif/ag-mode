# Web Security Directives
- **SQL / NoSQL Injection**: Mandatory parameterized queries and ORM escaping.
- **XSS**: Strict output encoding, Content Security Policy (CSP), avoid `dangerouslySetInnerHTML` / `innerHTML`.
- **CSRF**: SameSite cookies, CSRF tokens on state-changing requests.
- **Headers**: Helmet / security headers (`Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`).
- **Secrets**: Never commit `.env` or credentials. Use environment variables.
