---
layout: default
title: Blog
permalink: /blog/
---

# Blog

<div class="post-list">
{% for post in site.posts %}
<div class="post-item">
  <span class="post-date">{{ post.date | date: "%b %d, %Y" }}</span>
  <a href="{{ post.url | relative_url }}">{{ post.title }}</a>{% if post.description %} <span class="post-desc">{{ post.description }}</span>{% endif %}
</div>
{% endfor %}
</div>

{% if site.posts.size == 0 %}
<p class="text-muted">No posts yet. Check back soon.</p>
{% endif %}
