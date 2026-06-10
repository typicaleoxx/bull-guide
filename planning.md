# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Bull Guide is an unofficial computer science course guide. It covers course difficulty, exam preparation strategies, programming study habits, group project workflows, course registration planning, and balancing internships with coursework. This knowledge is valuable because official course catalogs list prerequisites and credit hours but give no sense of actual workload, exam style, or what tends to help students succeed. Students mostly pass this information down informally through word of mouth, and it often disappears between cohorts. Bull Guide collects that tacit knowledge into one searchable place.

The documents in this project are locally created synthetic sample documents based on common computer science student experiences. They are not real student reviews, Reddit posts, surveys, or verified testimony from any institution.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Synthetic sample document | General student experiences in Data Structures: workload, drawing structures by hand, office hours, and study group tips | documents/raw/data_structures_experiences.txt |
| 2 | Synthetic sample document | Exam preparation advice for Data Structures: Big-O practice, edge cases, working through past exams under timed conditions | documents/raw/data_structures_exam_advice.txt |
| 3 | Synthetic sample document | Student experiences with Discrete Mathematics: proofs by induction, logic sections, graph theory, and reading the textbook before lecture | documents/raw/discrete_math_experiences.txt |
| 4 | Synthetic sample document | Student experiences with Computer Logic: Boolean algebra, Karnaugh maps, sequential circuits, and lab section tips | documents/raw/computer_logic_experiences.txt |
| 5 | Synthetic sample document | Experiences with software engineering group projects: Agile processes, Git branching strategy, documentation, and sprint communication | documents/raw/software_engineering_projects.txt |
| 6 | Synthetic sample document | Student experiences with Operating Systems: concurrency bugs, project time estimates of 15-25 hours, and the Three Easy Pieces textbook | documents/raw/operating_systems_experiences.txt |
| 7 | Synthetic sample document | General programming study habits: daily practice, debugging strategies, reading model solutions, and peer explanation | documents/raw/programming_study_advice.txt |
| 8 | Synthetic sample document | Advice for CS group projects: ownership by module, commit frequency, addressing team friction early, and shared meeting notes | documents/raw/group_project_advice.txt |
| 9 | Synthetic sample document | Course registration advice: planning two to three semesters ahead, waitlists, prerequisite reasoning, and balancing course load honestly | documents/raw/course_registration_advice.txt |
| 10 | Synthetic sample document | Managing coursework during an internship semester: reducing technical course load, time blocking, communicating with managers, and returning to class with stronger motivation | documents/raw/internship_course_balance.txt |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** Approximately 700 characters

**Overlap:** 120 characters

**Reasoning:** The documents are written as multi-paragraph plain text, where each paragraph covers one distinct idea. Paragraph-aware chunking means the splitter finishes the current paragraph before closing a chunk rather than cutting at an exact character count mid-sentence. This keeps related sentences together and prevents a chunk from ending in the middle of a thought that would confuse the retrieval model. A target of 700 characters holds roughly one to two full paragraphs, which matches the granularity of the advice in these documents. A chunk that is too small would split a single argument across two separate retrievals; a chunk that is too large would mix unrelated topics and hurt precision. The 120-character overlap carries the last sentence or two of one chunk into the start of the next, so that advice spanning a paragraph boundary is not silently dropped from any single retrieval result.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 5

**Production tradeoff reflection:** all-MiniLM-L6-v2 is fast, free to run locally, and performs well on short factual text, which fits this corpus. If this were deployed at real scale, the main tradeoff to consider is domain specificity. A general-purpose model like MiniLM was not trained on CS course advice, so it may rate a chunk about parking or campus housing as relevant to a question about OS concurrency if the surface vocabulary overlaps. A model fine-tuned on educational or student-forum text would narrow that gap. Latency is less of a concern here because the documents are small and local, but in a high-traffic deployment a hosted embedding API would shift the bottleneck from compute to network round-trip time. Multilingual support is not a priority for this project, but would matter immediately if the guide expanded to serve non-English-speaking students.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What study techniques do students in Data Structures recommend for keeping up with the material? | Drawing data structures by hand, reviewing slides the night they are posted, attending office hours, and forming small study groups where students explain concepts to each other. |
| 2 | How long do students say Operating Systems projects typically take to complete? | Students report that OS projects such as implementing a shell, a memory allocator, or parts of a file system can each take 15 to 25 hours for students working steadily. |
| 3 | What textbook do students recommend for the Operating Systems course? | Operating Systems: Three Easy Pieces is mentioned as a commonly used text that explains concepts clearly with diagrams and pseudocode. Relying only on slides tends to leave gaps. |
| 4 | What Git practices do students recommend to avoid merge conflicts in team software projects? | Using feature branches, reviewing pull requests before merging to main, committing small changes frequently, and not working in isolation for several days before pushing. |
| 5 | Where can CS students park on campus? | The system should respond that parking information is not covered in the available documents and cannot be answered from the provided knowledge base. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Off-topic retrieval on vague queries. Because all ten documents are about CS student life in general, a broad question like "how do I do better in class?" could pull chunks from five different files covering unrelated topics: exam prep, group projects, internships, and registration. The retrieved context would be diffuse and the generated answer would blend advice in ways that do not clearly address what the user actually asked. Keeping top-k at 5 and using specific evaluation questions during testing will help catch this early.

2. Paragraph boundary splits cutting key advice in half. Some paragraphs in these documents end with a specific fact, such as the 15 to 25 hour estimate for OS projects, that only makes full sense with the sentence before it. If a chunk boundary lands just before that sentence, the fact will appear in two separate chunks with neither one carrying the full context. The 120-character overlap is designed to reduce this, but it is worth manually inspecting a sample of the generated chunks during the ingestion milestone to confirm the split points are landing between paragraphs rather than inside them.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion -> Chunking -> Embedding + Vector Store -> Retrieval -> Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
INGESTION + INDEXING (runs once, offline)
==========================================

  documents/raw/*.txt
          |
          v
  [ Document Ingestion ]
    pipeline.py
    reads each .txt file as plain text
          |
          v
  [ Paragraph-Aware Chunking ]
    pipeline.py  chunk_text()
    target ~700 chars, 120 char overlap
    splits at paragraph boundaries
          |
          v
  [ Embedding ]
    sentence-transformers
    model: all-MiniLM-L6-v2
    produces 384-dim vectors
          |
          v
  [ ChromaDB Vector Store ]
    persisted locally
    stores chunk text + embeddings + metadata


QUERY + GENERATION (runs per user query)
==========================================

  [ Gradio UI ]
    user types a question
          |
          v
  [ Query Embedding ]
    same model: all-MiniLM-L6-v2
          |
          v
  [ ChromaDB Retrieval ]
    cosine similarity search
    returns top-5 chunks
          |
          v
  [ Prompt Assembly ]
    app.py
    system prompt + retrieved chunks + user question
          |
          v
  [ Groq LLM ]
    generation
          |
          v
  [ Gradio UI ]
    displays answer to user
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

I will use Claude Code in the terminal. I will paste the Chunking Strategy section of this file as context and ask it to implement two functions in pipeline.py: one that reads all .txt files from documents/raw and one called chunk_text() that splits a string into paragraph-aware chunks with a target of 700 characters and an overlap of 120 characters. I will verify the output by printing the first five chunks from one document and checking by eye that each chunk ends at a paragraph boundary, that no chunk is shorter than 200 characters or longer than 900, and that the overlap content from the previous chunk appears at the start of the next one.

**Milestone 4 — Embedding and retrieval:**

I will use Claude Code again, giving it the Retrieval Approach section of this file and the function signatures from Milestone 3 as context. I will ask it to implement the embedding step using sentence-transformers with all-MiniLM-L6-v2 and the vector store step using ChromaDB, including a retrieve() function that takes a query string and returns the top-5 most similar chunks. I will verify this by running a known query from the Evaluation Plan, such as the OS project time estimate question, and confirming that at least one of the five returned chunks contains the 15 to 25 hour figure from operating_systems_experiences.txt.

**Milestone 5 — Generation and interface:**

I will use Claude Code with the Architecture diagram and the full Evaluation Plan as context. I will ask it to implement the Gradio interface in app.py: a text input for the question, a call to retrieve() from Milestone 4, a prompt assembly step that injects the retrieved chunks as context, a call to the Groq API for generation, and a text output displaying the answer. I will verify by running all five evaluation questions manually through the interface and checking each answer against the expected answers in this file. The parking question in row 5 is a specific test for the refusal behavior: the system should acknowledge the question is out of scope rather than generating a plausible-sounding but wrong answer.
