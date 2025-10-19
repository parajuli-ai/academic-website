# Tilak Parajuli - Academic Personal Website

Professional academic website showcasing AI/ML research, projects, and experience. Built with Jekyll, designed for fast performance and clean scientific presentation.

## 🌐 Live Site

- **Local**: http://localhost:4000
- **Production**: https://yourusername.github.io (configure with your GitHub Pages URL)

## 📋 Overview

Clean, fast, accessible academic website with:
- **Formal academic design** - Scientific presentation style
- **Fast loading** - Optimized CSS, minimal dependencies
- **Easy to read** - High contrast, clear typography
- **Mobile responsive** - Works perfectly on all devices
- **SEO optimized** - Meta tags, semantic HTML
- **AI chat integration** - RAG-powered Q&A assistant

## 🏗️ Site Structure

```
├── Home (index.md)           # About, recent updates, skills
├── Research (research.md)    # Research interests and activities
├── Projects (projects.md)    # Technical projects and work
├── Experience (experience.md)# Work experience and education
├── CV (cv.md)               # Curriculum vitae
├── Contact (contact.md)     # Contact information
└── Chat (chat.md)           # AI chat assistant
```

## 🚀 Quick Start

### Prerequisites

- Ruby 3.4+ (via Homebrew recommended on macOS)
- Bundler gem manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/yourusername.github.io.git
cd yourusername.github.io

# Install dependencies
bundle install

# Run locally
bundle exec jekyll serve

# Open in browser
open http://localhost:4000
```

### For macOS Users

If you encounter native extension compilation issues:

```bash
# Install Homebrew Ruby
brew install ruby

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/ruby/bin:$PATH"' >> ~/.zshrc
echo 'export PATH="/opt/homebrew/lib/ruby/gems/3.4.0/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Then run bundle install
bundle install
```

## ✏️ Customization

### 1. Update Personal Information

Edit `_config.yml`:

```yaml
title: "Your Name"
email: your.email@example.com
author:
  name: "Your Full Name"
  bio: "Your professional title"
  location: "Your Location"
  linkedin: your-linkedin
  github: your-github
```

### 2. Update Content Pages

All content is in Markdown files at the root:

- `index.md` - Home page (about, skills, highlights)
- `research.md` - Research interests and areas
- `projects.md` - Technical projects
- `experience.md` - Work experience and education
- `cv.md` - Curriculum vitae
- `contact.md` - Contact information

### 3. Add Your Photos

- Profile photo: `/assets/images/profile.jpg` (recommended: 400x400px)
- CV PDF: `/assets/cv.pdf`

### 4. Customize Colors

Edit `/assets/css/main.css`:

```css
/* Primary color (links, accents) */
color: #3498db;

/* Text color */
color: #2c3e50;

/* Background */
background-color: #ffffff;
```

## 🎨 Design Philosophy

This website follows scientific presentation principles:

✅ **Clean & Minimal** - No clutter, focus on content  
✅ **Fast Loading** - Optimized CSS, no heavy frameworks  
✅ **High Contrast** - Easy to read, WCAG compliant  
✅ **White Space** - Ample spacing for readability  
✅ **Consistent** - Uniform styling throughout  
✅ **Professional** - Academic and formal tone

## 📱 Responsive Design

The website is fully responsive and tested on:
- Desktop (1920px+)
- Laptop (1366px)
- Tablet (768px)
- Mobile (375px)

## 🤖 AI Chat Assistant

The `/chat` page includes an AI-powered assistant that can answer questions about your work. To enable:

1. Set up FastAPI backend (see `/backend` directory)
2. Deploy to Vercel (free tier)
3. Update API URL in `/assets/js/chat.js`

## 🚀 Deployment

### GitHub Pages

1. Create repository: `yourusername.github.io`
2. Push your code
3. Enable GitHub Pages in repository settings
4. Site will be live at `https://yourusername.github.io`

### Custom Domain

1. Add `CNAME` file with your domain
2. Configure DNS with your domain provider
3. Enable HTTPS in GitHub Pages settings

## 📦 File Structure

```
.
├── _config.yml              # Jekyll configuration
├── _layouts/                # Page templates
│   ├── default.html
│   └── page.html
├── _includes/               # Reusable components
│   ├── navigation.html
│   └── footer.html
├── assets/
│   ├── css/
│   │   └── main.css        # All styles (optimized)
│   ├── js/
│   │   ├── main.js
│   │   └── chat.js
│   └── images/
│       └── profile.jpg
├── index.md                 # Home page
├── research.md              # Research page
├── projects.md              # Projects page
├── experience.md            # Experience page
├── cv.md                    # CV page
├── contact.md               # Contact page
├── chat.md                  # Chat page
└── backend/                 # RAG backend (separate deployment)
```

## 🔧 Technical Stack

- **Static Site Generator**: Jekyll 4.2
- **Styling**: Pure CSS (no frameworks)
- **Hosting**: GitHub Pages (free)
- **Backend**: FastAPI + Vercel (for chat)
- **AI**: LangChain, Hugging Face (for RAG)

## ⚡ Performance

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Lighthouse Score**: 95+
- **File Size**: < 50KB (CSS + JS)

## 🎯 Features

✅ Clean scientific design  
✅ Fast page loads  
✅ Mobile responsive  
✅ SEO optimized  
✅ Accessible (WCAG AA)  
✅ Easy content updates  
✅ AI chat assistant  
✅ Downloadable CV  
✅ Social media links  
✅ No dependencies  

## 📝 Content Guidelines

### Writing Style

- **Formal & Academic** - Professional tone
- **Clear & Concise** - Short paragraphs, bullet points
- **Scannable** - Use headings, subheadings
- **Objective** - Focus on facts and achievements

### Page Organization

- **Home**: Brief intro, highlights, skills
- **Research**: Detailed research interests
- **Projects**: Technical work with results
- **Experience**: Chronological work history
- **CV**: Comprehensive academic record
- **Contact**: Multiple contact options

## 🔄 Updates

To update your website:

1. Edit the relevant Markdown file
2. Commit and push to GitHub
3. GitHub Pages will automatically rebuild (2-5 minutes)

For local testing:
```bash
bundle exec jekyll serve
```

## 📊 SEO Best Practices

- ✅ Descriptive page titles
- ✅ Meta descriptions
- ✅ Semantic HTML
- ✅ Alt text for images
- ✅ Sitemap.xml
- ✅ Robots.txt
- ✅ Open Graph tags

## 🆘 Troubleshooting

### Jekyll Won't Build

```bash
# Clear cache and rebuild
bundle exec jekyll clean
bundle exec jekyll build
```

### Missing Dependencies

```bash
# Reinstall gems
rm Gemfile.lock
bundle install
```

### Port Already in Use

```bash
# Kill process on port 4000
lsof -ti:4000 | xargs kill

# Or use different port
bundle exec jekyll serve --port 4001
```

## 📖 Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Guide](https://docs.github.com/en/pages)
- [Markdown Guide](https://www.markdownguide.org/)

## 📄 License

MIT License - feel free to use this template for your own website.

## 🤝 Contributing

This is a personal website template. Feel free to fork and adapt for your needs.

## 📧 Contact

**Tilak Parajuli**  
Email: tilak.parajuli.58@gmail.com  
LinkedIn: [linkedin.com/in/tilak-parajuli](https://linkedin.com/in/tilak-parajuli)  
GitHub: [github.com/tilak-parajuli](https://github.com/tilak-parajuli)

---

**Last Updated**: October 2024  
**Version**: 1.0.0  
**Built with**: Jekyll + GitHub Pages
