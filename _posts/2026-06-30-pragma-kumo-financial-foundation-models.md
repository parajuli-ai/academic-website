---
layout: post
title: "PRAGMA, KumoRFM, and the Gap Between Them: Why Financial AI Needs Both Sequences and Graphs"
date: 2026-06-30
description: "Revolut's PRAGMA models a customer as a sequence of events. Kumo's KumoRFM models an enterprise as a graph of entities. Neither alone detects money laundering well. This post explains the architectural reason, and why NVIDIA paid a reported US$400M to own both sides of the gap."
author: "Tilak Parajuli"
tags: [foundation-models, financial-ai, graph-neural-networks, transformers, banking]
series: "Architecture Deep Dives"
math: true
reading_time: "24 min"
toc: true
---

## 1. Motivation

The motivation for this post is a gap between how one recent model is discussed and what its paper actually reports. In the public conversation about foundation models in banking, including posts circulating in my own professional network, PRAGMA tends to appear as a general purpose replacement for task specific financial machine learning, captured by the slogan that a single pre-trained model can be learned once and adapted many times. The paper supports that reading for most tasks. It also records, in Table 9, one task on which the model is clearly worse than the production system it was built to replace: anti-money-laundering (AML). The authors attribute the shortfall to the architecture itself, not to a lack of data or tuning (Ostroukhov et al., [2026](https://arxiv.org/abs/2604.08649)).

A short time later, NVIDIA, which co-developed PRAGMA, acquired Kumo, the company behind KumoRFM, which is in effect the graph structured model that PRAGMA is not (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)). The contrast between these two systems is the subject of this post. The question I want to answer is concrete: what does each architecture represent, what can it not represent, and what would a model that combined them require. The post explains the landscape and names an open problem. It does not claim to solve that problem; that is the role of the experiments and the paper that should follow.

## 2. Background: why one model per task is breaking down

For roughly a decade, production financial machine learning has followed one pattern: a separate supervised model for each task. A gradient boosted tree for credit risk, another for fraud, another for churn, each with its own feature pipeline, its own SQL, and its own validation. Adding a use case or entering a market means repeating the cycle. The KumoRFM-2 authors quantify the human cost plainly: building the task specific features for a single relational prediction, the current gold standard, requires an expert data scientist and hours to days of work per task (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)).

There is also a deeper limit. Hand built features are fixed, task agnostic aggregations, and a fixed aggregation cannot express a signal that depends on how rows relate to each other. The KumoRFM-2 paper gives a clean illustration. Suppose a parent table is labelled positive exactly when two binary attributes, $A$ and $B$, co-occur in at least one related child row. A column wise aggregation that summarises $A$ and $B$ separately sees identical marginals in the positive and negative classes and cannot separate them at all, scoring an area under the ROC curve of $0.5$; a model that aligns rows before aggregating reaches $1.0$ (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)). The point generalises: compressing a customer's world into a flat row discards exactly the cross row structure that many tasks depend on.

This is the limit that representation learning removed in language and vision, and the foundation model recipe is the same in finance. Pre-train one model on broad raw data with a self supervised objective, obtain a general representation, then adapt it cheaply to many tasks (Bommasani et al., [2021](https://arxiv.org/abs/2108.07258)). Formally, pre-training minimises a loss that needs no labels,

$$\theta^\star = \arg\min_{\theta} \mathbb{E}_{x \sim \mathcal{D}}\big[\mathcal{L}_{\mathrm{ssl}}(f_\theta, x)\big],$$

where $f_\theta$ is the model, $\mathcal{D}$ is the data distribution, and $\mathcal{L}_{\mathrm{ssl}}$ is a pretext objective such as reconstructing masked inputs or predicting the next token. Adaptation then fits a small task head $g_\psi$ on the learned representation $f_{\theta^\star}(x)$ using a comparatively small labelled set. One model is learned once and reused many times.

Finance, however, has structure that text does not, and there are two natural ways to encode it. The first treats each customer as an ordered stream of events, a sequence. The second treats the whole institution as interconnected tables, a graph. That single decision, the inductive bias, is what separates the two models in this post. Figure 1 places the two pipelines side by side.

![Figure 1. Sequence pipeline beside graph pipeline.](https://github.com/user-attachments/assets/e685203f-8f0e-4667-a0ac-e13699ae22b3)

*Figure 1. Two ways to build a financial foundation model. PRAGMA (left) reads one customer as an ordered event sequence and produces a per user embedding. KumoRFM (right) reads the institution as a temporal graph and answers queries by reasoning over entity subgraphs. Blue marks input data, green a learned representation, orange a downstream task. Source: author created and original; not reproduced from any paper.*

## 3. PRAGMA: the sequence paradigm

PRAGMA is a family of encoder only Transformers, pre-trained with masked modelling on banking event sequences (Ostroukhov et al., [2026](https://arxiv.org/abs/2604.08649)). The closest familiar analogue is BERT (Devlin et al., [2019](https://arxiv.org/abs/1810.04805)), with one change of object: where BERT masks word pieces in a sentence, PRAGMA masks fields inside a customer's financial history and learns to reconstruct them. According to the paper, the training corpus contains 26 million customer records across 111 countries, comprising 24 billion events and 207 billion tokens over a 25 month window. Some secondary write ups round this to forty billion events from twenty five million users; the figures here follow the paper itself, because the difference matters for a citable claim.

### 3.1 Tokenisation: key, value, and time

A financial event is not a sentence. It is a short record of mixed types: a transaction type, an amount, a merchant category, a channel, a free text note, and a timestamp. Serialising that as plain text inflates the sequence and, more damagingly, splits numbers into digit fragments that lose magnitude and order. PRAGMA instead decomposes each datum into a semantic type (the key), a value, and a temporal coordinate, an approach established by earlier transaction models.

Keys form a small vocabulary, on the order of sixty tokens, one per field type. Values are encoded by type: numeric values are mapped to learned percentile buckets, with one token per bucket and a dedicated bucket for zero, which preserves magnitude and order; low cardinality strings become a single categorical token; free text is split with a sub word tokeniser. The value vocabulary is roughly twenty eight thousand tokens. Time is encoded twice. The elapsed time $t$ in seconds since the most recent event is compressed with a soft logarithmic transform,

$$\tau(t) = 8\ln\left(1 + t/8\right),$$

which keeps fine resolution for recent events while compressing decade old history, and calendar structure is added through fixed period sinusoids of the hour, day of week, and day of month, for example $\big(\sin(2\pi h / 24), \cos(2\pi h / 24)\big)$ for the hour $h$. Each key and value pair is embedded from a shared table $E$ and summed, then given a within field position code,

$$x = \mathrm{PosEmb}\big(E(k) + E(v)\big), \qquad x \in \mathbb{R}^{n \times d},$$

where $d$ is the embedding dimension. A learnable summary token is prepended to each sequence.

### 3.2 A hierarchy of three Transformers

PRAGMA is not one Transformer but three, composed in a hierarchy. The primitive is standard self attention (Vaswani et al., [2017](https://arxiv.org/abs/1706.03762)): for an input packed as rows of a matrix $X$, the model forms queries, keys, and values $Q = XW_Q$, $K = XW_K$, $V = XW_V$ and computes

$$\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right) V,$$

with $d_k$ the key dimension, and multi head attention runs several such maps in parallel. Every block in PRAGMA is bidirectional, which suits discriminative tasks where the full history is available at prediction time. The three blocks are a profile state encoder, which compresses static per user context such as plan tier and account age, together with timestamped milestones, into a single summary vector $z_a$; an event encoder, which encodes each event independently into a per event vector and then adds the calendar features; and a history encoder, which concatenates the profile vector with the event vectors and contextualises them with a final bidirectional Transformer. The history encoder output $z_h$ is the record level representation used downstream. Temporal coordinates enter the encoders through rotary position embeddings (Su et al., [2024](https://arxiv.org/abs/2104.09864)), which rotate each query and key by an angle proportional to position so that attention depends on relative time. The detail to keep in mind is that the event encoder processes events independently, with no attention between events; this choice is efficient, and it is also the origin of the model's relational limitation.

The family scales by widening and deepening all three blocks together: a small model at 10 million parameters, a medium model at 100 million, and a large model at 1 billion. To my knowledge it is the largest published encoder backbone for consumer banking events.

### 3.3 The pre-training objective

PRAGMA is trained by masked modelling. With $M$ the set of masked positions in a record $x$, the model maximises the likelihood of the originals given the rest,

$$\mathcal{L}_{\mathrm{MLM}} = -\mathbb{E}_{x \sim \mathcal{D}} \sum_{i \in M} \log p_\theta\big(x_i \mid x_{\setminus M}\big).$$

Masking happens at three scales: individual tokens, whole events, and whole keys. Masking a whole event forces reconstruction from neighbouring events; masking a whole key forces the model to infer a field's value from context. For each masked position the prediction head combines three vectors, the local within event representation, the cross event representation, and the user level representation, and scores against the embedding table with a cross entropy loss. A fraction of selected positions are replaced with an unknown token excluded from the loss, which acts as input dropout and reduces dependence on the mask token that never appears at prediction time.

### 3.4 Adaptation and systems

Two adaptation modes are reported. In the probe setting the backbone is frozen, the representation $z_h$ is extracted, and a linear or logistic probe is fit, which is fast enough to iterate in minutes. In the LoRA setting (Hu et al., [2022](https://arxiv.org/abs/2106.09685)), only low rank updates to the attention and feed forward projections are trained, a small fraction of parameters, leaving the shared backbone intact.

On systems, the paper reports pre-training on 16 to 32 H100 GPUs depending on model size, in bf16, with the small model converging in about two days and the larger two in about two weeks each. Revolut's infrastructure account describes a dedicated 64 GPU cluster for PRAGMA and notes that Revolut's total artificial intelligence footprint exceeds 200 H100 GPUs on its cloud provider (Nebius, [2026](https://nebius.com/customer-stories/revolut)); the figure of two hundred or more GPUs that circulates therefore describes the whole estate, not the PRAGMA training run. Efficiency comes from packing variable length events with a fused attention kernel (Dao et al., [2022](https://arxiv.org/abs/2205.14135)) and from aggressive truncation, with very long histories subsampled to the most recent events.

### 3.5 Results, and the metric caveat

PRAGMA reports only relative improvements, the relative change $(x / \text{baseline} - 1)$ reported as a percentage, because absolute metrics are commercially sensitive. Against task specific baselines, the large model with LoRA improves credit scoring by 130.2% in PR-AUC and 12.4% in ROC-AUC; communication engagement by 79.4% and 20.4%; external fraud by 16.7% in precision and 64.7% in recall; product recommendation by 40.5% in mean average precision; recurrent transaction detection by 5.8% in F1; and lifetime value by 1.8% in PR-AUC and 2.6% in ROC-AUC (Ostroukhov et al., [2026](https://arxiv.org/abs/2604.08649)). These are offline backtests on internal datasets, a point the peer review section returns to.

### 3.6 The AML result

Anti-money-laundering is the exception. Treated as a binary classification task, it is the one place the model underperforms its production baseline, by 47.1% in $F_{0.5}$, the precision weighted F measure,

$$F_\beta = (1 + \beta^2)\frac{P \cdot R}{\beta^2 P + R}, \qquad \beta = 0.5,$$

using a probe on the large model's embeddings (Ostroukhov et al., [2026](https://arxiv.org/abs/2604.08649), Table 9). The authors' explanation is the centre of this post. In their words, "AML detection is inherently relational: the baseline leverages cross-record features that capture network-level signals." Because the model encodes each customer's history in isolation, its embeddings cannot represent the cross record dependencies the task needs. This is a structural ceiling, not a shortage of training, and the paper names cross record interaction as future work.

One qualification matters for accuracy. The 47.1% figure is the research backbone losing to an internal, network aware baseline model. It is not a claim that Revolut cannot detect laundering. In production, that work runs through a separate set of language model based financial crime agents, on the order of two million risk assessment tasks per month (Nebius, [2026](https://nebius.com/customer-stories/revolut)). PRAGMA, the foundation model, is simply not the AML engine, and the paper is candid about why it cannot be. Figure 2 shows the reason in one picture.

![Figure 2. What each model can see on a money-laundering case.](https://github.com/user-attachments/assets/17bc5fd2-6500-4728-9003-250fdc00e893)

*Figure 2. The same scenario, two representations. User A's own transactions look ordinary. The laundering signal is the funnel shape, two intermediary accounts converging on a flagged entity, which lives entirely in the edges between accounts. A graph model (right) encodes those edges; a sequence model (left) encodes A's history in isolation, so the structure is, by construction, outside its view. Source: author created and original; the scenario depicts the mechanism behind PRAGMA Table 9.*

## 4. KumoRFM: the graph paradigm

KumoRFM begins from the opposite premise: the most valuable enterprise data is already structured, as customers, accounts, transactions, and products linked by keys, and flattening it into one wide table discards the structure that matters (Fey et al., [2025](https://kumo.ai/company/news/kumo-relational-foundation-model/)). So it does not flatten. It learns directly on the schema.

### 4.1 A relational database as a temporal graph

The construction comes from Relational Deep Learning (Fey et al., [2024](https://relbench.stanford.edu)) and is lossless. Each table becomes a node type, each row a node, each primary to foreign key link an edge, and each record's timestamp orders the graph in time. The result is a temporal heterogeneous graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ in which every node $v$ carries a type, its column values, and a time $t_v$, so that one can form a time consistent snapshot $\mathcal{G}^{\le t}$ containing only records available up to time $t$. A money laundering ring is now a concrete substructure in $\mathcal{G}$, the funnel of Figure 2.

### 4.2 Message passing, and how KumoRFM differs from it

The standard way to learn on this graph is message passing, in which a node's representation is updated by aggregating transformed messages from its neighbours (Gilmer et al., [2017](https://arxiv.org/abs/1704.01212)):

$$h_v^{(\ell+1)} = \phi^{(\ell)}\Big(h_v^{(\ell)}, \bigoplus_{u \in \mathcal{N}(v)} \psi^{(\ell)}\big(h_v^{(\ell)}, h_u^{(\ell)}, e_{uv}\big)\Big),$$

where $h_v^{(\ell)}$ is node $v$'s embedding at layer $\ell$, $\mathcal{N}(v)$ its neighbours, $\psi$ a message function, $\bigoplus$ a permutation invariant aggregator, $\phi$ an update, and $e_{uv}$ the edge features. Stacking $L$ layers lets information travel $L$ hops, so a signal can flow from a flagged account through an intermediary to the customer under assessment. The supervised relational baselines, such as GraphSAGE (Hamilton et al., [2017](https://arxiv.org/abs/1706.02216)), work this way. PRAGMA's event encoder, by contrast, deliberately allows no message passing between events, which is precisely the capability AML needs.

KumoRFM is not a supervised message passing network. It is a relational foundation model that predicts by in-context learning, the mechanism behind few-shot prediction in large language models (Brown et al., [2020](https://arxiv.org/abs/2005.14165)), adapted to structured data. Given a target node $v_n$ at a future time $t_n$, the model predicts

$$\hat{y}_n = \mathrm{RFM}_{\theta}\Big(\mathcal{G}^{\le t_n}[v_n], \big\lbrace \big(\mathcal{G}^{\le t_i}[v_i], y_i\big)\big\rbrace_{i=1}^{n-1}\Big),$$

where $\mathcal{G}^{\le t}[v]$ is the entity centred subgraph around $v$ using only records up to time $t$, the set in braces is a context of labelled examples constructed from the database's own history, and the parameters $\theta$ stay frozen (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)). No gradient step is taken at prediction time; the model must reason over the supplied subgraphs.

### 4.3 The KumoRFM-2 architecture, stated precisely

It is worth being exact here, because the architecture is easy to mis-state. KumoRFM-2 does not use graph message passing as its core, and it is not, despite some secondary descriptions, built on a Relational Graph Transformer. Its mechanism is a hierarchical attention scheme over two stages (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)). A lightweight network first computes row representations within each table by alternating column wise and row wise attention, with the context targets injected early so that feature extraction is task conditioned. A larger network then relates these representations across tables using foreign key attention and across context examples using cross sample attention. This staged design attends across four axes, rows, columns, foreign keys, and samples, while avoiding the quadratic cost of attending to every cell. The Relational Graph Transformer (Dwivedi et al., [2025](https://arxiv.org/abs/2505.10960)) is a distinct, supervised architecture that appears in the paper only as a baseline, not as what KumoRFM-2 is.

Queries are written in a declarative Predictive Query Language (Kocijan et al., [2026](https://arxiv.org/abs/2602.09572)), so a request such as predicting which customers will churn in the next thirty days is expressed as a short composition of aggregations and filters, from which the system constructs context examples and subgraphs automatically while preserving temporal consistency.

### 4.4 What the numbers say

KumoRFM-2 is evaluated on 41 prediction tasks across 15 relational databases drawn from RelBench v1 (Robinson et al., [2024](https://arxiv.org/abs/2407.20060)), RelBench v2 (Gu et al., [2026](https://arxiv.org/abs/2602.12606)), the SALT enterprise benchmark, and 4DBInfer, none of which were used in pre-training (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)). In context learning uses at most ten thousand context examples, which in the largest databases is as little as 0.2% of the available training data. On RelBench v1 the model improves on its predecessor by about 10% and surpasses the strongest supervised model, RelGNN, by about 5% on both classification and regression. On the SALT benchmark it exceeds large AutoGluon ensembles by about 8% and a recent tabular foundation model by about 25%. Fine tuning adds a further 16%. The authors state that this is, to their knowledge, the first time a few-shot foundation model has surpassed tuned supervised approaches on these benchmarks. On engineering, the system scales to databases of more than 500 billion rows through an SSD backed graph engine, reaching about 5 GB per second of bandwidth and 20 million lookups per second. Unlike PRAGMA, the model is available through a public software development kit, and the benchmark scripts are open at [github.com/kumo-ai/kumo-rfm](https://github.com/kumo-ai/kumo-rfm).

### 4.5 What KumoRFM does not do well

The limitation is the mirror image of PRAGMA's. KumoRFM represents temporal ordering through timestamps on the graph, but it is not a sequence model. A customer's last thirty transactions enter as dated neighbours of a node, not as an ordered stream processed with fine grained temporal attention. Signals that turn on the exact order and recency of events, the kind a behavioural credit model relies on, are where a graph model that treats those events as a bag of dated neighbours is weakest. Each model is strong on the structure the other discards.

### 4.6 The graph paradigm is an industry-wide bet

KumoRFM is not alone, and this matters for the strategic reading later. Google Research describes graph foundation models built on the same table to graph construction, a single model that generalises to unseen schemas and features without retraining; on internal tasks such as spam detection in ads, across dozens of connected tables, they report 3 to 40 times higher average precision than the best tuned single table baselines (Galkin & Doguparty, [2025](https://research.google/blog/graph-foundation-models-for-relational-data/)). On the academic side, the relational foundation model space already includes Griffin (Wang et al., [2025](https://arxiv.org/abs/2505.05568)), the Relational Transformer trained by masked token prediction (Ranjan et al., [2025](https://arxiv.org/abs/2510.06377)), and the Relational Graph Transformer architecture (Dwivedi et al., [2025](https://arxiv.org/abs/2505.10960)), alongside the benchmarks that anchor the field, RelBench and its successor (Robinson et al., [2024](https://arxiv.org/abs/2407.20060); Gu et al., [2026](https://arxiv.org/abs/2602.12606)). It is worth distinguishing these from single table tabular foundation models such as TabPFN (Hollmann et al., [2023](https://arxiv.org/abs/2207.01848)), which operate on one flat table and cannot represent multi table structure, and from financial language models such as BloombergGPT (Wu et al., [2023](https://arxiv.org/abs/2303.17564)), which model financial text rather than transaction events and address a different problem entirely.

## 5. The coverage map: what each model can and cannot see

Place every financial task on two axes. The horizontal axis is how much the signal depends on a single customer's ordered sequence of events. The vertical axis is how much it depends on structure across entities. The division of labour, and one empty corner, then become visible.

![Figure 3. Coverage map of tasks by temporal and relational complexity.](https://github.com/user-attachments/assets/5b448292-0ee5-4cc3-b101-206d1e0f9c5c)

*Figure 3. The argument in one chart. Credit scoring and lifetime value sit low on the relational axis, so both models do well. Recommendation rewards fine grained sequence dynamics, which favours the sequence model. AML and fraud ring detection are low in per user temporal complexity but high in relational complexity, which favours the graph model. The upper right corner, tasks that need both rich per user behaviour and cross entity structure, is covered by neither model today. Source: author created and original.*

The quantitative picture, restricted to numbers the papers actually report, is summarised in Table 1.

**Table 1. Benchmark comparison, published results only.**

| Model | AML | Fraud | Credit | LTV and churn | Recommendation | Data scale |
|---|---|---|---|---|---|---|
| PRAGMA (Revolut, NVIDIA) | underperforms, 47.1% lower F0.5 | strong, +16.7% precision and +64.7% recall | strong, +12.4% ROC-AUC | modest, +2.6% ROC-AUC | strong, +40.5% mAP | 26M users, 24B events |
| KumoRFM-2 (Kumo, NVIDIA) | strong, inferred from relational design | strong | strong | strong | strong | 500B+ rows |
| nuFormer (Nubank) | not reported | not the reported focus | not the reported focus | +4.4% churn reduction, production | +1.25% AUC | single bank |
| XGBoost or LightGBM | strong, with network features | moderate | moderate | moderate | moderate | varies |

Notes. "Strong" means the model surpasses tuned supervised baselines on the cited benchmarks. KumoRFM-2 improves on its predecessor by about 10% and on RelGNN by about 5% on RelBench v1, and exceeds AutoGluon by about 8% and a tabular foundation model by about 25% on SALT (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)). The KumoRFM entry for AML is inferred from its relational design and general benchmark strength, not from a published financial AML benchmark, and is marked as such. nuFormer supports credit, fraud, and recommendation, but its published numbers are a recommendation AUC gain and a production churn reduction (Braithwaite et al., [2025](https://arxiv.org/abs/2507.23267)). PRAGMA's figures are relative, with absolutes withheld, and are offline backtests on internal data (Ostroukhov et al., [2026](https://arxiv.org/abs/2604.08649)); nuFormer's churn figure is the only production deployment result in the table.

The pattern matches Figure 3. The two models are complementary, the gap is real, and the corner where a task needs both views at once, for example a synthetic identity ring whose members each also show a behaviourally suspicious sequence, is not addressed by either model.

## 6. Why NVIDIA owns both, and what that suggests

The Kumo acquisition reads less as a financial event than as a statement of direction. NVIDIA co-developed PRAGMA; four of the paper's authors are NVIDIA staff (Ostroukhov et al., [2026](https://arxiv.org/abs/2604.08649)), which gives the company direct exposure to the sequence paradigm. On 3 June 2026 it was reported to have acquired Kumo, at a value above 400 million US dollars and with official terms undisclosed (The Information, [2026](https://www.theinformation.com/articles/nvidia-buys-enterprise-model-maker-kumo-ai-least-400-million); Janakiram, [2026](https://www.forbes.com/sites/janakirammsv/2026/06/10/nvidia-kumo-ai-enterprise-data/)). That move brought in Kumo's founders, including Vanja Josifovski, formerly chief technology officer at Airbnb and Pinterest, Hema Raghavan, formerly an artificial intelligence lead at LinkedIn, and Jure Leskovec, the Stanford professor known for the GraphSAGE and node2vec lines of work and Kumo's chief scientist. One attribution is worth correcting, because it appears in some commentary: the PyTorch Geometric library that this ecosystem relies on was created by Matthias Fey and Jan Lenssen (Fey & Lenssen, [2019](https://arxiv.org/abs/1903.02428)), not by Leskovec; Fey is the lead author of KumoRFM and a co-author of KumoRFM-2. With the acquisition, the graph paradigm is in-house as well.

The move fits a clear pattern. Across 2024 to 2026, NVIDIA acquired [Run:ai](https://blogs.nvidia.com/blog/runai/) for orchestration, absorbed [Groq](https://www.cnbc.com/2025/12/24/nvidia-buying-ai-chip-startup-groq-for-about-20-billion-biggest-deal.html)'s inference technology and team in a large acqui-hire, acquired [Illumex](https://www.calcalistech.com/ctechnews/article/hkrcgl5dbx) for data semantics, and now Kumo for relational prediction. The throughline is not chips. It is ownership of the enterprise stack above the chip: orchestration, inference, data semantics, and now the model class that turns a company's relational database into predictions. Holding both a strong sequence model and a strong graph model is consistent with a bet that the two paradigms will need to live in one stack rather than remain separate products.

That this is a real bet, and not a single company's idiosyncrasy, is clearer once you notice that Google Research is independently pursuing graph foundation models on the same construction, reporting large gains on internal relational tasks (Galkin & Doguparty, [2025](https://research.google/blog/graph-foundation-models-for-relational-data/)). Two of the largest infrastructure companies are investing in the graph view of enterprise data at the same time. The reading in this section is inference from public acquisitions, author affiliations, and published research, not from any private information.

## 7. The open frontier: temporal-relational foundation models

The open problem can be stated directly. As of June 2026, no published model combines, in one architecture, per entity sequential modelling with fine grained temporal attention, the strength of PRAGMA, and cross entity relational inference, the strength of KumoRFM and the graph foundation models. The two approaches come close from opposite sides and miss in the middle. PRAGMA adds a static profile state branch, which is per user context rather than network structure. KumoRFM encodes timestamps on the graph, but does not run a sequence model over a customer's events. I will call the missing class temporal-relational foundation models. Figure 4 sketches what one might look like, and the dashed border is deliberate: it is a research direction, not a deployed system.

![Figure 4. A hypothetical unified architecture.](https://github.com/user-attachments/assets/47460731-a40f-47af-a152-b11bf970dc40)

*Figure 4. A proposed temporal-relational architecture, not a built system. Per entity sequence encoders produce embeddings that become node features in a relational layer; a cross attention layer fuses the sequence view with the graph view before task heads. This sketches what closing the upper right corner of Figure 3 would require. Source: author created and original.*

### 7.1 What the architecture would need to do

Concretely, such a model would compose the two paradigms rather than choose between them. For each entity $e$, a user, an account, or a merchant, with event history $H_e$, a sequence encoder would summarise its behaviour over time,

$$s_e = \mathrm{SeqEnc}_\theta(H_e) \in \mathbb{R}^d,$$

using temporal self attention in the manner of PRAGMA. These per entity summaries would become node features in the relational graph, and a relational layer would mix in cross entity structure,

$$g_e = \mathrm{RelLayer}_\phi\big(\lbrace s_{e'}\rbrace_{e'}, \mathcal{G}\big),$$

respecting the temporal constraint that a node attends only to its past. A fusion step would then combine the two views with cross attention, with the query taken from one view and the keys and values from the other,

$$z_e = \mathrm{softmax}\left(\frac{(W_Q s_e)(W_K g_e)^\top}{\sqrt{d}}\right)(W_V g_e),$$

so the joint representation $z_e$ can weigh what a customer did, in order, against who the customer is connected to. Pre-training would need an objective that supervises both halves at once,

$$\mathcal{L} = \mathcal{L}_{\mathrm{MLM}}(\theta) + \lambda \mathcal{L}_{\mathrm{graph}}(\phi),$$

where the first term is masked event reconstruction, as in PRAGMA, the second is a relational objective such as link prediction or node classification, as in relational deep learning, and $\lambda$ balances them.

### 7.2 Open questions

None of the following are settled, and each is a plausible direction for a focused paper.

First, joint pre-training. How should a per sequence reconstruction loss be balanced against a cross entity objective so that neither collapses the other, and does a curriculum, sequence first then graph, beat joint optimisation.

Second, training data. PRAGMA's corpus is one institution's ledger, while a graph that captures laundering across institutions would need data no single bank holds. Regulatory and privacy constraints on sharing data across institutions are a first order obstacle, not a footnote, and they may bound what is buildable outside a consortium or a privacy preserving setting such as federated training.

Third, querying. How would a declarative query language extend to temporal sequence predicates, for example selecting customers whose recent transaction pattern resembles known fraud and who also sit within two hops of a flagged account.

Fourth, scale and leakage. Composing sequence encoders with a relational layer over billions of events, without leaking future information and without an unacceptable compute cost, is not obvious.

Fifth, evaluation. There is no public benchmark that is at once sequence rich and graph rich for finance. Building one, for instance a graph with per node event sequences and real fraud labels, may be a prerequisite contribution in its own right. These are stated as hypotheses and open problems. The aim of this post is to argue that the corner is empty and worth occupying, not to claim that it has been occupied.

## 8. A peer review of PRAGMA

PRAGMA is a strong and useful paper. The tokenisation scheme is well designed, the multi scale masking is a sensible objective, the breadth of six tasks exceeds prior transaction ledger models, and the AML result is the kind of negative finding the field needs more of. Read as a reviewer, and as preparation for building on it, the following points are where I would push. Several are acknowledged by the authors, and together they outline the empirical questions a follow up should answer.

The central evaluation issue is that every result is relative, with absolutes withheld for commercial sensitivity. A reader cannot tell whether a 130% gain in PR-AUC on credit is a large jump from a low base or a modest one from a high base, nor how strong the baselines are. This is understandable commercially, but it limits verifiability and comparability, which is the first thing a venue would raise.

Related to this, the evaluation is on internal datasets with no external replication, and, the uplift study aside, the results are offline backtests rather than production tests. The baselines are also under characterised in architecture, feature set, and tuning budget; a foundation model beating an untuned tree is far less informative than beating a well tuned one. It is notable that the single place the baseline is described as strong and network aware, AML, is the single place the model loses. By contrast, nuFormer reports a production deployment outcome, a 4.4% churn reduction (Braithwaite et al., [2025](https://arxiv.org/abs/2507.23267)), which is a reminder that backtest gains and deployed gains can differ.

The AML result is best read as a class of limitations rather than one. By the authors' own argument the architecture cannot represent cross record structure, which bounds applicability for every network structured task, including collusion rings, synthetic identity fraud, and money mule networks. The paper frames it as a single limitation; it is closer to the boundary of the paradigm. The shallow profile state branch is the closest the model comes to context beyond a single customer, and it is static metadata, not network structure, so it cannot substitute for the graph view.

A few narrower points. Truncation is aggressive: very long histories are subsampled to the most recent events, and the heaviest users are often both the most valuable and the most relevant to fraud and AML, yet the effect of truncation on that tail is not measured. The tables report point estimates without standard deviations across seeds or runs, so statistical significance of the "outperforms" claims is hard to judge. Temporal generalisation is noted as a risk but not deeply stressed, which is the failure mode most likely to affect a deployed credit or fraud model. The optional text encoder helps credit but reduces recommendation quality and adds latency, so its gains appear narrow. The encoder and masked modelling design also forecloses generation and forecasting, which decoder approaches target (Braithwaite et al., [2025](https://arxiv.org/abs/2507.23267); Dou et al., [2025](https://arxiv.org/abs/2511.08939)); this is a scope choice, not a flaw, but it is worth stating. Finally, a credit scoring model built on learned embeddings raises fairness and explainability questions, such as adverse action reasoning and disparate impact, that the paper does not engage and that regulators care about.

The constructive reading is that the AML and profile state points converge on a single testable hypothesis: whether adding a cross entity graph layer on top of a sequential transaction encoder recovers the AML signal a pure sequence model misses. That is measurable today on public, graph structured fraud data such as the Elliptic Bitcoin dataset or the IEEE-CIS fraud dataset, against a simplified sequence only baseline. This post does not run that experiment. It argues why the experiment is worth running.

## 9. Limitations of this analysis

The limits of this post itself follow in the same spirit. PRAGMA's results are Revolut's own, relative, and largely backtested, and have not been reproduced outside Revolut. KumoRFM's strength on financial AML graphs is inferred from its design and from general benchmarks, not from a published financial AML benchmark, and the corresponding cell in Table 1 is marked as inferred. nuFormer is the only model discussed with a published production deployment number. The unified architecture in Figure 4 does not exist; it is a proposal, and the fusion and joint loss are one design point among several. The strategic reading of NVIDIA's acquisitions is inference from public sources, not inside information. Finally, this literature is young: PRAGMA and KumoRFM-2 are April 2026 preprints and the Kumo acquisition is June 2026, so numbers, venues, and even the claim that no unified model exists could be overtaken quickly. Treat the analysis as a June 2026 snapshot.

## 10. Conclusion

The argument was that PRAGMA and KumoRFM solve the same surface problem, replacing task specific models with a reusable representation, from opposite inductive biases, and that neither alone closes the gap. The evidence supports it. PRAGMA reads a customer as a sequence and is strong on behaviour over time, but its own Table 9 records a 47.1% drop in F0.5 on AML because it cannot represent cross record structure. KumoRFM and the graph foundation models read the enterprise as a graph and are strong on cross entity structure, but are not sequence models. The upper right corner of the coverage map, tasks that need both, is covered by neither today. NVIDIA now holds a model on each side of that corner, and Google is independently building on the graph side, which is at least consistent with the view that the corner matters. The open problem has a name, temporal-relational foundation models, and a shape. What it does not yet have is a model that fills it, or the experiments to show that one would help. That is the work that should come next.

## Appendix A: code and reproducibility

PRAGMA does not release code or data; the model and corpus are proprietary to Revolut, so independent replication is not currently possible (Ostroukhov et al., [2026](https://arxiv.org/abs/2604.08649)). KumoRFM is available through a public software development kit, with open benchmark scripts at [github.com/kumo-ai/kumo-rfm](https://github.com/kumo-ai/kumo-rfm) and an agent skill set at [github.com/kumo-ai/kumo-coding-agent](https://github.com/kumo-ai/kumo-coding-agent) (Hudovernik et al., [2026](https://arxiv.org/abs/2604.12596)). The relational deep learning foundations are open: RelBench is available at [relbench.stanford.edu](https://relbench.stanford.edu), and PyTorch Geometric, the underlying library, at [github.com/pyg-team/pytorch_geometric](https://github.com/pyg-team/pytorch_geometric) (Fey & Lenssen, [2019](https://arxiv.org/abs/1903.02428)). Google's graph foundation model is described in a research blog and is not, at the time of writing, released as a product, though its training stack uses the open JAX framework (Galkin & Doguparty, [2025](https://research.google/blog/graph-foundation-models-for-relational-data/)).

A reproducibility note on the claims in this post, since it analyses published work rather than original experiments. Hyperparameters and environment are reported for PRAGMA at the level of architecture, optimiser, and GPU counts, and for KumoRFM-2 at the level of benchmark protocol, context size, and data splits. Random seeds and run to run variance are not reported in PRAGMA's tables, which is the main reproducibility gap. Dataset details are public for KumoRFM-2's benchmarks and internal for PRAGMA. Code is open for KumoRFM and the relational tooling, and unavailable for PRAGMA.

## Appendix B: pre-publication checklist

Standalone abstract under 150 words: yes. At least three figures with captions and alt text: yes, four figures and a summary table. No long section without a visual or equation: yes. Jargon defined on first use, including attention, masked modelling, rotary position embeddings, message passing, in-context learning, and the F-beta measure: yes. Limitations and open questions present, and related work covered across academia and industry: yes. Negative result reported, the PRAGMA AML finding, rather than omitted: yes. Numbers checked against primary sources, with the event count corrected to 24 billion, the SALT and RelBench gains taken from the KumoRFM-2 paper, the PyTorch Geometric attribution corrected, and unverified figures dropped: yes. Citations in author date form with links to sources: yes.

## References

Bommasani, R., et al. (2021). *On the opportunities and risks of foundation models.* arXiv. [https://arxiv.org/abs/2108.07258](https://arxiv.org/abs/2108.07258)

Braithwaite, D., et al. (2025). *Your spending needs attention: Modeling financial habits with transformers.* arXiv. [https://arxiv.org/abs/2507.23267](https://arxiv.org/abs/2507.23267)

Brown, T., et al. (2020). *Language models are few-shot learners.* arXiv. [https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)

Dao, T., et al. (2022). *FlashAttention: Fast and memory-efficient exact attention with IO-awareness.* arXiv. [https://arxiv.org/abs/2205.14135](https://arxiv.org/abs/2205.14135)

Devlin, J., et al. (2019). *BERT: Pre-training of deep bidirectional transformers for language understanding.* arXiv. [https://arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805)

Dou, Y., et al. (2025). *TransactionGPT.* arXiv. [https://arxiv.org/abs/2511.08939](https://arxiv.org/abs/2511.08939)

Dwivedi, V. P., Jaladi, S., Shen, Y., López, F., Kanatsoulis, C. I., Puri, R., Fey, M., & Leskovec, J. (2025). *Relational graph transformer.* arXiv. [https://arxiv.org/abs/2505.10960](https://arxiv.org/abs/2505.10960)

Fey, M., & Lenssen, J. E. (2019). *Fast graph representation learning with PyTorch Geometric.* arXiv. [https://arxiv.org/abs/1903.02428](https://arxiv.org/abs/1903.02428)

Fey, M., et al. (2024). *Relational deep learning: Graph representation learning on relational databases.* RelBench. [https://relbench.stanford.edu](https://relbench.stanford.edu)

Fey, M., et al. (2025). *KumoRFM: A foundation model for in-context learning on relational data.* Kumo. [https://kumo.ai/company/news/kumo-relational-foundation-model/](https://kumo.ai/company/news/kumo-relational-foundation-model/)

Galkin, M., & Doguparty, P. (2025, July 10). *Graph foundation models for relational data.* Google Research Blog. [https://research.google/blog/graph-foundation-models-for-relational-data/](https://research.google/blog/graph-foundation-models-for-relational-data/)

Gilmer, J., et al. (2017). *Neural message passing for quantum chemistry.* arXiv. [https://arxiv.org/abs/1704.01212](https://arxiv.org/abs/1704.01212)

Gu, J., Ranjan, R., Kanatsoulis, C., Tang, H., Jurkovic, M., Hudovernik, V., Znidar, M., Chaturvedi, P., Shroff, P., Li, F., & Leskovec, J. (2026). *RelBench v2: A large-scale benchmark and repository for relational data.* arXiv. [https://arxiv.org/abs/2602.12606](https://arxiv.org/abs/2602.12606)

Hamilton, W. L., Ying, R., & Leskovec, J. (2017). *Inductive representation learning on large graphs.* arXiv. [https://arxiv.org/abs/1706.02216](https://arxiv.org/abs/1706.02216)

Hollmann, N., et al. (2023). *TabPFN: A transformer that solves small tabular classification problems in a second.* arXiv. [https://arxiv.org/abs/2207.01848](https://arxiv.org/abs/2207.01848)

Hu, E. J., et al. (2022). *LoRA: Low-rank adaptation of large language models.* arXiv. [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)

Hudovernik, V., et al. (2026). *KumoRFM-2: Scaling foundation models for relational learning.* arXiv. [https://arxiv.org/abs/2604.12596](https://arxiv.org/abs/2604.12596)

Janakiram, M. S. V. (2026, June 10). *Nvidia buys Kumo AI to bring AI predictions to business data.* Forbes. [https://www.forbes.com/sites/janakirammsv/2026/06/10/nvidia-kumo-ai-enterprise-data/](https://www.forbes.com/sites/janakirammsv/2026/06/10/nvidia-kumo-ai-enterprise-data/)

Kocijan, V., et al. (2026). *Predictive Query Language: A domain-specific language for predictive modeling on relational databases.* arXiv. [https://arxiv.org/abs/2602.09572](https://arxiv.org/abs/2602.09572)

Nebius. (2026). *Revolut on the inference frontier.* Nebius. [https://nebius.com/customer-stories/revolut](https://nebius.com/customer-stories/revolut)

Ostroukhov, M., et al. (2026). *PRAGMA: Revolut foundation model.* arXiv. [https://arxiv.org/abs/2604.08649](https://arxiv.org/abs/2604.08649)

Ranjan, R., Hudovernik, V., Znidar, M., Kanatsoulis, C., Upendra, R., Mohammadi, M., Meyer, J., Palczewski, T., Guestrin, C., & Leskovec, J. (2025). *Relational transformer: Toward zero-shot foundation models for relational data.* arXiv. [https://arxiv.org/abs/2510.06377](https://arxiv.org/abs/2510.06377)

Robinson, J., Ranjan, R., Hu, W., Huang, K., Han, J., Dobles, A., Fey, M., Lenssen, J. E., Yuan, Y., Zhang, Z., He, X., & Leskovec, J. (2024). *RelBench: A benchmark for deep learning on relational databases.* arXiv. [https://arxiv.org/abs/2407.20060](https://arxiv.org/abs/2407.20060)

Su, J., et al. (2024). *RoFormer: Enhanced transformer with rotary position embedding.* arXiv. [https://arxiv.org/abs/2104.09864](https://arxiv.org/abs/2104.09864)

The Information. (2026, June 3). *Nvidia buys enterprise model-maker Kumo AI for at least $400 million.* [https://www.theinformation.com/articles/nvidia-buys-enterprise-model-maker-kumo-ai-least-400-million](https://www.theinformation.com/articles/nvidia-buys-enterprise-model-maker-kumo-ai-least-400-million)

Vaswani, A., et al. (2017). *Attention is all you need.* arXiv. [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)

Wang, Y., Wang, X., Gan, Q., Wang, M., Yang, Q., Wipf, D., & Zhang, M. (2025). *Griffin: Towards a graph-centric relational database foundation model* [Conference paper]. ICML 2025. arXiv. [https://arxiv.org/abs/2505.05568](https://arxiv.org/abs/2505.05568)

Wu, S., et al. (2023). *BloombergGPT: A large language model for finance.* arXiv. [https://arxiv.org/abs/2303.17564](https://arxiv.org/abs/2303.17564)

---

*Series: Architecture Deep Dives. This post is a public notebook: it maps the landscape and names an open problem, and it makes no claim to have solved that problem. The experiments and the paper come next.*
