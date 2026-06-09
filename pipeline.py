import json
import os
import re
from pathlib import Path

RAW_DIR = "documents/raw"
CLEANED_DIR = "documents/cleaned"
CHUNKS_FILE = "data/chunks.json"

CHUNK_TARGET = 700
CHUNK_MAX = 1000
CHUNK_OVERLAP = 120


def load_documents(raw_dir):
    docs = []
    for path in sorted(Path(raw_dir).glob("*.txt")):
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        docs.append({"filename": path.name, "raw": raw})
    return docs


def parse_metadata(raw_text):
    """
    read title, source, and topic from the first three header lines.
    everything after the first blank line following the headers is the body.
    """
    lines = raw_text.strip().splitlines()
    meta = {}
    body_start = len(lines)

    for i, line in enumerate(lines):
        if line.startswith("title:"):
            meta["title"] = line[len("title:"):].strip()
        elif line.startswith("source:"):
            meta["source"] = line[len("source:"):].strip()
        elif line.startswith("topic:"):
            meta["topic"] = line[len("topic:"):].strip()
        # first blank line after we have all three fields marks the body
        if i > 2 and line.strip() == "":
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:])
    return meta, body


def clean_text(text):
    # collapse repeated spaces and tabs to a single space
    text = re.sub(r"[ \t]+", " ", text)
    # collapse three or more consecutive blank lines to two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def save_cleaned(filename, meta, body, cleaned_dir):
    Path(cleaned_dir).mkdir(parents=True, exist_ok=True)
    content = (
        f"title: {meta.get('title', '')}\n"
        f"source: {meta.get('source', '')}\n"
        f"topic: {meta.get('topic', '')}\n"
        f"\n{body}\n"
    )
    with open(os.path.join(cleaned_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)


def chunk_text(text, target=CHUNK_TARGET, max_size=CHUNK_MAX, overlap=CHUNK_OVERLAP):
    """
    paragraph-aware chunking: always close a chunk at a paragraph boundary.
    accumulate paragraphs until the chunk reaches target length.
    if the next paragraph would push the chunk past max_size, flush first.
    prepend the last `overlap` characters of each closed chunk to the next one.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if not paragraphs:
        return []

    chunks = []
    current = []
    current_len = 0
    tail = ""

    for para in paragraphs:
        # seed new chunk with overlap tail from previous chunk
        if not current and tail:
            current = [tail]
            current_len = len(tail)

        # cost of appending this paragraph (separator counts as 2 chars)
        cost = (2 + len(para)) if current else len(para)

        # if adding would exceed max, close the current chunk first
        if current and current_len + cost > max_size:
            chunk = "\n\n".join(current)
            chunks.append(chunk)
            tail = chunk[-overlap:] if len(chunk) > overlap else chunk
            current = [tail, para]
            current_len = len(tail) + 2 + len(para)
        else:
            current.append(para)
            current_len += cost

        # close chunk once it reaches the target length
        if current_len >= target:
            chunk = "\n\n".join(current)
            chunks.append(chunk)
            tail = chunk[-overlap:] if len(chunk) > overlap else chunk
            current = []
            current_len = 0

    # flush any remaining paragraphs as the final chunk
    if current:
        chunk = "\n\n".join(current)
        if chunk.strip():
            chunks.append(chunk)

    return [c for c in chunks if c.strip()]


def run_pipeline():
    docs = load_documents(RAW_DIR)
    print(f"loaded {len(docs)} documents")

    all_chunks = []

    for doc in docs:
        filename = doc["filename"]
        meta, body = parse_metadata(doc["raw"])
        body = clean_text(body)
        save_cleaned(filename, meta, body, CLEANED_DIR)

        text_chunks = chunk_text(body)
        for i, chunk in enumerate(text_chunks):
            all_chunks.append({
                "source": filename,
                "title": meta.get("title", ""),
                "topic": meta.get("topic", ""),
                "chunk_index": i,
                "text": chunk,
            })

    # write all chunks to json
    chunks_path = Path(CHUNKS_FILE)
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"total chunks: {len(all_chunks)}")
    print()

    # print five representative chunks evenly spaced across the collection
    n = len(all_chunks)
    sample_indices = [0, n // 4, n // 2, 3 * n // 4, n - 1]
    print("--- five representative chunks ---")
    for idx in sample_indices:
        c = all_chunks[idx]
        print(f"\n[chunk {idx}]")
        print(f"  source:      {c['source']}")
        print(f"  title:       {c['title']}")
        print(f"  topic:       {c['topic']}")
        print(f"  chunk_index: {c['chunk_index']}")
        print(f"  length:      {len(c['text'])} chars")
        print(f"  text preview:")
        print(f"    {c['text'][:220].replace(chr(10), ' ')}")


def main():
    run_pipeline()


if __name__ == "__main__":
    main()
