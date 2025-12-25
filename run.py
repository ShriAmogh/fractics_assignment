import json
from rag.search import hybrid_search
from agents.controller import AgenticController

TOP_K = 5

controller = AgenticController()

print("\n🔎 Hybrid RAG + Agentic Summary System (Ctrl+C to exit)")

while True:
    try:

        query = input("\nEnter your research query: ").strip()
        if not query:
            print(" Query cannot be empty")
            continue

        date_filter = input(
            "Filter papers published AFTER (YYYY-MM-DD) or press Enter to skip: "
        ).strip()
        date_filter = date_filter if date_filter else None

        results = hybrid_search(query, date_filter, TOP_K)

        if not results["documents"][0]:
            print("No results found.")
            continue

        # Take the top result
        first_doc = results["documents"][0][0]
        meta = results["metadatas"][0][0]

        print("\nTop Retrieved Paper")
        print("-" * 60)
        print(f"Title          : {meta['title']}")
        print(f"Paper ID       : {meta['paper_id']}")
        print(f"Submission Date: {meta['submission_date']}")
        print(f"Authors        : {meta['authors']}")
        print("-" * 60)
        print(f"Snippet:\n{first_doc[:300].replace('\\n', ' ')}...")
        print("-" * 60)

        print("\n Running Agentic JSON-Correction Loop...")
        structured_summary = controller.run(first_doc)

        print("\n FINAL STRUCTURED SUMMARY (Validated JSON)")
        print("=" * 60)
        print(json.dumps(structured_summary, indent=2))
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n Key interuption -------------")
        break

    except Exception as e:
        print("❌ Error:", e)
