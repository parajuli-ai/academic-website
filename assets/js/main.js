/**
 * Main JavaScript for Academic Personal Website
 */

// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    // Set CSS var --header-height dynamically from actual header
    const siteHeader = document.querySelector('.site-header');
    if (siteHeader) {
        const setHeaderHeight = () => {
            let h = siteHeader.getBoundingClientRect().height || 70;
            if (h < 50) h = 70;
            document.documentElement.style.setProperty('--header-height', `${Math.ceil(h)}px`);
        };
        const updateHeaderOnScroll = () => {
            if (window.scrollY > 4) {
                siteHeader.classList.add('scrolled');
            } else {
                siteHeader.classList.remove('scrolled');
            }
        };
        // Initialize and keep height stable (no delayed recalculations)
        setHeaderHeight();
        window.addEventListener('resize', setHeaderHeight);
        // Only toggle class on scroll to avoid layout thrash/flicker
        window.addEventListener('scroll', updateHeaderOnScroll, { passive: true });
        updateHeaderOnScroll();
    }
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.getElementById('primary-nav');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            const isExpanded = navMenu.classList.contains('active');
            navToggle.setAttribute('aria-expanded', isExpanded);
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (navMenu && navToggle) {
            const isClickInside = navMenu.contains(event.target) || navToggle.contains(event.target);
            if (!isClickInside && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        }
    });
    
    // Close mobile menu when clicking a link
    if (navMenu) {
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    navMenu.classList.remove('active');
                    if (navToggle) {
                        navToggle.setAttribute('aria-expanded', 'false');
                    }
                }
            });
        });
    }
    
    // Build Table of Contents from h2/h3 in page-content
    (function buildTOC() {
        const source = document.querySelector('[data-toc-source]');
        const tocNav = document.getElementById('toc');
        if (!source || !tocNav) return;
        const headings = source.querySelectorAll('h2, h3');
        const list = document.createElement('ul');
        let currentH2List = null;
        headings.forEach((h, idx) => {
            const id = h.id || `section-${idx}`;
            h.id = id;
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = `#${id}`;
            a.textContent = h.textContent;
            a.addEventListener('click', (e) => {
                e.preventDefault();
                document.getElementById(id).scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
            li.appendChild(a);
            if (h.tagName === 'H2') {
                list.appendChild(li);
                currentH2List = document.createElement('ul');
                li.appendChild(currentH2List);
            } else if (h.tagName === 'H3' && currentH2List) {
                currentH2List.appendChild(li);
            } else {
                list.appendChild(li);
            }
        });
        tocNav.appendChild(list);
        
        // Highlight active section
        if ('IntersectionObserver' in window) {
            const links = tocNav.querySelectorAll('a');
            const map = new Map();
            links.forEach(l => map.set(l.getAttribute('href').slice(1), l));
            const headerOffset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--header-height')) || 70;
            const io = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        links.forEach(l => l.classList.remove('active'));
                        const link = map.get(entry.target.id);
                        if (link) link.classList.add('active');
                    }
                });
            }, { rootMargin: `-${headerOffset + 20}px 0px -60% 0px`, threshold: 0.1 });
            headings.forEach(h => io.observe(h));
        }
    })();
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '#0') {
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Add loading state to external links
document.querySelectorAll('a[target="_blank"]').forEach(link => {
    link.setAttribute('rel', 'noopener noreferrer');
});

// Lazy loading for images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// Print page functionality
function printPage() {
    window.print();
}

// Copy BibTeX to clipboard
function copyBibtex(element) {
    const text = element.textContent;
    navigator.clipboard.writeText(text).then(() => {
        const originalText = element.getAttribute('data-original-text') || 'Copy';
        element.textContent = 'Copied!';
        setTimeout(() => {
            element.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Back to top button (optional)
function createBackToTopButton() {
    const button = document.createElement('button');
    button.innerHTML = '↑';
    button.className = 'back-to-top';
    button.setAttribute('aria-label', 'Back to top');
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: white;
        border: none;
        font-size: 1.5em;
        cursor: pointer;
        display: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        transition: opacity 0.3s ease;
        z-index: 999;
    `;
    
    document.body.appendChild(button);
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    });
    
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Initialize back to top button
createBackToTopButton();

// Analytics event tracking (if Google Analytics is configured)
function trackEvent(category, action, label) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': category,
            'event_label': label
        });
    }
}

// Track downloads
document.querySelectorAll('a[href$=".pdf"]').forEach(link => {
    link.addEventListener('click', function() {
        trackEvent('Downloads', 'PDF', this.href);
    });
});

// Track external links
document.querySelectorAll('a[target="_blank"]').forEach(link => {
    link.addEventListener('click', function() {
        trackEvent('Outbound Links', 'Click', this.href);
    });
});

