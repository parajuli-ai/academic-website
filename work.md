---
layout: page
title: Work
permalink: /work/
toc: true
---

## Experience

### Data Scientist
**Climate Clean Solutions & LowPropTax**
*Jan 2026 to Present · California, USA / Kathmandu, Nepal (Hybrid)*

- Architected an autonomous multi-agent LLM pipeline that automates property-tax valuation end-to-end, combining RAG with API-driven comparable retrieval.
- Designed valuation models over physical, neighborhood, and climate signals, with automated QA gates that enforce >10% reduction thresholds before an appeal is filed.
- Engineered real-time data pipelines on AWS (S3 + Parquet) for air-quality signals such as PM2.5, NO₂, O₃, and CO₂, with dimensional modeling for downstream analytics.
- Automated time-series, anomaly-detection, and geospatial reporting in Power BI, replacing manual reporting cycles.

### AI/ML Research Fellow
**Fusemachines Nepal**
*June 2025 to Sept 2025 · Kathmandu, Nepal*

- Built an automated model-evaluation framework (MAE, RMSE, MAPE, SMAPE) with visual reporting, adopted across the team's forecasting models.
- Shipped real-time gaze detection into a live proctoring product (MediaPipe FaceMesh + React).
- Prototyped agentic workflows and fine-tuned vision-language models (CLIP, BLIP, PaliGemma 2) for evaluation.

### RPA Developer
**Quickfox Consulting**
*Feb 2025 to May 2025 · Kathmandu, Nepal*

- Automated data entry, form submission, web scraping, and Excel consolidation with production RPA bots, eliminating repetitive manual workflows.
- Led an LLM-powered data-cleaning pipeline that restored integrity to legacy medical databases.

### AI Research Intern
**NAAMII**
*June 2024 to Sept 2024 · Kathmandu, Nepal*

- Analyzed clinical and radiomics data for a radiation-oncology study under Dr. Taman Upadhaya (Cedars-Sinai).
- Applied permutation testing, ROC-AUC, and correlation analysis to surface candidate biomarker signals.

## Projects

### [RAG Pipeline for Job Data Retrieval](https://github.com/parajulitilak/RAG-Pipeline-for-Job-Data-Retrieval)
*Python, FastAPI, LlamaIndex, ChromaDB, Cohere, BM25, Docker*

End-to-end hybrid-retrieval system combining BM25 sparse search with dense vector embeddings and Cohere reranking. Served via FastAPI, fully containerized.

**Result:** Sub-second retrieval with improved relevance over single-mode baselines.

### [Travya: Multi-Agent Travel Platform](https://github.com/fuseai-fellowship/Travya---Agentic-AI-Powered-Travel-Companion)
*Python, LangGraph, React, FastAPI, PostgreSQL, Redis, Docker*

Multi-agent architecture with specialized research, planning, and booking agents. Streaming AI interface with Google Maps, Amadeus, and Stripe integrations.

**Result:** Full booking flow from natural language query to confirmed reservation, with real-time agent coordination.

### [Text Summarization (LSA + T5)](https://github.com/parajulitilak/seventh_sem_project/tree/main/summarizer_app)
*Python, Transformers (T5), NLP*

Dual extractive/abstractive summarizer. Fine-tuned T5 alongside LSA baseline, evaluated with ROUGE metrics.

**Result:** T5 outperformed LSA on abstractive quality; LSA faster for extractive use cases.

## Research Interests

I focus on building AI systems that work reliably in production: retrieval-augmented generation, multi-agent orchestration, applied ML (computer vision, time-series), and computational biology.

Beyond core AI, I'm drawn to how intelligence works at every level: how neurons encode signals, how people think, speak, and make decisions, and how these principles can inform better AI architectures. I follow neuroscience, cognitive psychology, robotics, and physics with the same curiosity I bring to engineering.

Current questions I'm exploring:

- How to evaluate and improve retrieval quality in RAG pipelines at scale
- Designing multi-agent systems that fail gracefully under real-world conditions
- Cross-domain transfer learning for clinical and environmental data
- What cognitive science and neuroscience reveal about attention, memory, and perception in both biological and artificial systems

All code is on [GitHub](https://github.com/parajulitilak). Publications and citations on [Google Scholar](https://scholar.google.com/citations?user=WAKS2J4AAAAJ).
