# 🚀 Deployment Guide - AI-Powered Car Valuation System

**Last Updated:** June 23, 2026  
**Version:** 1.0  
**Status:** Production Ready

---

## 📋 Prerequisites

### Required Services
- AWS Account (for Bedrock & RDS)
- PostgreSQL Database (AWS RDS recommended)
- Python 3.8+
- Node.js (for frontend, optional)

### Required Credentials
- AWS Access Key & Secret Key (for Bedrock)
- PostgreSQL database credentials

---

## 🔧 Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/srivignesh928/ai-powered-car-cost-estimation.git
cd ai-powered-car-cost-estimation
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Additional dependencies for ETL
pip install requests beautifulsoup4 sqlalchemy psycopg2-binary pydantic python-dotenv
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

**Required Environment Variables:**

```env
# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# PostgreSQL Configuration
POSTGRES_HOST=your_rds_endpoint_here
POSTGRES_PORT=5432
POSTGRES_DB=car_valuation
POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_db_password
```

### 5. Setup Database

The database tables will be created automatically on first run. Ensure your PostgreSQL database is accessible.

**Database Schema:**
- `market_prices` - Scraped car listings
- `market_statistics` - Aggregated market data
- `pipeline_logs` - ETL execution logs
- `market_sources` - Data source tracking
- `prediction_logs` - API prediction logs

### 6. Run ETL Pipeline (Optional - Get Market Data)

```bash
python etl/run_pipeline.py
```

This will scrape car listings from Cars24 and CarDekho for 15 cities.

**Configuration:** Edit `etl/config.py` to customize:
- Cities to scrape
- Pages per city
- Delay between requests

---

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### Open Frontend

Simply open `frontend/index.html` in your browser, or serve it:

```bash
cd frontend
python -m http.server 8080
```

Frontend will be available at: `http://localhost:8080`

---

## 🌐 Production Deployment

### Option 1: AWS EC2 + S3

**Backend (EC2):**
1. Launch EC2 instance (t2.medium or higher)
2. Install Python 3.8+
3. Clone repository
4. Setup virtual environment
5. Install dependencies
6. Configure .env with production credentials
7. Run with gunicorn:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
   ```
8. Setup nginx as reverse proxy
9. Configure SSL with Let's Encrypt

**Frontend (S3 + CloudFront):**
1. Upload frontend files to S3 bucket
2. Enable static website hosting
3. Create CloudFront distribution
4. Configure custom domain (optional)
5. Update API endpoint in `frontend/js/app.js`

### Option 2: Docker Deployment

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Run with Docker:**
```bash
docker build -t car-valuation-backend .
docker run -p 8000:8000 --env-file .env car-valuation-backend
```

### Option 3: AWS ECS/Fargate

1. Create ECR repository
2. Build and push Docker image
3. Create ECS cluster
4. Define task definition
5. Create service with load balancer
6. Configure auto-scaling

---

## 🔒 Security Checklist

- ✅ Never commit `.env` file
- ✅ Use environment variables for all secrets
- ✅ Enable HTTPS in production
- ✅ Restrict database access (security groups)
- ✅ Use IAM roles instead of access keys (when possible)
- ✅ Enable CORS only for trusted domains
- ✅ Implement rate limiting
- ✅ Regular security updates

---

## 📊 Monitoring & Maintenance

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

### Database Monitoring

```bash
python view_database.py
```

### ETL Pipeline Logs

Check `etl/logs/` directory for scraping logs.

### Refresh Market Data

Run ETL pipeline weekly or bi-weekly:

```bash
python etl/run_pipeline.py
```

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test connection
python -c "from database.connection import get_session; print('✅ Connected')"
```

**Common fixes:**
- Check database credentials in `.env`
- Verify database is accessible (security groups)
- Ensure PostgreSQL is running

### Backend Not Starting

```bash
# Check if port 8000 is in use
lsof -i :8000

# Install missing dependencies
pip install -r backend/requirements.txt
```

### ETL Pipeline Errors

**Common issues:**
- Website structure changed (update scrapers)
- Rate limiting (increase delay in config)
- Network issues (check connectivity)

---

## 📈 Performance Optimization

### Enable Redis Caching (Optional)

```bash
pip install redis
```

Update `backend/app/main.py` to cache predictions.

### Database Indexing

Already configured in `database/models.py`:
- Index on `(brand, model, year, city)`
- Index on `last_seen_at`

### Load Balancing

Use AWS ALB or nginx for multiple backend instances.

---

## 🔄 CI/CD Pipeline (Optional)

### GitHub Actions Example

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to EC2
        run: |
          # Your deployment script
```

---

## 📞 Support

**Issues:** https://github.com/srivignesh928/ai-powered-car-cost-estimation/issues

**Documentation:**
- API_DOCUMENTATION.md
- USER_GUIDE.md
- TECHNICAL_DOCUMENTATION.md

---

## 📝 License

[Add your license here]

---

**System Status:** ✅ Production Ready  
**Version:** 1.0  
**Last Updated:** June 23, 2026
