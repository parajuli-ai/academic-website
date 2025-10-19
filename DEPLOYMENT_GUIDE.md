# Quick Deployment Guide

A streamlined guide for deploying your academic website and RAG backend.

## Prerequisites

- [ ] Git installed
- [ ] Ruby 2.7+ installed
- [ ] Python 3.8+ installed
- [ ] Node.js installed (for Vercel CLI)

## Part 1: Deploy Website to GitHub Pages (15 minutes)

### Step 1: Customize Your Site (5 minutes)

```bash
# 1. Update _config.yml with your info
nano _config.yml

# 2. Add your profile photo
cp /path/to/your/photo.jpg assets/images/profile.jpg

# 3. Add your CV
cp /path/to/your/cv.pdf assets/cv.pdf
```

### Step 2: Test Locally (2 minutes)

```bash
# Install dependencies
bundle install

# Run local server
bundle exec jekyll serve

# Visit: http://localhost:4000
```

### Step 3: Deploy to GitHub (8 minutes)

```bash
# 1. Create GitHub repo named: yourusername.github.io

# 2. Initialize and push
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/yourusername.github.io.git
git push -u origin main

# 3. Enable GitHub Pages
# Go to: Settings > Pages > Source: main branch > Save

# 4. Wait 2-5 minutes, then visit:
# https://yourusername.github.io
```

## Part 2: Deploy Backend to Vercel (10 minutes)

### Step 1: Get HuggingFace Token (2 minutes)

1. Sign up: https://huggingface.co/join
2. Get token: https://huggingface.co/settings/tokens
3. Copy the token

### Step 2: Setup Backend (3 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env

# Edit .env and add your token
nano .env
# Set: HUGGINGFACE_API_TOKEN=hf_your_token_here
# Set: WEBSITE_URL=https://yourusername.github.io
```

### Step 3: Index Documents (2 minutes)

**Wait until your GitHub Pages site is live first!**

```bash
python index_documents.py
```

### Step 4: Deploy to Vercel (3 minutes)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod

# Add environment variable in Vercel dashboard:
# 1. Go to: https://vercel.com/dashboard
# 2. Select your project
# 3. Settings > Environment Variables
# 4. Add: HUGGINGFACE_API_TOKEN = your_token
# 5. Redeploy: vercel --prod

# Copy the deployment URL (e.g., https://your-backend.vercel.app)
```

## Part 3: Connect Everything (5 minutes)

### Update Jekyll Config

```bash
# Go back to main directory
cd ..

# Update _config.yml
nano _config.yml

# Change this line:
chat_api_url: "https://your-backend.vercel.app"

# Commit and push
git add _config.yml
git commit -m "Update chat API URL"
git push
```

### Wait and Test

1. Wait 2-5 minutes for GitHub Pages to rebuild
2. Visit: https://yourusername.github.io/chat
3. Test the chat interface

## Quick Test Commands

### Test Jekyll Locally
```bash
bundle exec jekyll serve
# Visit: http://localhost:4000
```

### Test Backend Locally
```bash
cd backend
source venv/bin/activate
python app.py
# Visit: http://localhost:8000/health
```

### Test Backend on Vercel
```bash
curl https://your-backend.vercel.app/health
```

### Test Chat API
```bash
curl -X POST https://your-backend.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main research interests?"}'
```

## Common Issues & Quick Fixes

### Issue: Jekyll won't install
```bash
# Try user install
gem install bundler --user-install
bundle install --path vendor/bundle
```

### Issue: Python dependencies fail
```bash
# Upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Vercel deployment fails
```bash
# Make sure you're in the backend directory
cd backend
vercel --prod
```

### Issue: Chat not working
```bash
# Check backend URL in _config.yml
# Check browser console for errors
# Test backend health endpoint
curl https://your-backend.vercel.app/health
```

### Issue: Documents not indexing
```bash
# Make sure website is live first
# Check WEBSITE_URL in .env
# Run indexing with verbose output
python index_documents.py
```

## Update Workflow

When you update content:

```bash
# 1. Update content files
nano publications.md  # or any file

# 2. Test locally
bundle exec jekyll serve

# 3. Commit and push
git add .
git commit -m "Update content"
git push

# 4. Re-index for chat (if needed)
cd backend
source venv/bin/activate
python index_documents.py
vercel --prod
```

## Maintenance Schedule

### Weekly
- Check that website loads correctly
- Test chat functionality

### Monthly
- Add new blog posts
- Update publications
- Update CV

### Quarterly
- Update dependencies: `bundle update`
- Update Python packages: `pip install --upgrade -r requirements.txt`
- Review and optimize content

## Support Resources

- **Jekyll Issues**: https://jekyllrb.com/docs/
- **GitHub Pages**: https://docs.github.com/en/pages
- **Vercel**: https://vercel.com/docs
- **LangChain**: https://docs.langchain.com/
- **HuggingFace**: https://huggingface.co/docs

## Success Checklist

- [ ] Website live on GitHub Pages
- [ ] Backend deployed on Vercel
- [ ] Chat interface working
- [ ] All pages accessible
- [ ] Mobile responsive
- [ ] Profile photo showing
- [ ] CV downloadable
- [ ] Publications listed
- [ ] Blog posts showing

---

**Total Time: ~30 minutes**

Need help? Check README.md for detailed instructions.

