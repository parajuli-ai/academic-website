---
layout: page
title: Publications
permalink: /publications/
toc: false
---

{% for p in site.data.publications %}{% include publication.html pub=p mode="full" %}{% endfor %}

[Google Scholar profile]({{ site.author.scholar_url }}) · ORCID: [{{ site.author.orcid }}]({{ site.author.orcid_url }})
