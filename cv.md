---
layout: page
title: Curriculum Vitae
permalink: /cv/
toc: false
hide_title: true
---

<div class="cv-header">
  <h1 class="cv-name">Tilak Parajuli</h1>
  <p class="cv-contact">
    Kathmandu, Nepal |
    <a href="mailto:{{ site.author.email }}">{{ site.author.email }}</a> |
    <a href="{{ site.author.linkedin_url }}" target="_blank" rel="noopener">LinkedIn</a> |
    <a href="{{ site.author.github_url }}" target="_blank" rel="noopener">GitHub</a> |
    <a href="{{ site.author.scholar_url }}" target="_blank" rel="noopener">Scholar</a>
  </p>
  <p class="cv-download"><a href="{{ '/assets/tilak-parajuli-cv.pdf' | relative_url }}" class="btn" target="_blank" rel="noopener">Download CV (PDF)</a></p>
</div>

AI/ML engineer and researcher working on evaluation reliability: I measure where automated judges fail and build the evaluation gates that decide what reaches a human. I also own production for a multi-service agent platform on AWS.

## Publications

{% for p in site.data.publications %}{% include publication.html pub=p mode="compact" %}{% endfor %}

## Experience

{% for e in site.data.experience %}{% include experience.html job=e mode="compact" %}{% endfor %}

Details on the [Work]({{ '/work/' | relative_url }}) page.

## Skills

<dl class="skills">
  <dt>Evaluation &amp; Security</dt>
  <dd>LLM-as-judge evaluation, AI safety, threat modeling, least-privilege IAM, secrets management, auth hardening, PHI handling</dd>
  <dt>Cloud &amp; Infrastructure</dt>
  <dd>AWS (ECS Fargate, Lambda, API Gateway, SQS/SNS, S3, ECR, CloudWatch, IAM, Secrets Manager, SSM, PrivateLink, Route 53), Terraform, Docker, MongoDB Atlas, DuckDB, Parquet</dd>
  <dt>CI/CD &amp; Release</dt>
  <dd>GitHub Actions (OIDC to AWS, matrix builds, per-service test baselines, release manifests, image promotion by digest), permission simulation before deploy</dd>
  <dt>LLM Engineering</dt>
  <dd>RAG (Pinecone, Qdrant), fine-tuning (LoRA/PEFT), multi-agent systems, DeepInfra, Anthropic API, LangGraph, per-request cost accounting, PyTorch</dd>
  <dt>Backend &amp; Data</dt>
  <dd>Python, FastAPI, Pydantic, pytest, boto3, SQS consumers with idempotency, structured logging, PostgreSQL, Redis, SQL, Bash, TypeScript</dd>
</dl>

## Education

**B.Sc. in Computer Science and Information Technology**, 78/100, First Division with Distinction
Bhaktapur Multiple Campus, Tribhuvan University · Dec 2019 to Oct 2024

## Honors and Certifications

{% for h in site.data.honors %}- [{{ h.title }}]({{ h.url }}){% if h.note %}. {{ h.note }}{% endif %}
{% endfor %}

<div class="cv-footer"><p>Last updated: September 2026</p></div>
