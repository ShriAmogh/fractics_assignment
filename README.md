**Phase 1: Data Scraping** --> Location: scraper/scraper.py

Description

    Scrapes 50 academic research papers

    Stores results in a structured JSON format

Output

    data/cscl_dataset.json

Each paper includes:

    paper_id

    title

    abstract

    authors

    submission_date

    content

    references

Run
    python scraper/scraper.py

**Phase 2: Data Ingestion & Vectorization** --. Location: data_ingestion/ingestion.py

Description

    Loads the scraped JSON dataset

    Splits long papers into overlapping chunks

    Generates embeddings using sentence-transformers

    Stores vectors in ChromaDB with metadata attached for filtering

Key Features

    Chunking with overlap

    Deterministic chunk IDs

    Metadata preservation

    Persistent vector storage

Output

    Embedded vectors stored in chroma_store/

Run
    python data_ingestion/ingestion.py

**Phase 3: Hybrid RAG with Cross-Encoder and Agentic Workflow** --> Location: run.py

Description

    Main execution entrypoint

    Combines dense retrieval, neural re-ranking, and agentic reasoning

    Retrieval Pipeline (Updated)
    Step 1: Vector Retrieval (Bi-Encoder)

    User query is embedded using all-MiniLM-L6-v2

    Cosine similarity search is performed in ChromaDB

    Top VECTOR_TOP_K = 20 candidate chunks are retrieved

    This step prioritizes recall and speed

    Step 2: Cross-Encoder Re-Ranking

    Retrieved 20 candidate chunks are re-ranked using:

    cross-encoder/ms-marco-MiniLM-L-6-v2

    Each candidate is scored jointly with the query

    Candidates are sorted by relevance score

    Low-confidence results are discarded using a threshold

    Final top results are selected for downstream processing


**Agentic Workflow**

    Once the best paper chunk is selected, the system enters an agentic self-correction loop to ensure reliable structured output.

    AgenticController (Orchestrator)

    Location: agents/controller.py

Responsibilities

    Coordinates multiple agents

    Controls retry logic (maximum 3 attempts)

    Feeds validation errors back to the generator

    Terminates safely on repeated failure

    JSONCreatorAgent (Generator)

    Location: agents/json_creator.py

Description

    Uses Google Gemini (google-genai)

    Generates a structured JSON summary of the retrieved paper

Output Schema
    {
      "title": "string",
      "summary": "string",
      "complexity_score": 1-10,
      "future_work": "string"
    }

    Constraints

    JSON output only

    No markdown

    No explanations or additional text

    ValidatorAgent (Verifier)

    Location: agents/validator.py

Validation Steps

    Syntax validation using json.loads

    Schema enforcement using Pydantic

    Failure Handling

    Missing fields

    Incorrect data types

    Invalid value ranges

    Empty or malformed responses

    Validation errors are automatically fed back to the generator

    Schema Definition

    Location: agents/schema.py

class PaperSummary(BaseModel):
    title: str
    summary: str
    complexity_score: int = Field(ge=1, le=10)
    future_work: str

Self-Correction Loop

Attempt 1

    Generate structured JSON

    Validate output

    Failure detected

    Validation error passed back to generator

    Retry up to 3 times

    On success: return validated JSON

After 3 failures: graceful termination with error

End-to-End Workflow Summary

    Scrape academic papers

    Ingest and embed content into ChromaDB

    Accept user query

    Perform cosine similarity search (Top 20)

    Re-rank results using cross-encoder

    Select best candidate

    Run agentic self-correction workflow

    Output validated structured summary