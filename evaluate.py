import json
import os
from pathlib import Path

from dotenv import load_dotenv

from pipeline import ask

load_dotenv()

# five test questions aligned with the current document set.
# question 5 is unsupported to verify the refusal behavior.
EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": "What do students find difficult about Data Structures?",
        "expected": (
            "Students struggle with recursion (tracing calls), pointers and references "
            "in linked structures, and understanding which structure is most appropriate "
            "for a given situation."
        ),
    },
    {
        "id": 2,
        "question": "What do students recommend for preparing for Computer Logic exams?",
        "expected": (
            "Students recommend practicing complete problems that move from a verbal "
            "requirement to a truth table, a simplified Boolean expression, and a circuit "
            "diagram. Rereading lecture notes alone is not enough."
        ),
    },
    {
        "id": 3,
        "question": "What problems commonly occur during software engineering group projects?",
        "expected": (
            "Common problems include coordination failures, uneven workloads, integration "
            "errors when team members work on separate branches without agreeing on "
            "interfaces, and scope creep where optional features take priority over "
            "required functionality."
        ),
    },
    {
        "id": 4,
        "question": "What advice do students give for balancing coursework with an internship?",
        "expected": (
            "Students recommend avoiding multiple project-heavy courses in the same "
            "semester, using weekly time blocks to protect study time, starting assignments "
            "early to absorb unexpected work tasks, and communicating scheduling needs "
            "to supervisors and classmates in advance."
        ),
    },
    {
        "id": 5,
        "question": "Which parking garage is best for biology students?",
        "expected": (
            "The available documents do not provide enough information to answer this question."
        ),
    },
]


def run_evaluation():
    results = []

    for item in EVAL_QUESTIONS:
        q = item["question"]
        print(f"\n[{item['id']}] {q}")

        try:
            result = ask(q)
            answer = result["answer"]
            sources = result["sources"]
            chunks = result["retrieved_chunks"]
            error = None
        except Exception as exc:
            answer = f"ERROR: {exc}"
            sources = []
            chunks = []
            error = str(exc)

        print(f"  answer:  {answer[:200]}")
        print(f"  sources: {sources}")

        results.append({
            "id": item["id"],
            "question": q,
            "expected": item["expected"],
            "answer": answer,
            "sources": sources,
            "error": error,
            "retrieved_chunks": [
                {
                    "source": c["source"],
                    "distance": c["distance"],
                    "text_preview": c["text"][:250],
                }
                for c in chunks
            ],
        })

    # save results under evaluation/
    out_dir = Path("evaluation")
    out_dir.mkdir(exist_ok=True)

    json_path = out_dir / "results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    txt_path = out_dir / "results.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Bull Guide Evaluation Results\n")
        f.write("=" * 70 + "\n\n")
        for r in results:
            f.write(f"[{r['id']}] {r['question']}\n\n")
            f.write(f"Expected:\n  {r['expected']}\n\n")
            f.write(f"System answer:\n  {r['answer']}\n\n")
            f.write(f"Sources: {', '.join(r['sources']) if r['sources'] else 'none'}\n\n")
            if r["retrieved_chunks"]:
                top = r["retrieved_chunks"][0]
                f.write(
                    f"Top retrieved chunk: {top['source']} "
                    f"(distance: {top['distance']:.4f})\n"
                )
                f.write(f"  {top['text_preview'][:200]}\n\n")
            if r["error"]:
                f.write(f"Error: {r['error']}\n\n")
            f.write("-" * 70 + "\n\n")

    print(f"\nresults saved to {json_path} and {txt_path}")
    return results


if __name__ == "__main__":
    run_evaluation()
