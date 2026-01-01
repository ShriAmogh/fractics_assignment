import json
from rag.search import hybrid_search
from agents.controller import AgenticController

TOP_K = 5

controller = AgenticController()

print("\nHybrid RAG + Agentic Summary System")

while True:
    try:
        query = input("\nEnter your research query: ").strip()
        if not query:
            print("Query cannot be empty")
            continue

        date_filter = input(
            "Filter papers published AFTER (YYYY-MM-DD) or press Enter to skip: "
        ).strip()
        date_filter = date_filter if date_filter else None

        # ---- Hybrid Retrieval ----
        results = hybrid_search(query, date_filter, TOP_K)

        if not results:
            print("No results found.")
            continue

        # ---- Take top reranked result ----
        top_result = results[0]

        first_doc = top_result["document"]
        meta = top_result["metadata"]

        print("\nTop Retrieved Paper")
        print("-" * 60)
        print(f"Title          : {meta['title']}")
        print(f"Paper ID       : {meta['paper_id']}")
        print(f"Submission Date: {meta['submission_date']}")
        print(f"Authors        : {meta['authors']}")
        print("-" * 60)
        print(f"Snippet:\n{first_doc[:300].replace('\\n', ' ')}...")
        print("-" * 60)

        print("\nRunning Agentic JSON-Correction Loop...")
        structured_summary = controller.run(first_doc)

        print("\nFINAL STRUCTURED SUMMARY (Validated JSON)")
        print("=" * 60)
        print(json.dumps(structured_summary, indent=2))
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nKey interruption — exiting system.")
        break

    except Exception as e:
        print("Error:", e)
