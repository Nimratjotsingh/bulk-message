# Bulk Message Service 🚀

A high-performance, stateless, asynchronous email dispatch microservice built with **FastAPI**, **SQLAlchemy AsyncIO**, and **Neon PostgreSQL**. Designed for secure multi-tenant email dispatching with support for dual-authentication (JWT & custom API Keys) and dynamic SMTP configuration management.

---

## 🌟 Key Features

- **Stateless Direct Email Dispatch (`/email/send`)**: Send plain-text or HTML emails instantly without persisting message logs.
- **Dual Authentication Support**:
  - **JWT Bearer Authentication**: Secure session-based access for web dashboards and direct user integrations.
  - **API Key Authentication (`X-API-Key`)**: Fast, persistent access for background jobs, scripts, and third-party automated clients.
- **Dynamic SMTP Management (`/smtp`)**: Store and encrypt multi-provider SMTP configurations using Fernet cryptography.
- **Secure API Key Management (`/api-keys`)**: Generate, list, and revoke API keys with secure SHA-256 hashing.
- **Smart Protocol Mapping**: Automatic configuration handling for Port 587 (Explicit `STARTTLS`) and Port 465 (Implicit `SSL/TLS`).
- **Async & Scalable**: Fully non-blocking architecture using `SQLAlchemy 2.0 AsyncIO`, `asyncpg`, `aiosmtplib`, and Python 3.12+.

---

## 🏗️ Architecture & Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [Neon PostgreSQL](https://neon.tech/) (Serverless Postgres)
- **ORM & Drivers**: SQLAlchemy 2.0 AsyncIO, `asyncpg`, `greenlet`
- **Security & Crypto**: PyJWT, `cryptography` (Fernet), Passlib/Pwdlib (Bcrypt), SHA-256
- **Email Protocol**: `aiosmtplib` (Asynchronous SMTP client)

---

## 📂 Project Structure

```text
.
├── app/
│   ├── api/                # API Route Handlers
│   │   ├── api_keys.py     # API Key generation and management routes
│   │   ├── auth.py         # Login and authentication routes
│   │   ├── email.py        # Direct email sending endpoint
│   │   └── smtp.py         # User SMTP configurations CRUD
│   ├── dependencies/       # Security & Auth Dependencies (JWT + API Key)
│   ├── models/             # SQLAlchemy ORM Models (User, SMTP, APIKey)
│   ├── schemas/            # Pydantic Schemas (Request/Response Models)
│   ├── services/           # Business logic & Email dispatch engine
│   ├── utils/              # Security helpers, Fernet encryption, hashing
│   ├── database.py         # Async SQLAlchemy engine & session setup
│   └── main.py             # FastAPI App Initialization
├── .env.example            # Environment variables template
├── pyproject.toml          # Project configuration & dependencies
└── README.md
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory based on the example configuration below:

```env
# Database Settings
DATABASE_URL=postgresql+asyncpg://user:password@ep-example-123456.us-east-2.aws.neon.tech/neondb?ssl=require

# Security Keys (Keep these static in production!)
JWT_SECRET_KEY=your_super_secret_jwt_key_here
SMTP_SECRET_KEY=your_32_byte_base64_fernet_encryption_key_here

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ **Critical Security Note**: Always generate a static, 32-byte Url-safe Base64 key for `SMTP_SECRET_KEY` (e.g., via `cryptography.fernet.Fernet.generate_key()`). Regenerating this key dynamically on server restarts will prevent decryption of saved SMTP credentials.

---

## 🚀 Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/bulk-message-service.git
cd bulk-message-service
```

### 2. Set Up Virtual Environment
```bash
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

### 4. Run Database Migrations / Start Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, access the interactive API documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔑 Authentication Guide

The service supports two authentication methods for protected endpoints.

### Method 1: JWT Bearer Token (For Users / Dashboard)
1. **Login**: Send a `POST` request to `/auth/login` to obtain an `access_token`.
2. **Authorize**: Pass the token in the `Authorization` header on subsequent requests:
   ```http
   Authorization: Bearer <your_access_token>
   ```

### Method 2: API Key Header (For Automated Clients / Scripts)
1. **Generate Key**: Send a `POST` request to `/api-keys` (authenticated via JWT) to create an API key (`bk_live_...`).
2. **Authorize**: Pass the API key in the custom `X-API-Key` header:
   ```http
   X-API-Key: bk_live_your_generated_api_key
   ```

---

## ✉️ Sending Emails (`POST /email/send`)

Send an asynchronous email by specifying a recipient, subject, body, and saved `config_id`.

### Example Request (`cURL`):

```bash
curl -X POST "https://your-domain.com/email/send" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config_id": 1,
    "recipient_email": "recipient@example.com",
    "subject": "Welcome to Bulk Message Service!",
    "body": "<h1>Hello!</h1><p>Your email service is active and working.</p>"
  }'
```

### Example Response (`200 OK`):

```json
{
  "status": "success",
  "message": "Email dispatched successfully",
  "recipient": "recipient@example.com",
  "config_id": 1
}
```

---

## 🛠️ Protocol & Port Matrix

| Port | Protocol Strategy | Parameters Used |
| :--- | :--- | :--- |
| **587** | Explicit STARTTLS | `start_tls=True`, `use_tls=False` |
| **465** | Implicit SSL/TLS | `use_tls=True`, `start_tls=False` |
| **25 / 2525** | Standard / Custom SMTP | Configurable based on provider |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.