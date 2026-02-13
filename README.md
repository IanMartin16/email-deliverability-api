# 📧 Email Deliverability Checker API

A comprehensive FastAPI-based email validation service with deliverability scoring, designed for deployment on Render and distribution via RapidAPI.

## 🚀 Features

### Core Validations
- ✅ **Syntax Validation** - RFC-compliant email format checking
- ✅ **MX Record Verification** - Checks if domain can receive emails
- ✅ **Disposable Email Detection** - Identifies temporary/throwaway emails
- ✅ **SMTP Verification** - Verifies if mailbox actually exists (optional)
- 📊 **Deliverability Score** - 0-100 score with risk assessment

### Additional Features
- 🔄 Batch validation (up to 100 emails)
- 📈 Validation statistics
- 🔐 RapidAPI integration ready
- 💾 PostgreSQL database logging
- 🐳 Docker containerized
- 📚 Auto-generated API documentation

## 💰 Pricing Tiers (RapidAPI)

| Tier | Price | Validations/Month |
|------|-------|-------------------|
| Free | $0 | 100 |
| Basic | $19 | 5,000 |
| Pro | $49 | 50,000 |

## 🏗️ Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL
- **Hosting**: Render
- **Marketplace**: RapidAPI
- **Frontend** (future): Next.js

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker (optional)
- Git

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd email-deliverability-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/email_deliverability
RAPIDAPI_PROXY_SECRET=your-secret-here
SMTP_CHECK_ENABLED=true
```

### 5. Setup Database

```bash
# Create PostgreSQL database
createdb email_deliverability

# Tables will be auto-created on first run
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

Visit:
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t email-deliverability-api .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/db \
  email-deliverability-api
```

### Using Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/email_deliverability
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=email_deliverability
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run: `docker-compose up -d`

## ☁️ Render Deployment

### Method 1: Using Blueprint (Recommended)

1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml` and deploy

### Method 2: Manual Setup

1. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - New → PostgreSQL
   - Note the Internal Database URL

2. **Create Web Service**
   - New → Web Service
   - Connect your GitHub repo
   - Environment: Docker
   - Add environment variables:
     ```
     DATABASE_URL=<from-postgres-database>
     RAPIDAPI_PROXY_SECRET=your-secret
     ```

3. **Deploy**
   - Render will build and deploy automatically

## 📡 API Endpoints

### Single Email Validation

```bash
POST /api/v1/email/validate
```

**Request:**
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
  "has_mx_records": true,
  "is_disposable": false,
  "smtp_verified": true,
  "deliverability_score": 95.0,
  "score_category": "Excellent",
  "risk_level": "Low",
  "domain": "example.com",
  "mx_records": ["mail.example.com"],
  "recommendations": ["Email appears highly deliverable."]
}
```

### Batch Validation

```bash
POST /api/v1/email/validate/batch
```

**Request:**
```json
{
  "emails": ["user1@example.com", "user2@example.com"],
  "check_smtp": false
}
```

### Statistics

```bash
GET /api/v1/email/stats
```

**Response:**
```json
{
  "total_validations": 1234,
  "valid_emails": 980,
  "disposable_emails": 45,
  "average_score": 78.5
}
```

## 🎯 Deliverability Scoring

| Score | Category | Risk Level | Meaning |
|-------|----------|------------|---------|
| 90-100 | Excellent | Low | Highly deliverable |
| 70-89 | Good | Medium | Should deliver |
| 50-69 | Fair | High | May have issues |
| 1-49 | Poor | Very High | Likely to bounce |
| 0 | Invalid | Very High | Will not deliver |

### Score Breakdown
- Valid syntax: **20 points**
- Has MX records: **30 points**
- Not disposable: **25 points**
- SMTP verified: **25 points**

## 🔑 RapidAPI Integration

### Headers Required

```
X-RapidAPI-User: <user-id>
X-RapidAPI-Subscription: <tier-name>
```

### Rate Limiting

Rate limits are enforced by RapidAPI based on subscription tier:
- Free: 100/month
- Basic: 5,000/month
- Pro: 50,000/month

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_validators.py
```

## 📊 Database Schema

```sql
CREATE TABLE email_validations (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL,
    is_valid_syntax BOOLEAN DEFAULT FALSE,
    has_mx_records BOOLEAN DEFAULT FALSE,
    is_disposable BOOLEAN DEFAULT FALSE,
    smtp_valid BOOLEAN,
    deliverability_score FLOAT NOT NULL,
    domain VARCHAR,
    mx_records VARCHAR,
    api_user VARCHAR,
    subscription_tier VARCHAR DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 Security Considerations

1. **SMTP Verification**: Disabled by default in batch mode (can be abused)
2. **Rate Limiting**: Implement at RapidAPI level
3. **Input Validation**: All inputs validated with Pydantic
4. **Database**: Uses parameterized queries (SQLAlchemy ORM)
5. **CORS**: Configurable via environment variables

## 🚧 Roadmap

- [ ] Email reputation scoring (blacklist checking)
- [ ] Catch-all detection
- [ ] Role-based email detection (admin@, info@, etc.)
- [ ] Email enrichment (name, company info)
- [ ] Webhooks for async validation
- [ ] Next.js frontend dashboard
- [ ] Export validation reports (CSV, PDF)
- [ ] GraphQL API
- [ ] Real-time validation via WebSocket

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📧 Support

For issues or questions:
- Create an issue on GitHub
- Contact via RapidAPI support (once published)

## 🎉 Acknowledgments

- FastAPI for the amazing framework
- RapidAPI for marketplace platform
- Render for simple deployment

---

**Built with ❤️ using FastAPI and PostgreSQL**
