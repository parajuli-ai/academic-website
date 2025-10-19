# Setup Checklist

Use this checklist to ensure you've completed all setup steps.

## Initial Setup

### Prerequisites
- [ ] Git installed
- [ ] Ruby installed (2.7+)
- [ ] Python installed (3.8+)
- [ ] GitHub account created
- [ ] Vercel account created
- [ ] HuggingFace account created

### Jekyll Website Setup

- [ ] Cloned/downloaded repository
- [ ] Ran `bundle install` successfully
- [ ] Updated `_config.yml` with your information
- [ ] Added profile photo to `assets/images/profile.jpg`
- [ ] Added CV PDF to `assets/cv.pdf`
- [ ] Updated publications in `_data/publications.yml`
- [ ] Updated teaching experience in `_data/teaching.yml`
- [ ] Customized content pages (index.md, research.md, etc.)
- [ ] Added at least one blog post in `_posts/`
- [ ] Tested locally with `bundle exec jekyll serve`
- [ ] Site loads correctly at http://localhost:4000

### GitHub Pages Deployment

- [ ] Created GitHub repository `yourusername.github.io`
- [ ] Pushed code to GitHub
- [ ] Enabled GitHub Pages in repository settings
- [ ] Waited for deployment (2-5 minutes)
- [ ] Verified site is live at https://yourusername.github.io
- [ ] All pages load correctly
- [ ] Navigation works
- [ ] Images display correctly
- [ ] Links work properly

### Backend Setup

- [ ] Created Python virtual environment
- [ ] Installed requirements: `pip install -r requirements.txt`
- [ ] Got HuggingFace API token
- [ ] Created `.env` file from `env.example`
- [ ] Added HuggingFace token to `.env`
- [ ] Updated `WEBSITE_URL` in `.env`
- [ ] Ran `python index_documents.py` successfully
- [ ] Vector store created in `chroma_db/` directory
- [ ] Tested backend locally: `python app.py`
- [ ] Backend responds to health check

### Vercel Deployment

- [ ] Installed Vercel CLI: `npm install -g vercel`
- [ ] Logged into Vercel: `vercel login`
- [ ] Deployed backend: `vercel`
- [ ] Deployed to production: `vercel --prod`
- [ ] Added `HUGGINGFACE_API_TOKEN` in Vercel dashboard
- [ ] Redeployed after adding environment variable
- [ ] Backend accessible at https://your-backend.vercel.app
- [ ] Health endpoint works: `/health`

### Integration

- [ ] Updated `chat_api_url` in Jekyll `_config.yml`
- [ ] Committed and pushed changes to GitHub
- [ ] Waited for GitHub Pages rebuild
- [ ] Tested chat interface at /chat
- [ ] Chat responds to queries
- [ ] Chat retrieves relevant information
- [ ] Error handling works

## Content Population

### Required Content
- [ ] Added real profile photo
- [ ] Uploaded current CV
- [ ] Added at least 3 publications (or marked as coming soon)
- [ ] Added at least 2 teaching experiences (or marked N/A)
- [ ] Updated research interests section
- [ ] Updated contact information
- [ ] Wrote 1-2 blog posts

### Optional Content
- [ ] Added more publications
- [ ] Added conference presentations
- [ ] Added awards and honors
- [ ] Added project descriptions
- [ ] Created multiple blog posts
- [ ] Added images to blog posts

## Testing

### Website Testing
- [ ] All navigation links work
- [ ] All pages load correctly
- [ ] Mobile responsive (test on phone)
- [ ] Images load properly
- [ ] CV downloads correctly
- [ ] External links open in new tabs
- [ ] RSS feed works: /feed.xml
- [ ] Sitemap loads: /sitemap.xml

### Chat Testing
- [ ] Chat interface loads
- [ ] Can type and send messages
- [ ] Bot responds to queries
- [ ] Responses are relevant
- [ ] Error handling works (try invalid inputs)
- [ ] Loading indicators show
- [ ] Mobile responsive

### Cross-Browser Testing
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (if on Mac)
- [ ] Mobile browsers

## Optimization

### Performance
- [ ] Images optimized (< 500KB each)
- [ ] CV file reasonable size (< 10MB)
- [ ] Site loads quickly (< 3 seconds)
- [ ] No console errors

### SEO
- [ ] Page titles are descriptive
- [ ] Meta descriptions added
- [ ] Images have alt text
- [ ] Sitemap submitted to Google Search Console (optional)

### Accessibility
- [ ] Can navigate with keyboard
- [ ] Links have descriptive text
- [ ] Images have alt text
- [ ] Proper heading hierarchy

## Sharing

### Online Presence
- [ ] Added website to LinkedIn profile
- [ ] Added website to GitHub profile
- [ ] Added website to email signature
- [ ] Added website to CV
- [ ] Shared on social media

### Academic Profiles
- [ ] Updated Google Scholar profile
- [ ] Updated ORCID profile
- [ ] Updated ResearchGate (if used)
- [ ] Updated Academia.edu (if used)

## Maintenance

### Regular Updates
- [ ] Set reminder to update CV
- [ ] Set reminder to add new publications
- [ ] Set reminder to write blog posts
- [ ] Set reminder to re-index backend documents

### Monitoring
- [ ] Check site loads correctly (monthly)
- [ ] Check chat works (monthly)
- [ ] Update dependencies (quarterly)
- [ ] Review analytics (if setup)

## Optional Enhancements

### Custom Domain
- [ ] Purchased custom domain
- [ ] Configured DNS settings
- [ ] Added CNAME file
- [ ] Updated GitHub Pages settings
- [ ] HTTPS enabled

### Analytics
- [ ] Created Google Analytics account
- [ ] Added tracking ID to _config.yml
- [ ] Verified tracking works

### Advanced Features
- [ ] Added Google Scholar feed
- [ ] Added publication metrics
- [ ] Enhanced chat with more data sources
- [ ] Added search functionality
- [ ] Integrated with ORCID API

## Troubleshooting Completed

If you encountered issues, mark which you resolved:

- [ ] Jekyll installation issues
- [ ] GitHub Pages deployment issues
- [ ] Python/backend issues
- [ ] Vercel deployment issues
- [ ] Chat integration issues
- [ ] Image loading issues
- [ ] Mobile responsiveness issues

## Notes

Add any notes or customizations you made:

```
[Your notes here]
```

## Final Check

- [ ] Website is live and fully functional
- [ ] Chat assistant works correctly
- [ ] All content is up-to-date
- [ ] Site is professional and polished
- [ ] Ready to share with others

---

**Congratulations! 🎉**

Your academic personal website with RAG chat is complete!

Date completed: _______________

Website URL: _______________

Backend URL: _______________

