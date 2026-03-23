# Diabetics Assistant RAG (Nalam) — Base Repository

This repository is the **standalone Python backend** for a diabetes-focused retrieval-augmented generation (RAG) assistant (“Nalam”). It combines **ChromaDB** vector search, **Google Gemini** for generation, and optional **risk analysis** from structured user vitals.

The **full integrated experience** (UI, auth, persistence, and wiring to your production models) lives in the **SmartPlate web application**. Treat this repo as the **reference / portable RAG core** you can run locally or embed in other services.

---

## What this codebase does

| Piece | Role |
|--------|------|
| **Knowledge ingestion** | JSON documents are chunked (where needed), embedded with `sentence-transformers` (`all-MiniLM-L6-v2`), and stored in **ChromaDB** under `./nalam_chroma_db`. |
| **Retrieval** | `NalamRetriever` queries the collection for top-k passages matching the user question. |
| **Generation** | `NalamGenerator` calls **Gemini** with retrieved context plus optional structured inputs (risk profile, macros, food suggestions). |
| **Risk analysis** | `RiskAnalyzer` scores clinical/lifestyle signals from a `UserProfile` when enough medical fields are present. |

---

## Production vs this base repo (important)

- **Macro targets (`macro_engine.py`)**  
  In this repo, macros are **fixed mock values** for easy testing. In **SmartPlate**, you will pass a real **user profile** and obtain targets from your **LightGBM** (or equivalent) macro model.

- **Food recommendations (`food_recommendations.py`)**  
  The function `mock_food_recommendation()` returns **sample meal ideas** for development. In **SmartPlate**, replace this with your **hybrid KNN–based food recommendation** output so the generator receives real candidates and nutrition breakdowns.

- **User profiles**  
  `main.py` uses **mock profiles** (`get_mock_user`) for CLI demos. Production should build `UserProfile` from your stored user / medical data.

---

## Quick start

### 1. Prerequisites

- **Python 3.10+**
- A **Google AI (Gemini) API key** (`GOOGLE_API_KEY` in `.env`)
- Optional: **GPU** not required; embeddings run on CPU by default via `sentence-transformers`

### 2. Clone and install

```bash
cd DiabeticsAssistantRAG-Nalam
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment

Create a `.env` file in the **project root** (same folder as `config.py`):

```env
GOOGLE_API_KEY=your_gemini_api_key_here
PORT=5000
```

`config.py` loads variables **from this file**; a missing `.env` will raise at import time.

### 4. Knowledge base (ChromaDB) — expect a long run

Ingestion reads **`nalam_data.json`** (array of document records) and writes vectors to **`./nalam_chroma_db`**.

```bash
python data_ingestion.py
```

**Time expectation:** With roughly **~23k document chunks** in the corpus, **injecting / embedding into Chroma often takes about 10–15 minutes** (CPU, disk, and batch size affect this). Let the process finish; interrupting it may leave an incomplete index.

If the Chroma collection is empty on first use, `NalamRetriever` can **auto-run** ingestion when `nalam_data.json` exists (see `nalam_retriever.py`).

### 5. Run the assistant

**Interactive CLI** (mock user + mock macros + mock food in food mode):

```bash
python main.py
```

**Startup delay:** The first time you run `main.py`, loading the embedding model and attaching to the knowledge base can take roughly **30–40 seconds** before the prompt lets you type a question. Later runs are usually faster if models are cached.

**HTTP API** (FastAPI):

```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```

---

## What to ask (CLI modes)

- **`normal` (default)** — Use for **general diabetes / FYP-style** questions: **nutrition**, **recipes**, **exercise**, **lifestyle**, meal ideas explained in context, and other educational topics. The retriever pulls from the knowledge base and combines with your (mock) profile and risk analysis when available.

- **`food_recommendation`** — Use when you want a **concrete “what can I eat now?”** style answer tied to a **meal slot** (breakfast / lunch / snacks / dinner). This path uses **mock** meal candidates and macro splits; in SmartPlate you will swap in your hybrid KNN output.

---

## Example CLI session

```text
✅ [Retriever] Connected to collection: nalam_knowledge

📋 --- PATIENT PROFILE SELECTION ---
1. Case A: High Risk (Uncontrolled Diabetes, Kidney Issues)
2. Case B: Well Controlled (Healthy)
3. No medical profile (skip RiskAnalyzer)
Select User Profile (1/2/3): 1

🥗 --- NALAM RAG READY --- 🥗
(Type 'quit' to exit)

Mode (normal/food_recommendation) [normal]: normal

👤 You: how make biriyani in healthier way based on my health condition?
🔍 [Retriever] Searching for: 'how make biriyani in healthier way based on my health condition?'
📄 [Retriever] Retrieved 5 chunks.
✅ [Retriever] 3 unique chunks after filtering.

🤖 Nalam: Biryani can be made healthier by making a few smart swaps, especially considering your moderate glycemic and obesity risks...
--------------------------------------------------

Mode (normal/food_recommendation) [normal]: food_recommendation
Meal type (breakfast/lunch/snacks/dinner): breakfast

👤 You: what i can eat now

🤖 Nalam: For your breakfast right now, you can have:

**Kambu (pearl millet) koozh + sundal (1 bowl)**

This is a very good choice for you, especially since you have diabetes...
--------------------------------------------------
```

---

## Repository layout (folders and key files)

| Path | Purpose |
|------|---------|
| **`documentsCreator/`** | **Document pipeline**: turn raw files + URLs into standardized JSON for RAG. See [Document pipeline](#document-pipeline-documentscreator) below. |
| **`documentsCreator/data/raw/`** | **Unprocessed inputs** — place PDFs, CSVs, `.txt`, structured `.json`, and `web/urls.txt` here. |
| **`documentsCreator/data/processed/json_documents/`** | **Builder output** — JSON arrays of `{ doc_id, source_type, title, content, ... }` produced by the builder. |
| **`documentsCreator/data/processed/processed_sources.json`** | **Registry of already-processed sources** (file paths and/or URLs). Anything **not** listed here will be read and merged on the next build; listed items are **skipped** so you do not duplicate work. |
| **`documentsCreator/loaders/`** | Pluggable loaders: `web_loader` (crawl), `pdf_loader`, `csv_loader`, `txt_loader`, `json_loader`. |
| **`nalam_data.json`** | **Canonical ingestion file** for `data_ingestion.py` / retriever auto-ingest — same schema as builder output (list of records). Often populated by **merging** outputs from `documentsCreator`. |
| **`nalam_chroma_db/`** | Persistent **ChromaDB** store (created after ingestion). You can regenerate it from `nalam_data.json`; omit from version control if the bundle is large. |
| **`data_ingestion.py`** | Chunks text (web), keeps CSV rows atomic, upserts into Chroma. |
| **`nalam_retriever.py`** | Vector search over `nalam_knowledge`. |
| **`nalam_generator.py`** | Gemini prompts with context + structured JSON. |
| **`nalam_risk_engine.py`** | `UserProfile` + `RiskAnalyzer` rules. |
| **`macro_engine.py`** | **Mock** daily/meal macro targets (replace in SmartPlate with LightGBM outputs). |
| **`food_recommendations.py`** | **`mock_food_recommendation()`** — placeholder meals (replace with hybrid KNN recommender in production). |
| **`main.py`** | CLI entry: mock profiles, retrieval + generation. |
| **`app.py`** | FastAPI service mirroring the same concepts for HTTP clients. |
| **`config.py`** | Loads `.env` (`GOOGLE_API_KEY`, `PORT`). |
| **`inspect_chroma_db.py`** | Optional utility to dump/stats from Chroma (may need `numpy` if not already installed). |
| **`evaluation_dataset_v2.json`** | Evaluation / test prompts (if you run offline eval). |
| **`Dockerfile`** | Optional container build for deployment (not required for local development). |

---

## Document pipeline (`documentsCreator`)

Use this module when you want to **add or refresh knowledge** without hand-writing `nalam_data.json`.

### How it works

1. **Add raw data** under `documentsCreator/data/raw/`:
   - `web/urls.txt` — one URL per line (sites are crawled per the web loader).
   - `pdf/`, `csv/`, `text/`, `json/` — drop files as needed.

2. **Registry** — `documentsCreator/data/processed/processed_sources.json` stores **which sources were already converted**. On each run, the builder **skips** those paths/URLs and only processes **new** files or URLs.

3. **Build** standardized JSON:

   ```bash
   cd documentsCreator
   pip install requests beautifulsoup4 pypdf
   python build_json_documents.py --output-filename standard_documents.json
   ```

   Output path: `documentsCreator/data/processed/json_documents/standard_documents.json`.

4. **Feed the RAG** — merge the JSON array into **`nalam_data.json`** at the repo root (append or replace, depending on whether you are doing a full rebuild). Then re-run:

   ```bash
   cd ..
   python data_ingestion.py
   ```

   After updating the corpus, budget **~10–15 minutes** again for full re-embedding if the document count is on the order of tens of thousands of chunks.

### Notes for collaborators

- If you **clone on a new machine**, `processed_sources.json` may contain **absolute paths from another computer**. Either delete entries you want to re-ingest, or reset the file, so new paths are registered correctly.
- Web crawling depends on **network access** and site policies; failures for a URL are skipped or logged by the builder.
- Extra dependencies for the builder are **`requests`**, **`beautifulsoup4`**, and **`pypdf`** (not all are in the root `requirements.txt` by default).

---

## Embedding model and API

- **Embeddings:** `all-MiniLM-L6-v2` via Chroma’s `SentenceTransformerEmbeddingFunction` (downloads on first use).
- **LLM:** Google **Gemini** (`gemini-2.5-flash` default in `nalam_generator.py`).

---

## Modes (CLI / API)

- **`normal`** — Retrieves from Chroma, optionally runs risk analysis when medical fields are complete, injects macro **mock** structure into the prompt. Best for **nutrition, recipes, exercise, lifestyle**, and broad diabetes education.
- **`food_recommendation`** — Uses **mock** meal suggestions and meal-level macro split; use when you want **meal-slot “what should I eat?”** behavior. Wire your **LightGBM** and **hybrid KNN** outputs into the same structured fields in SmartPlate.

---

## Relationship to SmartPlate

| This repo | SmartPlate web app |
|-----------|---------------------|
| Base RAG, CLI, optional FastAPI | Full stack: UI, user sessions, real profiles |
| Mock macros / mock food | LightGBM macros + KNN (or hybrid) food ranking |
| Portable core for sharing | End-to-end product |

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| `FileNotFoundError` for `.env` | Add `.env` next to `config.py` with `GOOGLE_API_KEY`. |
| Empty or missing Chroma | Ensure `nalam_data.json` exists and run `python data_ingestion.py`. |
| Ingestion seems stuck | Large corpora (~23k chunks) can take **10–15 minutes**; wait for completion. |
| `main.py` slow to start | First load can take **30–40 seconds** (models + DB); later runs are faster. |
| First run slow | `sentence-transformers` / model download; subsequent runs are faster. |
| Document builder import errors | From `documentsCreator`, run `pip install requests beautifulsoup4 pypdf`. |

---

## License / usage

Confirm licensing for any **third-party text, PDFs, or crawled web content** before redistributing or deploying. This README describes the software pipeline only.

---

## Summary

1. Put secrets in **`.env`**, install **`requirements.txt`**, ingest **`nalam_data.json`** into Chroma (allow **~10–15 minutes** for large ~23k-chunk corpora).  
2. Use **`documentsCreator`** to grow the corpus; **`processed_sources.json`** avoids duplicate processing.  
3. Run **`python main.py`** and expect **~30–40 seconds** before chatting on a cold start. Use **`normal`** for general topics; **`food_recommendation`** for meal-specific “what can I eat?” flows.  
4. Replace **`macro_engine`** and **`mock_food_recommendation`** in **SmartPlate** with your **LightGBM** and **hybrid KNN** stack while keeping the same RAG shell.

For questions about the **integrated** app behavior, refer to the **SmartPlate web** codebase; this repo is the **shared RAG foundation**.
