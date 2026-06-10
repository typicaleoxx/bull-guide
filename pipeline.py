import json
import os
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

RAW_DIR = "documents/raw"
CLEANED_DIR = "documents/cleaned"
CHUNKS_FILE = "data/chunks.json"
CHROMA_DIR = "data/chroma"
CHROMA_COLLECTION = "bull_guide"

CHUNK_TARGET = 700
CHUNK_MAX = 1000
CHUNK_OVERLAP = 120

# module-level cache so the model and collection load once per process
_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_or_create_collection(CHROMA_COLLECTION)
    return _collection


# ── ingestion and chunking ────────────────────────────────────────────────────


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


# ── embedding and retrieval ───────────────────────────────────────────────────


def index_chunks():
    """
    load chunks from json, embed with all-MiniLM-L6-v2, and store in chromadb.
    the collection is dropped and recreated on every call so repeated runs
    never accumulate duplicate records.
    """
    global _collection

    with open(CHUNKS_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"embedding {len(chunks)} chunks with all-MiniLM-L6-v2...")
    model = _get_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    # drop and recreate the collection so the count is always exactly len(chunks)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(CHROMA_COLLECTION)
    _collection = collection  # keep module-level cache in sync with retrieve()

    ids = [f"{c['source']}_{c['chunk_index']}" for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "title": c["title"],
            "topic": c["topic"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=metadatas,
    )

    print(f"indexed {collection.count()} chunks in chromadb at {CHROMA_DIR}")


def retrieve(query, top_k=5):
    """
    embed the query with the same model used at index time, then run cosine
    similarity search against the chromadb collection.
    returns a list of result dicts ordered from most to least relevant.
    """
    model = _get_model()
    query_embedding = model.encode([query])[0].tolist()

    collection = _get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": doc,
            "source": meta["source"],
            "title": meta["title"],
            "topic": meta["topic"],
            "chunk_index": int(meta["chunk_index"]),
            "distance": round(dist, 4),
        })
    return hits


def ask(question):
    """
    retrieve relevant chunks then generate a grounded answer via groq.
    the model is instructed to answer only from the provided context and to
    return a fixed refusal sentence when the context is not sufficient.
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        raise ValueError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    hits = retrieve(question, top_k=5)

    # format retrieved chunks as numbered context excerpts
    context_parts = []
    for i, hit in enumerate(hits, start=1):
        context_parts.append(f"[{i}] Source: {hit['source']}\n{hit['text']}")
    context = "\n\n".join(context_parts)

    system_prompt = (
        "You are an assistant for the Bull Guide, an unofficial computer science student course guide.\n\n"
        "Answer the user's question using ONLY the information in the provided context excerpts.\n"
        "Do not use any knowledge from your training data.\n"
        "Do not infer, guess, or add information that is not explicitly stated in the excerpts.\n\n"
        "If the context does not contain enough information to answer the question, "
        "respond with this sentence exactly and nothing else:\n"
        "The available documents do not provide enough information to answer this question."
    )

    user_message = f"Context excerpts:\n\n{context}\n\nQuestion: {question}"

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
    )

    answer = response.choices[0].message.content.strip()

    # build source list from retrieved metadata; preserve order, no duplicates
    seen = set()
    sources = []
    for hit in hits:
        if hit["source"] not in seen:
            seen.add(hit["source"])
            sources.append(hit["source"])

    return {
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": hits,
    }


def test_retrieval():
    queries = [
        "What do students find difficult about Data Structures?",
        "How should students prepare for Computer Logic exams?",
        "What problems happen during software engineering group projects?",
    ]

    print("\n--- retrieval test ---")
    for query in queries:
        print(f"\nquery: {query}")
        hits = retrieve(query, top_k=5)
        for rank, hit in enumerate(hits, start=1):
            preview = hit["text"][:160].replace("\n", " ")
            print(f"  [{rank}] {hit['source']}  distance: {hit['distance']:.4f}")
            print(f"       {preview}")


# ── entry point ───────────────────────────────────────────────────────────────


def main():
    # run ingestion and chunking only if chunks file does not exist yet
    if not Path(CHUNKS_FILE).exists():
        run_pipeline()
    index_chunks()
    test_retrieval()


if __name__ == "__main__":
    main()
