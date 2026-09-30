---
layout: page
title: Work
permalink: /work/
toc: true
---

## Experience

{% for e in site.data.experience %}{% include experience.html job=e mode="full" %}{% endfor %}

## Projects

{% for pr in site.data.projects %}{% include project.html project=pr %}{% endfor %}
