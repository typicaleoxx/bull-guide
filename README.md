# The Unofficial Guide: Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text. If a section is not done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Bull Guide is an unofficial computer science course guide. It covers course difficulty, exam preparation, programming study habits, group project coordination, course registration, and balancing internships with coursework. This knowledge is useful because official course catalogs list prerequisites and credit hours but say nothing about where students actually get stuck, what study habits work, or what goes wrong in team projects. Students pass this information to each other informally, and it often disappears between graduating cohorts. Bull Guide collects it in one searchable place.

The ten documents in this project are locally created synthetic sample documents based on common computer science student experiences. They are not real student reviews, Reddit posts, surveys, or verified testimony from any institution.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Synthetic sample document | Local .txt file | documents/raw/computer_logic_experiences.txt |
| 2 | Synthetic sample document | Local .txt file | documents/raw/course_registration_advice.txt |
| 3 | Synthetic sample document | Local .txt file | documents/raw/data_structures_exam_advice.txt |
| 4 | Synthetic sample document | Local .txt file | documents/raw/data_structures_experiences.txt |
| 5 | Synthetic sample document | Local .txt file | documents/raw/discrete_math_experiences.txt |
| 6 | Synthetic sample document | Local .txt file | documents/raw/group_project_advice.txt |
| 7 | Synthetic sample document | Local .txt file | documents/raw/internship_course_balance.txt |
| 8 | Synthetic sample document | Local .txt file | documents/raw/operating_systems_experiences.txt |
| 9 | Synthetic sample document | Local .txt file | documents/raw/programming_study_advice.txt |
| 10 | Synthetic sample document | Local .txt file | documents/raw/software_engineering_projects.txt |

---

## Chunking Strategy

**Chunk size:** Approximately 700 characters target, 1000 characters maximum

**Overlap:** 120 characters

**Why these choices fit your documents:**

Each document is written as a series of short paragraphs, where each paragraph covers one idea. The chunking strategy is paragraph-aware: the splitter accumulates paragraphs until the running character count reaches the target of 700, then closes the chunk at the end of the current paragraph rather than cutting mid-sentence. If the next paragraph would push the total past the 1000-character maximum, the current chunk is closed first before that paragraph is added. This prevents any chunk from mixing unrelated topics.

The 120-character overlap takes the tail of each closed chunk and prepends it to the start of the next one. This keeps some context from the previous chunk available so that advice near a paragraph boundary is still searchable. The overlap is character-based, not paragraph-based, so it may begin mid-sentence, but it still gives the embedding model enough context to bridge the gap.

A target of 700 characters holds roughly two to three short paragraphs, which matches how the advice in these documents is organized. Smaller chunks would split individual arguments across retrievals. Larger chunks would mix advice from different topics and reduce retrieval precision.

**Final chunk count:** 20 chunks across 10 documents (approximately 2 per document)

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, no API key required)

**Production tradeoff reflection:**

all-MiniLM-L6-v2 is fast, free to run locally, and returns 384-dimensional vectors that perform well on short factual text. It was the right choice for a local prototype with a small corpus and no latency requirements.

For a real deployment, the main concern is domain specificity. MiniLM is a general-purpose model not trained on CS student advice. When a query uses vocabulary that appears in multiple documents, the model can return chunks from the wrong topic because the surface words look similar. A model fine-tuned on educational or student-forum text would reduce that drift. Context length is not a concern here because all chunks are under 1000 characters, but a corpus with longer documents would push against MiniLM's 256-token limit. A hosted embedding API would remove the local compute cost but would add a per-call fee and network latency for every query and every indexing run. Multilingual support is not needed here but would matter immediately if the guide expanded to serve non-English-speaking students.

---

## Sample Chunks

These five chunks are drawn evenly from the 20-chunk collection. Each chunk is the text stored in ChromaDB and returned by retrieval.

**Chunk 0 -- computer_logic_experiences.txt, chunk index 0 (744 chars)**
```
Students describe Computer Logic and Design as a course that connects Boolean algebra with
physical digital circuits. Early topics often include binary numbers, logic gates, truth tables,
Boolean expressions, and simplification.

Boolean simplification is a common source of mistakes. Students may know individual identities
but apply them incorrectly when several variables are involved. Writing one transformation per
line makes the reasoning easier to check.

Karnaugh maps can make simplification faster, but students sometimes group cells incorrectly.
Valid groups must contain powers of two, may wrap around the edges, and should be as large as
possible. Students recommend checking the simplified result against the original truth table.
```

**Chunk 5 -- data_structures_exam_advice.txt, chunk index 1 (615 chars)**
```
at manipulate indexes or references. Writing the state of each variable after every important
line can prevent mistakes.

Students also recommend practicing Big O analysis without relying only on memorized answers.
For each operation, they identify how the amount of work changes as the input grows and whether
the algorithm processes one element, all elements, or nested combinations of elements.

Before the exam, students suggest reviewing mistakes from homework and previous quizzes.
Problems that caused confusion during assignments often reveal the same concepts that need
additional practice before the test.
```

**Chunk 10 -- group_project_advice.txt, chunk index 0 (702 chars)**
```
Students recommend discussing expectations at the beginning of a group project. The team should
agree on communication channels, meeting times, task ownership, coding conventions, and how
missed deadlines will be handled.

Large tasks should be divided into smaller deliverables with clear acceptance criteria. Saying
that one person owns the backend is too broad. Assigning a specific endpoint, database function,
test, or documentation section makes progress easier to verify.

Version control problems are common when team members work directly on the same branch. Students
recommend creating separate branches, making focused commits, and reviewing changes before
merging them into the main branch.
```

**Chunk 15 -- operating_systems_experiences.txt, chunk index 1 (576 chars)**
```
e. Race conditions, locks, semaphores, and critical sections require students to reason about
multiple execution orders.

Virtual memory is another challenging area. Students need to understand addresses, pages,
frames, page tables, translation, and page replacement. Drawing address translation steps can
make the process more concrete.

Students recommend starting programming assignments early because operating systems bugs may not
produce clear error messages. Tools such as compiler warnings, debuggers, memory checkers, logs,
and small test cases are especially useful.
```

**Chunk 19 -- software_engineering_projects.txt, chunk index 1 (625 chars)**
```
racts early, using pull requests, and merging small changes regularly instead of combining
everything near the deadline.

Scope control is also important. Teams sometimes spend too much time adding optional features
while required functionality remains incomplete. A better approach is to finish a small working
version first and then add improvements only after the core system is stable.

Students say that clear documentation improves both teamwork and grading. A useful README should
explain the project purpose, setup steps, architecture, important decisions, known limitations,
and how each major feature can be tested.
```

---

## Retrieval Tests

Three queries were run against the ChromaDB collection after re-indexing. Top-5 results are shown with source filenames and distance scores. Lower distance means higher similarity.

**Query 1: What do students find difficult about Data Structures?**

| Rank | Source | Distance |
|------|--------|----------|
| 1 | data_structures_experiences.txt | 0.6070 |
| 2 | data_structures_experiences.txt | 0.7796 |
| 3 | data_structures_exam_advice.txt | 0.8002 |
| 4 | computer_logic_experiences.txt | 0.9207 |
| 5 | programming_study_advice.txt | 0.9982 |

Rank 1 is the strongest match. It comes from the document that describes student experiences in Data Structures, including the sections on recursion and pointer difficulties. Rank 2 is the second chunk of that same document, continuing the discussion of linked structure implementation. Rank 3 is partially relevant because it describes what the exam tests, which overlaps with what students find hard. Rank 4 drifts into Computer Logic, probably because similar "difficulty" language appears there too.

**Query 2: How should students prepare for Computer Logic exams?**

| Rank | Source | Distance |
|------|--------|----------|
| 1 | computer_logic_experiences.txt | 0.7596 |
| 2 | data_structures_exam_advice.txt | 0.8357 |
| 3 | programming_study_advice.txt | 0.9231 |
| 4 | computer_logic_experiences.txt | 0.9756 |
| 5 | operating_systems_experiences.txt | 1.0059 |

Rank 1 is a good match. The computer_logic_experiences.txt document has a paragraph specifically about exam preparation for that course, covering full-problem practice from verbal requirement to truth table to circuit diagram. Rank 2 is the Data Structures exam advice document, which contains general study tips that apply across many courses. The retrieval is partially on target. The model sees similar exam-related words in different documents and returns advice from the wrong course at rank 2.

**Query 3: What problems happen during software engineering group projects?**

| Rank | Source | Distance |
|------|--------|----------|
| 1 | software_engineering_projects.txt | 0.7083 |
| 2 | group_project_advice.txt | 0.7966 |
| 3 | group_project_advice.txt | 0.9447 |
| 4 | software_engineering_projects.txt | 1.0231 |
| 5 | programming_study_advice.txt | 1.3178 |

Rank 1 is a direct match. The software_engineering_projects.txt document describes concrete problems: coordination failures, uneven workloads, integration errors, and scope control. Rank 2 is also relevant. The group_project_advice.txt document covers the same topic from the advice side, including version control problems and what to do when communication breaks down. Together these two documents gave the model enough context to produce a complete answer. Rank 5 (programming_study_advice) appears because it mentions debugging and code review, which share vocabulary with team project discussions.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt instructs the model to answer using only the information in the provided context excerpts, to not use any knowledge from its training data, and to not infer or guess information not explicitly stated. If the context is insufficient, the model is instructed to return this exact sentence and nothing else:

> The available documents do not provide enough information to answer this question.

The full system prompt is in `pipeline.py` in the `ask()` function.

**How source attribution is surfaced in the response:**

Source filenames come from the retrieved chunk metadata, not from the model. The `ask()` function collects them from the `hits` list in retrieval order and skips duplicates. The source list is returned alongside the answer in the result dictionary. The Gradio interface displays it in a separate output field. The model is never asked to name or format source files.

---

## Example Responses

**Supported question 1: What do students find difficult about Data Structures?**

System answer:
> According to the context excerpts, students find the following aspects of Data Structures difficult:
>
> 1. Recursion: Students struggle to trace several recursive calls at once, but drawing the call stack by hand and identifying the base case can make it easier.
> 2. Pointers and references: Especially when implementing linked structures, small mistakes involving null references, incorrect links, or updates in the wrong order can break the entire structure. Drawing each node and pointer connection before changing the code can help.

Sources: `data_structures_experiences.txt`, `data_structures_exam_advice.txt`, `computer_logic_experiences.txt`, `programming_study_advice.txt`

**Supported question 2: What problems commonly occur during software engineering group projects?**

System answer:
> According to the context excerpts, the following problems commonly occur during software engineering group projects:
>
> 1. Coordination problems, such as unclear responsibilities, deadlines, and interfaces.
> 2. Uneven workloads, where one member may complete most of the implementation while others contribute late or submit work that does not integrate.
> 3. Integration problems, which appear when team members work on separate branches without agreeing on data formats or function interfaces.
> 4. Version control problems, which occur when team members work directly on the same branch.
> 5. Scope control issues, where teams spend too much time adding optional features while required functionality remains incomplete.
> 6. Communication problems, such as not informing the group early enough when a task becomes blocked.
> 7. Inconsistent naming, input formats, environment variables, or dependency versions, which can cause features to fail when combined.

Sources: `software_engineering_projects.txt`, `group_project_advice.txt`, `programming_study_advice.txt`

**Unsupported question: Which parking garage is best for biology students?**

System answer:
> The available documents do not provide enough information to answer this question.

Sources listed by retrieval (the closest matches in the corpus, all unrelated to parking): `course_registration_advice.txt`, `internship_course_balance.txt`, `group_project_advice.txt`, `operating_systems_experiences.txt`. The model correctly refused to use these unrelated chunks to fabricate an answer.

---

## Query Interface

The Gradio interface is implemented in `app.py`. It launches a local web page at `http://localhost:7860` when run with `python app.py`.

**Input fields:**
- Question textbox with placeholder text. Submits on Enter key or button click.
- Ask button.

**Output fields:**
- Answer: the grounded response from the model.
- Sources: the list of source filenames the answer was drawn from, built from chunk metadata.
- Retrieved Evidence: the top five chunks returned by semantic search, each labeled with source filename and similarity distance.

**Example questions included in the interface:**
1. What do students find difficult about Data Structures?
2. How should students prepare for Computer Logic exams?
3. What problems happen during software engineering group projects?
4. Which parking garage is best for biology students?

**Sample interaction transcript:**

```
Question:  What do students recommend for preparing for Computer Logic exams?

Answer:    For preparing for Computer Logic exams, students recommend practicing
           complete problems that move from a verbal requirement to a truth table,
           simplified expression, and circuit diagram. They also suggest checking
           the simplified result against the original truth table, especially when
           using Karnaugh maps for simplification. Additionally, students recommend
           writing one transformation per line when simplifying Boolean expressions
           to make the reasoning easier to check. Rereading lecture notes alone is
           not considered enough practice for this type of problem.

Sources:   - computer_logic_experiences.txt
           - data_structures_exam_advice.txt
           - programming_study_advice.txt
           - operating_systems_experiences.txt

Retrieved  [1] computer_logic_experiences.txt  (distance: 0.7845)
Evidence:  Students describe Computer Logic and Design as a course that connects
           Boolean algebra with physical digital circuits...
```

---

## Evaluation Report

Five test questions were run through the full pipeline. Results are also saved in `evaluation/results.txt` and `evaluation/results.json`.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students find difficult about Data Structures? | Recursion, pointers, choosing the right structure | Named recursion, pointers, linked structure mistakes; matched expected content | Relevant | Accurate |
| 2 | What do students recommend for preparing for Computer Logic exams? | Practice full problems: verbal to truth table to circuit diagram | Covered full-problem practice, Karnaugh map checking, and writing one transformation per line | Relevant | Accurate |
| 3 | What problems commonly occur during software engineering group projects? | Coordination, uneven workloads, integration errors, scope creep | Listed all four expected problem types plus version control and communication issues from a second source | Relevant | Accurate |
| 4 | What advice do students give for balancing coursework with an internship? | Avoid heavy courses, time blocks, start early, communicate with supervisors | Covered all four expected points plus added sleep and recovery advice from the document | Relevant | Accurate |
| 5 | Which parking garage is best for biology students? | Exact refusal sentence | Returned the exact required refusal sentence | Off-target (expected) | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

Query 2 (Computer Logic exam prep) is the clearest partial failure. The query was answered correctly, but rank 2 in retrieval returned `data_structures_exam_advice.txt` rather than the second chunk of `computer_logic_experiences.txt`.

**What the system returned:**

The top retrieval hit was correct: chunk 0 of `computer_logic_experiences.txt` at distance 0.7596. But rank 2 was `data_structures_exam_advice.txt` at 0.8357 because that document contains general exam advice that shares vocabulary ("exams", "practice", "review") with the query.

**Root cause (tied to a specific pipeline stage):**

This is a retrieval drift problem. all-MiniLM-L6-v2 was not trained on CS course material. The model sees similar exam-related words in both documents and ranks the Data Structures advice nearly as high as the Computer Logic advice. The second chunk of `computer_logic_experiences.txt`, which has the most specific exam guidance (practicing full circuit design problems), ends up at distance 0.9756 and ranked 4th.

**What you would change to fix it:**

Adding the topic label (for example, "Computer Logic") to each chunk's stored text before embedding would help the model separate exam-advice documents that cover different courses. Alternatively, metadata filtering could restrict retrieval to only `computer_logic_experiences.txt` when the query explicitly names that course.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The Chunking Strategy section of planning.md specified paragraph-aware splitting at roughly 700 characters with 120 characters of overlap before any code was written. Having this written down meant the implementation of `chunk_text()` had a clear contract to satisfy: close at paragraph boundaries, do not exceed 1000 characters, prepend the overlap tail to the next chunk. Without the spec, it would have been easy to implement a simple fixed-character split and miss the paragraph-boundary requirement.

**One way your implementation diverged from the spec, and why:**

The original evaluation plan in planning.md listed five questions based on the document content at the time the spec was written. Several of those documents were later updated with different content, so the expected answers in the original spec no longer matched what the system could find. The wording of some evaluation questions was adjusted after the final document set was completed so that each expected answer could be verified directly from the corpus. This divergence happened because the spec was finalized before the document content was stable, which is the opposite of the recommended order.

---

## AI Usage

I used an AI coding tool to help implement and debug parts of the project. I provided the assignment requirements, my planning decisions, the repository structure, and the expected behavior for each stage. I worked on the project one stage at a time instead of asking it to generate the entire project at once.

### Instance 1: Document pipeline and retrieval

I provided the tool with my chunking strategy from planning.md, including paragraph-aware splitting, a target size of about 700 characters, a maximum size of 1000 characters, and 120 characters of overlap. I asked it to implement document loading, cleaning, chunking, ChromaDB indexing, and semantic retrieval.

The tool produced the main pipeline functions and connected the local documents to all-MiniLM-L6-v2 and ChromaDB. I ran the pipeline, checked that all 10 documents loaded, inspected the generated chunks, verified that source metadata remained attached, and tested retrieval with course-specific questions. I also reran indexing to make sure it did not create duplicate records.

### Instance 2: Grounded generation and interface

I provided the grounding rules, the required refusal sentence, the source attribution requirements, and the fields needed in the Gradio interface. I asked the tool to connect retrieval to Groq and build a simple page that displayed the answer, sources, and retrieved evidence.

The tool produced the `ask()` function and the Gradio interface. I tested supported questions about Data Structures and software engineering group projects. I also tested an unsupported parking question and checked that the system refused to answer instead of inventing information. When the project failed because chromadb was missing from the active virtual environment, I installed the required dependencies and reran the tests.

I also used the tool to review the README against the project rubric. I checked the final documentation, Git changes, evaluation results, and application behavior before preparing the repository for submission.

---

## Setup and Run Instructions

**Requirements:** Python 3.9 or later, a Groq API key (free at console.groq.com, no credit card required).

**1. Clone and set up a virtual environment**

```bash
git clone <your-fork-url>
cd bull-guide
python -m venv .venv
source .venv/bin/activate        # Mac / Linux
# .venv\Scripts\activate         # Windows
```

**2. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**3. Add your API key**

```bash
cp .env.example .env
# open .env and replace your_key_here with your Groq API key
```

**4. Run the pipeline (ingestion, chunking, embedding, indexing)**

```bash
python pipeline.py
```

This reads all ten documents from `documents/raw/`, writes cleaned versions to `documents/cleaned/`, saves chunks to `data/chunks.json`, and indexes them in ChromaDB under `data/chroma/`. Running the pipeline again will not create duplicate records.

**5. Launch the interface**

```bash
python app.py
```

Open `http://localhost:7860` in your browser.

**6. Run the evaluation**

```bash
python evaluate.py
```

Results are saved to `evaluation/results.txt` and `evaluation/results.json`.
