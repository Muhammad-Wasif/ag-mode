# Authentication
- Passwords hashed with bcrypt (work factor >= 12) or Argon2id.
- JWTs: Short-lived access tokens (15m) with refresh token rotation stored in HttpOnly, Secure, SameSite cookies.
- Support OAuth2 / OpenID Connect and MFA (TOTP) where required.
