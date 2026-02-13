# 📧 Email Deliverability Checker API

A comprehensive email validation API built with FastAPI that checks email deliverability through multiple validation layers.

## 🚀 Features

- ✅ **Syntax Validation** - RFC-compliant email format checking
- 🌐 **MX Records Verification** - Checks if domain can receive emails
- 🚫 **Disposable Email Detection** - Identifies temporary/throwaway emails
- 📬 **SMTP Verification** - Validates actual mailbox existence (optional)
- 📊 **Deliverability Score** - 0-100 score indicating email quality
- ⚡ **Bulk Validation** - Validate up to 100 emails per request
- 🔒 **API Key Authentication** - Secure access via RapidAPI

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL
- **Deployment**: Render
- **Marketplace**: RapidAPI
- **Email Validation**: dnspython, email-validator
- **SMTP**: aiosmtplib (async)

## 📦 Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd email-validator-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

Edit `.env` file:

```env
# Application
APP_NAME="Email Deliverability Checker API"
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/email_validator

# Security
SECRET_KEY=your-super-secret-key

# SMTP
SMTP_FROM_EMAIL=verify@yourdomain.com
```

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Validate Single Email

**POST** `/validate`

```json
{
  "email": "user@example.com",
  "check_smtp": true
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "is_valid": true,
  "syntax_valid": true,
  "domain": "example.com",
  "has_mx_records": true,
  "mx_records": [
    {
      "host": "mail.example.com",
      "priority": 10
    }
  ],
  "is_disposable": false,
  "smtp_check_performed": true,
  "mailbox_exists": true,
  "smtp_response": "250 OK",
  "deliverability_score": 95.0,
  "checked_at": "2024-02-12T10:30:00Z",
  "processing_time_ms": 1234.56
}
```

#### 2. Bulk Validation

**POST** `/validate/bulk`

```json
{
  "emails": [
    "user1@example.com",
    "user2@example.com"
  ],
  "check_smtp": false
}
```

#### 3. Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-02-12T10:30:00Z"
}
```

## 📊 Deliverability Score

The score (0-100) is calculated based on:

| Check | Points |
|-------|--------|
| Valid Syntax | 20 |
| Has MX Records | 30 |
| Not Disposable | 20 |
| Mailbox Exists (SMTP) | 30 |

**Score Interpretation:**
- 90-100: Excellent deliverability
- 70-89: Good deliverability
- 50-69: Fair (some issues)
- 0-49: Poor (high risk)

## 💰 Pricing Plans (RapidAPI)

| Plan | Price | Validations/Month |
|------|-------|-------------------|
| Free | $0 | 100 |
| Basic | $19 | 5,000 |
| Pro | $49 | 50,000 |

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📁 Project Structure

```
email-validator-api/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   └── validator.py       # Email validation logic
│   ├── utils/                 # Utility functions
│   └── main.py               # FastAPI app
├── tests/                     # Test files
├── .env.example              # Environment template
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## 🚀 Deployment to Render

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure the service:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Add environment variables** from `.env`
5. **Deploy!**

## 📝 Development Roadmap

### Phase 1 ✅ (Current)
- [x] FastAPI setup
- [x] Syntax validation
- [x] MX record verification
- [x] Disposable email detection
- [x] Basic scoring system

### Phase 2 🚧 (Next)
- [ ] SMTP verification implementation
- [ ] PostgreSQL database integration
- [ ] Usage tracking & rate limiting
- [ ] API key authentication

### Phase 3 📋 (Future)
- [ ] Advanced SMTP checks (catch-all detection)
- [ ] Role-based email detection (info@, admin@)
- [ ] Email reputation scoring
- [ ] Webhook notifications
- [ ] Dashboard UI (Next.js)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 📧 Support

- **Documentation**: `/docs` (Swagger UI)
- **Issues**: GitHub Issues
- **Email**: support@yourdomain.com

## ⚡ Performance Tips

1. **Disable SMTP checks for bulk operations** - Much faster
2. **Cache MX records** - Coming in Phase 2
3. **Use bulk endpoint** - More efficient than multiple single calls
4. **Monitor rate limits** - Plan accordingly

## 🔒 Security

- All API requests require authentication via RapidAPI
- Rate limiting enforced at marketplace level
- No sensitive data stored
- SMTP connections timeout after 10s

---

Built with ❤️ using FastAPI
