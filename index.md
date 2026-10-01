---
layout: default
title: Home
---

<div class="profile">
  <img src="{{ '/assets/images/profile.jpg' | relative_url }}" alt="Tilak Parajuli" class="profile-photo" width="110" height="110" loading="eager">
  <div class="profile-info">
    <h1>Tilak Parajuli</h1>
    <p class="role">AI/ML Engineer and Researcher</p>
    <p class="links">
      <a href="mailto:{{ site.author.email }}">Email</a>
      <a href="{{ site.author.github_url }}" target="_blank" rel="noopener">GitHub</a>
      <a href="{{ site.author.linkedin_url }}" target="_blank" rel="noopener">LinkedIn</a>
      <a href="{{ site.author.scholar_url }}" target="_blank" rel="noopener">Scholar</a>
      <a href="{{ site.author.orcid_url }}" target="_blank" rel="noopener">ORCID</a>
      <a href="{{ '/assets/tilak-parajuli-cv.pdf' | relative_url }}" target="_blank" rel="noopener">CV (PDF)</a>
    </p>
  </div>
</div>

<div class="home-bio" markdown="1">

My work centers on one problem: when one model judges another's output, can that judgment be trusted, where does it fail, and what fixes it? I study it in research and build against it in production as a data scientist and AI engineer.

Currently a Data Scientist / AI Engineer at [Climate Clean Solutions](https://climatecleansolutions.com/) & LowPropTax, where I own production for a multi-service agent platform on AWS. Previously at [Fusemachines](https://fusemachines.com/) and [NAAMII](https://naamii.org/about/team-and-leadership/tilak_parajuli). B.Sc. in Computer Science and Information Technology, Tribhuvan University.

**Research interests:** evaluation reliability, LLM-as-judge, error propagation in multi-agent systems, AI safety and security.

</div>

<div class="home-section">
<h2>Publications</h2>
{% for p in site.data.publications %}{% include publication.html pub=p mode="compact" %}{% endfor %}
<p><a href="{{ '/publications/' | relative_url }}">All publications</a></p>
</div>

<div class="home-section" markdown="1">

## Recent

- **Sep 2026** · Paper accepted at the NeurIPS 2026 Workshop on Trust-AI-Eval; extended version submitted to ICLR 2027.
- **Aug 2026** · Fault-injection study selected as a top AI/ML project at SISTER 2026.
- **Jan 2026** · Joined Climate Clean Solutions & LowPropTax.

</div>
