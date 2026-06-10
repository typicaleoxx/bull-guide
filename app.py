import os

import gradio as gr
from dotenv import load_dotenv

from pipeline import ask

load_dotenv()


def handle_query(question):
    question = question.strip()
    if not question:
        return "", "", ""

    # surface a clear message when the api key is not configured
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        msg = "GROQ_API_KEY is not set. Copy .env.example to .env and add your Groq key."
        return msg, "", ""

    try:
        result = ask(question)
    except Exception as exc:
        return f"Error: {exc}", "", ""

    answer = result["answer"]

    sources_text = "\n".join(f"- {s}" for s in result["sources"])

    # show each retrieved chunk with its source and similarity distance
    evidence_parts = []
    for i, chunk in enumerate(result["retrieved_chunks"], start=1):
        header = f"[{i}] {chunk['source']}  (distance: {chunk['distance']:.4f})"
        body = chunk["text"][:400]
        evidence_parts.append(f"{header}\n{body}")
    evidence_text = "\n\n".join(evidence_parts)

    return answer, sources_text, evidence_text


EXAMPLES = [
    "What do students find difficult about Data Structures?",
    "How should students prepare for Computer Logic exams?",
    "What problems happen during software engineering group projects?",
    "Which parking garage is best for biology students?",
]

with gr.Blocks(title="Bull Guide") as demo:
    gr.Markdown(
        "# Bull Guide\n"
        "An unofficial computer science course guide -- ask about course difficulty, "
        "exams, study habits, group projects, and registration."
    )

    question_box = gr.Textbox(
        label="Question",
        placeholder="Ask about CS courses, exams, group projects, or registration...",
        lines=2,
    )

    ask_btn = gr.Button("Ask")

    answer_out = gr.Textbox(label="Answer", lines=8, interactive=False)
    sources_out = gr.Textbox(label="Sources", lines=4, interactive=False)
    evidence_out = gr.Textbox(label="Retrieved Evidence", lines=14, interactive=False)

    gr.Examples(examples=EXAMPLES, inputs=[question_box])

    # submit on button click or Enter key
    ask_btn.click(
        fn=handle_query,
        inputs=[question_box],
        outputs=[answer_out, sources_out, evidence_out],
    )
    question_box.submit(
        fn=handle_query,
        inputs=[question_box],
        outputs=[answer_out, sources_out, evidence_out],
    )

if __name__ == "__main__":
    demo.launch()
