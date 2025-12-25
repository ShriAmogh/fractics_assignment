**Pahse 1 : Data Scraping**
scraper/scraper.py

This script scrapes 50 academic research papers and stores them in a structured JSON format.

Output

data/cscl_dataset.json

Each paper includes:

paper_id

title

abstract

authors

submission_date

content

refrences

RUN : 
python scraper/scraper.py

**Phase 2: Data Ingestion & Vectorization**
data_ingestion/ingestion.py

This script:

Loads the scraped JSON dataset

Chunks long papers

Generates embeddings using sentence-transformers

Stores vectors in ChromaDB (persistent) with their metadata attached for hard constraints filtering.

Key Features

Chunking with overlap

Deterministic chunk IDs

Metadata preservation

Persistent storage

Output

Embedded vectors stored in chroma_store/

Run
python data_ingestion/ingestion.py

**Phase 3: Hybrid RAG + Agentic Workflow**
run.py

This is the main execution entrypoint.

What it does:

Accepts a research query

Performs semantic search using ChromaDB

Retrieves the most relevant paper

Runs an agentic self-correction workflow to generate a validated summary

Run
python run.py

Agentic Workflow (Core Innovation)

The agentic system ensures structured, reliable outputs using multiple cooperating agents.

AgenticController (Orchestrator)
agents/controller.py

The controller:

Orchestrates agent interactions

Enforces retry logic

Feeds validation errors back to the generator

Terminates safely after 3 failed attempts

Responsibilities

Retry loop (max 3 attempts)

Error propagation

Final success/failure decision

JSONCreatorAgent (Generator)
 agents/json_creator.py

Uses Google Gemini (google-genai) to generate a structured JSON summary.

Output Schema
{
  "title": "string",
  "summary": "string",
  "complexity_score": 1-10,
  "future_work": "string"
}

Constraints

JSON only

No markdown

No explanations

 ValidatorAgent (Verifier)
 agents/validator.py

Validates LLM output using:

json.loads (syntax validation)

Pydantic schema enforcement

Failure Handling

Missing fields

Wrong data types

Invalid ranges

Empty responses

Errors are fed back to the generator for self-correction.

Schema Definition
agents/schema.py
class PaperSummary(BaseModel):
    title: str
    summary: str
    complexity_score: int = Field(ge=1, le=10)
    future_work: str

Self-Correction Loop
Attempt 1 → Generate JSON → Validate → Fail
          ↓
Error Feedback → Generate Again → Validate → Success


If all 3 attempts fail → graceful termination with error.
