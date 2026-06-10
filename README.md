# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

My system covers student reviews of CS professors at Widener University. I picked
this because it's hard to get this kind of info from the official school pages —
they tell you what a class covers but not what the professor is actually like, like
their teaching style, how hard they grade, or how much work they give. Most of the
real opinions are spread out across RateMyProfessors and student review sites, so
it's not easy to find everything in one place. My chatbot pulls those reviews
together and answers questions about them using only what's in the reviews.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

The documents I actually used are 5 text files in the [data/](data/) folder. Each
one holds the student reviews I collected for a specific Widener CS professor, plus
one file of general reviews about the CS program. I planned more sources in my
planning.md (Reddit threads and the official department pages), but I left those out
of the final corpus because they didn't really have usable student review text when
I went to grab them.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Jeffrey Rufinus — RateMyProfessors | Student reviews | [data/rufinus.txt](data/rufinus.txt) · https://www.ratemyprofessors.com/professor/502947 |
| 2 | Suk-Chung Yoon — RateMyProfessors | Student reviews | [data/yoon.txt](data/yoon.txt) · https://www.ratemyprofessors.com/professor/976472 |
| 3 | Adam Fischbach — RateMyProfessors | Student reviews | [data/fischbach.txt](data/fischbach.txt) · https://www.ratemyprofessors.com/professor/1879795 |
| 4 | Yana Kortsarts — RateMyProfessors | Student reviews | [data/yana.txt](data/yana.txt) · https://www.ratemyprofessors.com/search/professors/1198?q=Kortsarts |
| 5 | Widener CS program — StudentsReview | Student reviews | [data/studentrev.txt](data/studentrev.txt) · http://www.studentsreview.com/undergraduate.php3?MAJOR_NAME=Computer+Science&PID=12&UID=1222 |

Sources I planned but didn't end up using: the r/Widener Reddit threads, the official
[CS & CIS department page](https://www.widener.edu/profile/computer-science-computer-information-systems-department),
and the [BS course catalog](https://catalog.widener.edu/preview_program.php?catoid=50&poid=8000).

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 400 characters max per chunk (`max_chunk_size=400` in my
`chunk_text()` function in [main.py](main.py)). Instead of cutting straight at 400
characters, I first split the text into sentences, then keep adding whole sentences
to a chunk until the next one would push it over 400. If a single sentence is
somehow longer than 400 chars by itself, a fallback hard-splits it so a chunk can't
overflow.

**Overlap:** 1 sentence. My overlap is counted in sentences, not characters — when I
start a new chunk I carry over the last sentence from the chunk before it. (I had
written "~50 characters" in my first draft, but I changed it because counting in
sentences keeps a whole idea together instead of cutting it mid-word.)

**Why these choices fit my documents:** My documents are short student reviews where
each sentence is usually one opinion ("tough grader," "explains clearly," "gives a
lot of homework"). Splitting on sentences keeps those opinions whole, and 400
characters is big enough to hold a full thought but small enough that retrieval
stays focused and unrelated opinions don't get mixed into the same chunk. The
1-sentence overlap helps when a reviewer's point runs across two sentences so the
chunk boundary doesn't cut it in half. My only preprocessing is reading each file as
UTF-8 and stripping whitespace — the reviews were already saved as clean plain text,
so there was no HTML to remove.

**Final chunk count:** 21 chunks total — fischbach.txt (6), rufinus.txt (4),
yana.txt (4), yoon.txt (4), studentrev.txt (3).

---

## Sample Chunks

Here are 6 real chunks my `chunk_text()` function produced, each labeled with the
source file it came from:

**1. `source: yoon.txt`**
> Professor Yoon is straight up the goat. If you need lab science credits, take his class any day of the week. He's very easy when it comes to programming in Python because he explains how to code really well. He also gives extra credit to students who show up on days with low attendance. Amazing lectures, respected, helpful. One of the nicest professors I've had.

**2. `source: fischbach.txt`**
> Sometimes he tells us to add new things to our projects without explaining them. Tough grader, lecture heavy. Fischbach is not a bad professor but not great. Most of the time he doesn't really teach but yaps constantly during lectures, which makes them boring and forces us to teach ourselves Java. He's really picky about projects, which makes grading feel confusing.

**3. `source: yana.txt`**
> Two weeks of strings is mad crazy too. Tough grader, lots of homework, respected, helpful. Love her accent, she's awesome and her teaching style is very elite. Not only is she a nice professor but a nice person as well and understands what she's doing as a professor doing her job right. Helpful. Professor Kortsarts has been one of my favorite professors so far.

**4. `source: rufinus.txt`**
> Test heavy. Lecture heavy.” “He starts the first class off talking about the OSI model, then immediately jumps into physics. From that day forward, it's all physics and tests every week (8 in total). I tried on the first exam and got a 74, which surprisingly is a B for his class. Test heavy. Lecture heavy.”

**5. `source: studentrev.txt`**
> Some professors are amazing, others feel like they're just reading off slides. The environment is friendly, but the surrounding area isn't great.” “The education in general at Widener is pretty good, but the Computer Science department is HORRIBLE. DO NOT GO HERE FOR COMPUTER SCIENCE. The surrounding city is unsafe, and the department feels outdated.

**6. `source: yana.txt`**
> Helpful. Professor Kortsarts has been one of my favorite professors so far. She was always helping us and gave students lots of opportunities as well. Clear grading criteria, caring, respected, helpful.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` through `sentence-transformers` (loaded with
LangChain's `HuggingFaceEmbeddings`). I picked it because it runs locally on my
machine, so it needs no API key and costs nothing to embed all my chunks. It makes
384-dimensional vectors, which are small and fast to search in FAISS, and for short
review text it was accurate enough in my tests. I retrieve the top `k=3` chunks per
query.

**Production tradeoff reflection:** If I were deploying this for real students and
cost wasn't a problem, here's what I'd weigh before switching to a bigger model like
OpenAI's `text-embedding-3-large` or Cohere's `embed-v3`:
- **Accuracy on my kind of text:** Review slang ("he yaps," "straight up the goat,"
  "tough grader") is really informal and sometimes sarcastic. A bigger model would
  probably pick up on that tone better, and it might fix the recall problem I ran
  into in my failure case below.
- **Context length:** MiniLM cuts off around 256 tokens, so if I moved to longer
  documents like full Reddit threads instead of single reviews, I'd want a model
  with a bigger input window so chunks don't get silently cut off.
- **Multilingual support:** Doesn't matter for my corpus since it's all English, but
  it would matter if I added international-student forums.
- **Latency:** A hosted API adds a network round-trip on every query and depends on
  their uptime, while MiniLM is instant and works offline.

For this project MiniLM wins — it's free, local, fast, and good enough for short
reviews. I'd only upgrade if I scaled up to longer or messier documents where the
retrieval quality started to slip.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** I enforce grounding with a strict prompt in
[rag.py](rag.py). It tells the model to answer using ONLY the retrieved review
chunks, and to refuse with one exact sentence if the chunks don't have the answer.
Here's the actual instruction:

```
You are The Unofficial Guide, an assistant that answers questions about
Widener University CS professors using ONLY the student reviews provided
in the context below.

Rules:
- Use ONLY the information in the context. Do not use any outside knowledge.
- Do not invent professors, facts, or opinions that are not in the context.
- If the context does not contain enough information to answer the question,
  reply with exactly this sentence and nothing else:
  "I don't have information about that in the professor reviews."
```

It's not just the prompt though — the structure backs it up too. The LLM
(`llama-3.1-8b-instant` on Groq) only ever sees the top-3 retrieved chunks as its
context, so it has no other access to the corpus or the internet. I run it at
`temperature=0.2` to keep it close to the retrieved text, and the fixed refusal
sentence means out-of-scope questions give a clean, predictable refusal instead of a
made-up answer.

**How source attribution is surfaced in the response:** Each chunk carries a
`metadata={"source": <filename>}` tag that I attach when I build the vector store in
[main.py](main.py). My chain uses `return_source_documents=True`, so every answer
comes back with the exact chunks behind it. The CLI in [rag.py](rag.py) prints them
under a `--- SOURCES ---` header, and the Streamlit app in [app.py](app.py) shows
`Source: <filename>` above each supporting chunk, so you can see which review file
the answer came from. (I had to add that source metadata myself — at first it always
showed "unknown" because the vector store was built without it.)

---

## Retrieval Test Results

I ran 3 queries through my retriever (`k=3`) and looked at the top chunks it
returned, with the source file for each.

### Query 1 — "Which professor is a tough grader?"
| Rank | Source | Chunk (excerpt) |
|------|--------|-----------------|
| 1 | yana.txt | "...Separating students during graded lab is absurd, and taking photos of the students' seats to see if they cheat is crazy too. Two weeks of strings is mad crazy too." |
| 2 | yana.txt | "Two weeks of strings is mad crazy too. **Tough grader, lots of homework**, respected, helpful..." |
| 3 | rufinus.txt | "...His lessons move extremely fast... Lecture heavy. Test heavy.” “People rate him poorly but in reality he's just a chill guy..." |

**Why these are relevant:** Chunk 2 is a direct hit — it literally has the words
"Tough grader" attached to Professor Kortsarts (yana.txt), and the system grabbed
the context around it about her strict lab rules. Chunk 1 is the chunk right before
it (my 1-sentence overlap links them), so it points at the same professor. The
retriever matched the idea of being strict even where the word "grader" wasn't in
the text.

### Query 2 — "Which professor gives the most homework?"
| Rank | Source | Chunk (excerpt) |
|------|--------|-----------------|
| 1 | yana.txt | "Good professor but needs to chill on giving too much slack to students..." |
| 2 | yoon.txt | "Professor Yoon is straight up the goat... He also gives extra credit..." |
| 3 | fischbach.txt | "...He's really picky about projects, which makes grading feel confusing." |

**Why these are relevant:** The top match (yana.txt) is the same review cluster that
elsewhere says "lots of homework," so it points at the right professor (Kortsarts)
for a workload question. The yoon and fischbach chunks are weaker, more general
matches about workload and projects — this query actually shows a gap, because the
chunk that literally says "lots of homework" didn't make the top-3 for this wording
(more on that in my failure case).

### Query 3 — "Which professor explains things clearly?"
| Rank | Source | Chunk (excerpt) |
|------|--------|-----------------|
| 1 | fischbach.txt | "...Most of the time he doesn't really teach but yaps constantly during lectures..." |
| 2 | yana.txt | "...her teaching style is very elite..." |
| 3 | yana.txt | "...gave students lots of opportunities... **Clear grading criteria**..." |

---

## Example Responses

Two real answers from my system that show source attribution, plus one out-of-scope
question that triggers the refusal.

**Example 1 (answered, with sources)**
> **Q:** Which professor is the most supportive or approachable?
>
> **Answer:** Based on the reviews, the professors described as "caring" and
> "helpful" include Professor Kortsarts and a professor repeatedly called "super
> caring" and "always available to help you." The one that stands out most for being
> supportive and approachable is the professor who is "super caring and always
> available to help you."
>
> **Sources:** yana.txt, yoon.txt, yana.txt

**Example 2 (answered, with sources)**
> **Q:** What do students say about the difficulty of CS courses overall?
>
> **Answer:** Students say the CS program doesn't prepare you well for real-world CS
> jobs, and that the department feels outdated.
>
> **Sources:** rufinus.txt, studentrev.txt, rufinus.txt

**Example 3 (out-of-scope — refusal)**
> **Q:** What is the best dining hall at Widener?
>
> **Answer:** I don't have information about that in the professor reviews.

This last one is the behavior I want: dining halls aren't in my professor reviews,
so instead of guessing, the system gives its fixed refusal sentence.

---

## Query Interface

I have two interfaces that share the same `qa_chain`:
1. **Command line** ([rag.py](rag.py)): run `python rag.py "your question"` for a
   one-shot answer, or just `python rag.py` to get an interactive `Question>` loop.
2. **Streamlit web app** ([app.py](app.py)): run `streamlit run app.py`.

**Input field:** one natural-language question typed as free text.
**Output fields:** (a) the grounded **Answer**, and (b) a **Sources** list showing
the filename and text of each chunk the answer was based on.

**Sample interaction (Streamlit):**
```
Enter your question: Which professor is the most supportive or approachable?
[Ask]

Answer
Based on the reviews, the professors described as caring and helpful include
Professor Kortsarts and a professor repeatedly called "super caring" and
"always available to help you." The one that stands out most is the professor
who is super caring and always available to help you.

Sources
Source: yana.txt
  ...Professor Kortsarts has been one of my favorite professors so far. She was
  always helping us and gave students lots of opportunities...
Source: yoon.txt
  ...One of the nicest professors I've had. Super caring and always available to
  help you. Caring, respected, accessible outside class...
Source: yana.txt
  ...Tough grader, lots of homework, respected, helpful...
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

I ran all 5 of my test questions through the full pipeline. Being honest here:
3 of the 5 came back with the refusal sentence even though the answer is actually in
my reviews, because the right chunk didn't land in the top-3 (a retrieval problem I
dig into in the failure case below).

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which CS professor is known for tough grading? | Fischbach and/or Kortsarts (both labeled "Tough grader") | "I don't have information about that in the professor reviews." (refused) | Off-target — top-3 were studentrev/rufinus chunks, not the "Tough grader" ones | Inaccurate (refused when it shouldn't have) |
| 2 | Which professor is praised for clear explanations? | Yoon ("super clear explanations") | Refused | Off-target — Yoon's clarity chunk wasn't retrieved | Inaccurate (false refusal) |
| 3 | Which professor gives the most homework? | Kortsarts ("lots of homework") | Refused | Partially relevant — right professor's cluster came up, but not the "lots of homework" chunk | Inaccurate (false refusal) |
| 4 | Which professor is most supportive/approachable? | Yoon and/or Kortsarts (both "caring," "helpful") | Named the "super caring / always available" professor (Yoon) and Kortsarts | Relevant (yana + yoon) | Partially accurate — right professors, but hedged and didn't name Yoon directly |
| 5 | What do students say about CS course difficulty overall? | Mixed — challenging, varies by professor | "The program doesn't prepare you well for real-world jobs and feels outdated." | Partially relevant — only pulled the negative studentrev chunk | Partially accurate — true but one-sided, missed the "depends on the professor" theme |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "Which CS professor at Widener is known for tough grading?"

**What the system returned:** The refusal sentence — "I don't have information about
that in the professor reviews." — even though both fischbach.txt and yana.txt
literally say "Tough grader."

**Root cause (tied to a specific pipeline stage):** This is a retrieval problem, not
a generation problem. Two of my choices combined to cause it:
1. **My chunking puts the labels at the end of chunks.** The short tags like "Tough
   grader, lecture heavy" sit at the very end of a review, so when I pack sentences
   into a chunk, that label lands at the tail of a chunk that's mostly other text.
   That means the chunk's embedding gets pulled toward the review's storyline, not
   toward the "tough grader" label itself.
2. **`k=3` is too small for my corpus.** Since only 3 chunks get passed to the LLM,
   the MiniLM similarity scores ranked more general chunks (studentrev's "professors
   vary in quality," rufinus's "lessons move fast") above the Fischbach/Yana chunks
   that actually have the label. And because my grounding prompt is strict and the
   temperature is low (0.2), the model correctly refused instead of guessing — the
   evidence genuinely wasn't in the 3 chunks it got.

So the info is in my corpus, the chunk that holds the actual label just didn't rank
high enough for this query, and the small `k` gave it no second chance.

**What I would change to fix it:**
- **Bump `k` from 3 to 5.** The label chunks tend to sit in positions 4–5 for these
  queries, so a slightly bigger `k` would feed them to the LLM without loosening any
  of my grounding rules. This is the cheapest, highest-impact fix and the first
  thing I'd try.
- **Add the professor's name to each chunk** (like prefixing "Review of Professor
  Fischbach:") so name and attribute queries embed closer to the right chunks.
- **Stop stranding the short label sentences** so a tag like "Tough grader, lecture
  heavy." doesn't start a fresh chunk on its own, separated from the review it
  describes.
- Longer term, a stronger embedding model (see my Embedding Model notes) would
  probably improve recall on this slangy, label-heavy text.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing out my Chunking
Strategy in planning.md before I coded anything made me actually think about the
shape of my documents (short reviews, one opinion per sentence) instead of just
grabbing some default chunk size. By the time I wrote `chunk_text()`, I already knew
I wanted sentence-based packing with a 400-char cap, so the function came together
fast and fit my data instead of needing a redo after I saw bad chunks.

**One way your implementation diverged from the spec, and why:** My plan said the
overlap would be "~50 characters," but in the code I switched it to whole sentences
(carry the last 1 sentence into the next chunk). A character overlap would cut words
or thoughts in half, which is exactly what hurts retrieval on opinion text, so
sentence overlap kept each idea together. I also added per-chunk source metadata
that wasn't in my original build step — without it the app always showed the source
as "unknown," so I had to pass `metadatas=...` into `FAISS.from_texts(...)` to make
source attribution actually work.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Writing the chunking function**

- *What I gave the AI:* My Chunking Strategy section from planning.md (400-char cap,
  overlap, "these are short reviews") and asked it to write `chunk_text()`.
- *What it produced:* A first version that just split on a fixed character count with
  about 50 characters of overlap.
- *What I changed or overrode:* I didn't like that it cut sentences in the middle, so
  I directed it to split on sentence boundaries first, pack whole sentences up to 400
  chars, and make `overlap` count *sentences* (1) instead of characters. I also had
  it add the `_hard_split` fallback so one giant sentence can't overflow a chunk.

**Instance 2 — Fixing the broken source attribution**

- *What I gave the AI:* The bug that [app.py](app.py)'s
  `doc.metadata.get('source', 'unknown')` always printed "unknown," plus the line in
  [main.py](main.py) that built the store with `FAISS.from_texts(all_chunks, embeddings)`.
- *What it produced:* It figured out the vector store was built with no metadata, so
  there was no `source` field to read back.
- *What I changed or overrode:* Instead of just hard-coding a label or dropping the
  source from the UI, I had it track each chunk's filename during ingestion and pass
  a matching `metadatas=[{"source": file}, ...]` list into `FAISS.from_texts(...)`,
  then rebuild the index — which made the real source show up in both the CLI and the
  Streamlit app.
