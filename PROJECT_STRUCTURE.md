# Project Structure Documentation

This document explains the purpose of each file and directory in the project.

## Root Directory Files

### Configuration Files

- **`_config.yml`**: Main Jekyll configuration file
  - Site metadata (title, author, email, etc.)
  - Navigation menu structure
  - Plugin settings
  - Google Analytics ID (optional)
  - Chat API URL

- **`Gemfile`**: Ruby dependencies for Jekyll
  - Jekyll version
  - Jekyll plugins (SEO, feed, sitemap)
  - GitHub Pages gem

- **`.gitignore`**: Files to exclude from Git
  - Build artifacts
  - Vendor directories
  - System files

### Documentation

- **`README.md`**: Main project documentation
  - Complete setup instructions
  - Deployment guides
  - Troubleshooting
  - Customization tips

- **`SETUP_CHECKLIST.md`**: Interactive checklist for setup
  - Step-by-step tasks
  - Testing verification
  - Maintenance reminders

- **`DEPLOYMENT_GUIDE.md`**: Quick deployment reference
  - Streamlined setup steps
  - Common commands
  - Quick fixes

- **`PROJECT_STRUCTURE.md`**: This file
  - File and directory explanations

### Legal

- **`LICENSE`**: MIT License for the project
- **`CNAME`**: Custom domain configuration (optional)

## Jekyll Content Files

### Main Pages (Markdown)

- **`index.md`**: Homepage
  - Profile section with photo
  - About me
  - Recent news
  - Featured publications
  - Action buttons

- **`research.md`**: Research interests page
  - Research overview
  - Current projects
  - Research areas with details
  - Research philosophy
  - Collaboration opportunities

- **`publications.md`**: Publications list
  - Organized by type (journal, conference, preprint)
  - Pulls data from `_data/publications.yml`
  - Download links (PDF, code, BibTeX)
  - Abstracts (collapsible)

- **`teaching.md`**: Teaching experience
  - Teaching philosophy
  - Courses taught (from `_data/teaching.yml`)
  - Guest lectures
  - Student supervision
  - Teaching awards

- **`cv.md`**: Curriculum Vitae page
  - Downloadable CV link
  - HTML version of key sections
  - Education, experience, skills
  - Awards and publications

- **`contact.md`**: Contact information
  - Email and office address
  - Professional profiles (LinkedIn, GitHub, etc.)
  - Contact form (optional)
  - Office hours

- **`chat.md`**: RAG chat interface
  - Chat widget
  - Usage instructions
  - Example questions
  - Privacy notice

- **`blog.md`**: Blog/news index
  - List of all blog posts
  - Tags and categories
  - RSS feed link
  - Archive by year

## Directory Structure

### `_data/`
YAML data files for structured content (easy to update)

- **`publications.yml`**: Publications database
  ```yaml
  - id: unique_id
    type: journal|conference|preprint
    title: "Paper Title"
    authors: "Author list"
    venue: "Journal/Conference"
    year: 2024
    abstract: "..."
    pdf_link: "/assets/publications/paper.pdf"
    bibtex: |
      @article{...}
  ```

- **`teaching.yml`**: Teaching experience database
  ```yaml
  - title: "Course Name"
    institution: "University"
    role: "TA"
    term: "Fall"
    year: 2024
    topics: ["Topic 1", "Topic 2"]
  ```

### `_layouts/`
HTML templates for different page types

- **`default.html`**: Base layout for all pages
  - HTML structure
  - Includes navigation and footer
  - SEO tags
  - Analytics code

- **`post.html`**: Blog post layout
  - Post header (title, date, author)
  - Post content
  - Tags
  - Previous/next navigation

- **`page.html`**: Simple page layout
  - Page header
  - Page content
  - Minimal styling

### `_includes/`
Reusable HTML components

- **`navigation.html`**: Navigation bar
  - Site title/logo
  - Menu items (from `_config.yml`)
  - Mobile hamburger menu
  - Active link highlighting

- **`footer.html`**: Page footer
  - Author bio
  - Social links
  - Quick navigation
  - Copyright notice

### `_posts/`
Blog posts (Markdown files)

Naming convention: `YYYY-MM-DD-title.md`

Front matter:
```yaml
---
layout: post
title: "Post Title"
date: 2024-10-18
tags: [research, conference]
---
```

Example posts included:
- `2024-10-15-new-publication.md`
- `2024-09-20-conference-presentation.md`
- `2024-08-10-teaching-award.md`

### `assets/`
Static files (CSS, JavaScript, images)

#### `assets/css/`
- **`main.css`**: Main stylesheet
  - CSS variables for colors
  - Base styles
  - Component styles (navigation, footer, chat)
  - Responsive design (mobile-first)
  - Print styles
  - Accessibility features

#### `assets/js/`
- **`main.js`**: Main JavaScript
  - Mobile navigation toggle
  - Smooth scrolling
  - External link handling
  - Back-to-top button
  - Analytics tracking

- **`chat.js`**: Chat interface
  - API communication
  - Message display
  - User input handling
  - Error handling
  - Loading states

#### `assets/images/`
- **`profile.jpg`**: Profile photo (add yours!)
  - Recommended: 400x400px square
  - Format: JPG, PNG
  - Max size: 500KB

- **`publications/`**: Publication PDFs (create this folder)
- **`posts/`**: Blog post images (optional)

#### `assets/`
- **`cv.pdf`**: Your CV (add yours!)
  - Max recommended size: 10MB
  - Keep it updated!

## Backend Directory (`backend/`)

### Main Application

- **`app.py`**: FastAPI application
  - API endpoints (`/chat`, `/index`, `/health`)
  - RAG implementation
  - LangChain integration
  - Vector store management
  - Error handling

### Scripts

- **`index_documents.py`**: Document indexing script
  - Loads website content
  - Processes CV PDF
  - Loads markdown files
  - Creates embeddings
  - Builds vector store

### Configuration

- **`requirements.txt`**: Python dependencies
  - FastAPI and Uvicorn
  - LangChain and LangChain Community
  - Sentence Transformers
  - ChromaDB
  - PyPDF
  - HuggingFace Hub

- **`vercel.json`**: Vercel deployment config
  - Build settings
  - Routes
  - Environment variables
  - Function settings

- **`env.example`**: Environment variables template
  - HuggingFace API token
  - Website URL
  - CV path
  - Optional Grok API

- **`.gitignore`**: Backend-specific ignores
  - Python cache
  - Virtual environment
  - Vector store database
  - Environment files

- **`README.md`**: Backend documentation
  - Setup instructions
  - API documentation
  - Deployment guide
  - Troubleshooting

### Generated Files (Not in Git)

- **`chroma_db/`**: Vector store database
  - Generated by `index_documents.py`
  - Contains document embeddings
  - Persists across deployments

- **`.env`**: Environment variables (local only)
  - Contains API keys
  - Never commit this file!

## File Relationships

### Content Flow
```
_data/publications.yml → publications.md → Generated HTML
_data/teaching.yml → teaching.md → Generated HTML
_posts/*.md → blog.md → Generated HTML
```

### Layout Hierarchy
```
default.html
├── navigation.html (included)
├── page content (inserted)
└── footer.html (included)

post.html (extends default.html)
├── post header
├── post content
└── post navigation
```

### Asset Loading
```
_layouts/default.html
├── assets/css/main.css (styles)
├── assets/js/main.js (general functionality)
└── assets/js/chat.js (chat page only)
```

### Backend Flow
```
User Query → chat.js → app.py (/chat endpoint)
                          ├── Vector Store (chroma_db/)
                          ├── LangChain Retrieval
                          └── LLM Generation
                               └── Response → chat.js → User
```

## Build Process

### Jekyll Build
```
Source Files:
- *.md files
- _data/*.yml
- _layouts/*.html
- _includes/*.html
- _posts/*.md
- assets/*

↓ Jekyll Build ↓

Output (_site/):
- HTML files
- CSS files
- JavaScript files
- Images
- RSS feed
- Sitemap
```

### Backend Build
```
Source Files:
- app.py
- requirements.txt
- chroma_db/

↓ Vercel Build ↓

Deployed Function:
- FastAPI application
- Dependencies
- Vector store
```

## Customization Points

### Easy Customization (No coding)
1. `_config.yml` - Site settings and personal info
2. `_data/publications.yml` - Add publications
3. `_data/teaching.yml` - Add teaching experience
4. `*.md` pages - Edit content
5. `_posts/*.md` - Add blog posts
6. `assets/images/profile.jpg` - Your photo
7. `assets/cv.pdf` - Your CV

### Moderate Customization (Basic HTML/CSS)
1. `assets/css/main.css` - Change colors, fonts, layout
2. `_includes/navigation.html` - Modify menu
3. `_includes/footer.html` - Modify footer
4. `_layouts/*.html` - Change page structure

### Advanced Customization (Programming)
1. `assets/js/chat.js` - Modify chat behavior
2. `backend/app.py` - Change RAG implementation
3. Custom Jekyll plugins
4. Additional API endpoints

## File Size Recommendations

- **Images**: < 500KB each (optimize with TinyPNG)
- **CV PDF**: < 10MB
- **Total site**: < 50MB (GitHub Pages limit: 1GB)
- **Backend function**: < 50MB (Vercel limit)

## Performance Considerations

### Fast Loading
- Minified CSS (Jekyll does this)
- Optimized images
- Async JavaScript loading
- Efficient font loading

### SEO
- `jekyll-seo-tag` plugin
- Sitemap.xml generated
- RSS feed for blog
- Proper heading hierarchy

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

## Backup Strategy

### Important Files to Backup
1. `_data/` directory (your data!)
2. `_posts/` directory (your blog posts)
3. `assets/images/` (your photos)
4. `assets/cv.pdf` (your CV)
5. Modified `*.md` pages
6. `_config.yml` (your settings)

### Automated Backups
- Git repository (GitHub) backs up everything
- Clone repository: `git clone <url>` to get a local copy

## Version Control

### What to Commit
- All source files
- Content files
- Configuration files
- Documentation

### What NOT to Commit
- `_site/` (generated files)
- `.env` (secrets)
- `venv/` (Python environment)
- `node_modules/` (if using npm)
- `.DS_Store` (system files)

## Maintenance Files

### Regular Updates Required
- `_data/publications.yml` - Add new publications
- `_data/teaching.yml` - Add new courses
- `_posts/*.md` - Add new blog posts
- `assets/cv.pdf` - Update CV
- `backend/chroma_db/` - Re-index after updates

### Periodic Updates
- `Gemfile` - Update Jekyll and plugins
- `backend/requirements.txt` - Update Python packages
- `README.md` - Update documentation as needed

---

## Quick Reference

### Where to Find Things

| What you want to do | File to edit |
|---|---|
| Change site title/info | `_config.yml` |
| Add publication | `_data/publications.yml` |
| Add teaching experience | `_data/teaching.yml` |
| Write blog post | Create `_posts/YYYY-MM-DD-title.md` |
| Update research interests | `research.md` |
| Update contact info | `contact.md` |
| Change colors | `assets/css/main.css` (CSS variables) |
| Modify navigation | `_config.yml` (navigation section) |
| Add photo | `assets/images/profile.jpg` |
| Update CV | `assets/cv.pdf` |
| Modify chat behavior | `assets/js/chat.js` |
| Change backend logic | `backend/app.py` |

### File Dependencies

```
Main Dependencies:
_config.yml ← (Used by all pages)
_data/*.yml ← publications.md, teaching.md
_layouts/default.html ← (Used by all pages)
assets/css/main.css ← (Used by all pages)
backend/app.py ← assets/js/chat.js
```

---

For questions about specific files, refer to the comments within each file or check the main README.md.

