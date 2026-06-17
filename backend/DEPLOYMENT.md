# 🚀 Backend Deployment Guide

Complete guide for deploying the RAG backend to production.

## 📋 Pre-Deployment Checklist

- [ ] Google AI API key obtained
- [ ] Pinecone account created and API key obtained
- [ ] Pinecone index created (or will be auto-created)
- [ ] Domain/subdomain configured (if using custom domain)
- [ ] Environment variables prepared

## 🌐 Vercel Deployment (Recommended)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Configure Environment Variables

In Vercel dashboard or via CLI:

```bash
vercel env add GOOGLE_API_KEY
vercel env add PINECONE_API_KEY
vercel env add PINECONE_INDEX_NAME
```

Or add via dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add all required variables

### Step 4: Deploy

```bash
cd backend
vercel --prod
```

### Step 5: Test Deployment

```bash
curl https://your-backend.vercel.app/health
```

## 🐳 Docker Deployment

### Option 1: Docker Compose (Local/VPS)

1. **Create `.env` file**:
```bash
cp env.example .env
# Edit .env with your API keys
```

2. **Build and run**:
```bash
docker-compose up --build -d
```

3. **Check logs**:
```bash
docker-compose logs -f
```

4. **Stop**:
```bash
docker-compose down
```

### Option 2: Docker (Manual)

1. **Build image**:
```bash
docker build -t academic-rag-backend .
```

2. **Run container**:
```bash
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  -e PINECONE_INDEX_NAME=tilak-academic-site \
  --name rag-backend \
  academic-rag-backend
```

3. **Check logs**:
```bash
docker logs -f rag-backend
```

## ☁️ Cloud Platform Deployment

### AWS (EC2 + Docker)

1. **Launch EC2 instance** (t2.medium recommended)
2. **Install Docker**:
```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

3. **Clone and deploy**:
```bash
git clone <your-repo>
cd backend
# Create .env file
docker-compose up -d
```

4. **Configure security group** to allow port 8000

### Google Cloud Run

1. **Build and push image**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/rag-backend
```

2. **Deploy**:
```bash
gcloud run deploy rag-backend \
  --image gcr.io/PROJECT_ID/rag-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=xxx,PINECONE_API_KEY=xxx
```

### Azure Container Instances

1. **Create resource group**:
```bash
az group create --name rag-backend-rg --location eastus
```

2. **Deploy container**:
```bash
az container create \
  --resource-group rag-backend-rg \
  --name rag-backend \
  --image your-registry/rag-backend:latest \
  --dns-name-label rag-backend-unique \
  --ports 8000 \
  --environment-variables \
    GOOGLE_API_KEY=xxx \
    PINECONE_API_KEY=xxx
```

## 🔧 Post-Deployment Configuration

### 1. Update Frontend Configuration

Edit `_config.yml`:
```yaml
chat_api_url: https://your-backend.vercel.app
```

Or update `assets/js/chat.js`:
```javascript
const API_URL = 'https://your-backend.vercel.app';
```

### 2. Upload Initial Documents

```bash
# Upload CV
curl -X POST "https://your-backend.vercel.app/upload" \
  -F "file=@cv.pdf"

# Upload research documents
curl -X POST "https://your-backend.vercel.app/upload" \
  -F "file=@research.pdf"
```

### 3. Test Chat Endpoint

```bash
curl -X POST "https://your-backend.vercel.app/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main research interests?"}'
```

## 🔒 Security Hardening

### 1. Enable CORS Restrictions

Update `config.py`:
```python
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

### 2. Add Rate Limiting

Install slowapi:
```bash
pip install slowapi
```

Add to `app.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, ...):
    ...
```

### 3. Add Authentication (Optional)

For upload endpoint:
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/upload")
async def upload_document(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    ...
):
    # Verify token
    if credentials.credentials != os.getenv("UPLOAD_TOKEN"):
        raise HTTPException(status_code=401)
    ...
```

## 📊 Monitoring & Logging

### 1. Health Monitoring

Set up uptime monitoring:
- UptimeRobot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- StatusCake: https://www.statuscake.com

Monitor endpoint: `https://your-backend.vercel.app/health`

### 2. Application Logs

**Vercel**:
```bash
vercel logs
```

**Docker**:
```bash
docker logs -f rag-backend
```

### 3. Error Tracking

Integrate Sentry:
```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./backend
```

## 🐛 Troubleshooting

### Issue: "Service Unavailable" Error

**Solution**:
1. Check API keys are set correctly
2. Verify Pinecone index exists
3. Check logs for specific errors

### Issue: Slow Response Times

**Solution**:
1. Increase Vercel function memory (vercel.json)
2. Reduce `TOP_K_RESULTS` in config
3. Optimize chunk size

### Issue: CORS Errors

**Solution**:
1. Add your domain to `ALLOWED_ORIGINS`
2. Ensure frontend uses correct API URL
3. Check browser console for specific error

### Issue: File Upload Fails

**Solution**:
1. Check file size < `MAX_FILE_SIZE_MB`
2. Verify file extension is supported
3. Increase Vercel payload limit if needed

## 📈 Scaling Considerations

### For High Traffic:

1. **Use CDN** for static assets
2. **Implement caching** for common queries
3. **Upgrade Pinecone plan** for more queries/second
4. **Use Redis** for conversation history
5. **Load balancing** with multiple instances

### Database Upgrade:

Replace in-memory `documents_db` with:
- PostgreSQL for document metadata
- Redis for conversation history
- S3 for document storage

## 📞 Support

For deployment issues:
- Check logs first
- Review this guide
- Open GitHub issue
- Contact support

---

**Next Steps**: After deployment, test all endpoints and upload your documents!

