document.addEventListener('DOMContentLoaded', function () {
  // Header height is a fixed CSS token (--header-height). It must NOT be
  // recomputed from the rendered header here: the header's own height is
  // driven by that same variable, so measuring it and writing it back forms
  // a feedback loop that grew the navbar on every resize/zoom event.

  var toggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('primary-nav');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      menu.classList.toggle('active');
      toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
    });
    document.addEventListener('click', function (e) {
      if (!menu.contains(e.target) && !toggle.contains(e.target) && menu.classList.contains('active')) {
        menu.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // TOC
  var source = document.querySelector('[data-toc-source]');
  var tocNav = document.getElementById('toc');
  if (source && tocNav) {
    var headings = source.querySelectorAll('h2, h3');
    var list = document.createElement('ul');
    var currentH2List = null;
    headings.forEach(function (h, i) {
      var id = h.id || 'section-' + i;
      h.id = id;
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent;
      a.addEventListener('click', function (e) {
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

    if ('IntersectionObserver' in window) {
      var links = tocNav.querySelectorAll('a');
      var map = new Map();
      links.forEach(function (l) { map.set(l.getAttribute('href').slice(1), l); });
      var offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--header-height')) || 56;
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            links.forEach(function (l) { l.classList.remove('active'); });
            var link = map.get(entry.target.id);
            if (link) link.classList.add('active');
          }
        });
      }, { rootMargin: '-' + (offset + 20) + 'px 0px -60% 0px', threshold: 0.1 });
      headings.forEach(function (h) { io.observe(h); });
    }
  }
});

document.querySelectorAll('a[target="_blank"]').forEach(function (link) {
  link.setAttribute('rel', 'noopener noreferrer');
});

(function () {
  var el = document.getElementById('email-link');
  if (!el) return;
  var u = 'tilak.parajuli.58', d = 'gmail.com';
  var addr = u + '@' + d;
  el.innerHTML = '<a href="mai' + 'lto:' + addr + '">' + addr + '</a>';
})();
