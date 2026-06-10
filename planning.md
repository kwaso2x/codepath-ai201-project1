# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
chose the domain of student reviews of CS professors at Widener University. It’s hard to get this kind of information from official school pages because they don’t tell you what the professors are actually like — things like teaching style, grading difficulty, or how much work they give. Most of the real opinions are scattered across RateMyProfessors, Reddit, and random student conversations, so it’s not easy to find everything in one place.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Jeffrey Rufinus — RateMyProfessors | Student ratings/reviews of Widener CS professor | https://www.ratemyprofessors.com/professor/502947 |
| 2 | Suk-Chung Yoon — RateMyProfessors | Student ratings/reviews of Widener CS professor | https://www.ratemyprofessors.com/professor/976472 |
| 3 | Adam Fischbach — RateMyProfessors | Student ratings/reviews of Widener CS professor | https://www.ratemyprofessors.com/professor/1879795 |
| 4 | Yana Kortsarts — RateMyProfessors | Student ratings/reviews of Widener CS dept. chair | https://www.ratemyprofessors.com/search/professors/1198?q=Kortsarts |
| 5 | Reddit — Widener CS professors | Thread(s) discussing CS professors  | https://www.reddit.com/r/Widener/search/?q=computer+science+professor |
| 6 | Reddit — CS classes at Widener | Thread(s) discussing CS classes  | https://www.reddit.com/r/Widener/search/?q=CS+classes |
| 7 | Reddit — Widener CS course difficulty/workload | Thread(s) on course difficulty & workload (verify thread exists) | https://www.reddit.com/r/Widener/search/?q=computer+science+hard+workload |
| 8 | Widener CS & CIS Department | Official faculty directory / department page | https://www.widener.edu/profile/computer-science-computer-information-systems-department |
| 9 | Widener Computer Science, BS | Official course catalog / program requirements | https://catalog.widener.edu/preview_program.php?catoid=50&poid=8000 |
| 10 | StudentsReview — Widener CS | Aggregated student reviews/comments on the CS program | http://www.studentsreview.com/undergraduate.php3?MAJOR_NAME=Computer+Science&PID=12&UID=1222 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->
    

**Chunk size:** 400 characters maximum per chunk (`max_chunk_size=400` in my `chunk_text()` function). Instead of cutting blindly at 400 characters, I split the text on sentence boundaries first and then pack whole sentences into a chunk until adding the next one would exceed 400 characters. If a single sentence is somehow longer than 400 characters on its own, a fallback hard-splits it so it can't overflow.

**Overlap:** 1 sentence. My `overlap` parameter is measured in *sentences*, not characters — when I start a new chunk I carry over the last sentence of the previous chunk. (Note: this differs from the "~50 characters" I wrote in my first draft above; in the actual implementation overlap is sentence-based, which fits review text better since it keeps a whole idea intact instead of slicing mid-word.)

**Reasoning:** My corpus is short student reviews where each sentence usually expresses one opinion ("tough grader," "explains clearly," "gives lots of homework"). Splitting on sentence boundaries keeps those opinions whole, and the 400-character cap is large enough to hold a full thought (a few short sentences) while staying small enough that retrieval stays precise and unrelated opinions don't get mixed into the same chunk. Carrying over 1 sentence of overlap preserves context when a reviewer's point spans two sentences, so a chunk boundary doesn't strand the second half of an idea. In practice this produced 21 clean chunks across my 5 source files.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** I'm using `all-MiniLM-L6-v2` through `sentence-transformers` (loaded with LangChain's `HuggingFaceEmbeddings`). It runs locally on my machine, so it needs no API key and costs nothing to embed all my chunks. It produces 384-dimensional vectors, which are small and fast to search in FAISS. For short, opinion-style review text, its accuracy is more than good enough — in my retrieval tests it correctly pulled the right professor for queries like "Which professor is the easiest?"

**Top-k:** 3. My retriever uses similarity search with `k=3` (`search_kwargs={"k": 3}`). Because my chunks are short single-topic reviews, the top 3 usually give the LLM enough supporting evidence to answer without flooding the prompt with off-topic comments. If I find answers are missing context, I can raise k to 4–5; if I see off-topic chunks sneaking in, I can lower it.

**Production tradeoff reflection:** If I were deploying this for real students and cost wasn't a constraint, I'd weigh a few things before swapping in a bigger embedding model (e.g. OpenAI `text-embedding-3-large` or Cohere `embed-v3`):
- **Accuracy on domain-specific text:** Review slang ("he yaps," "straight up the goat," "tough grader") is informal. A larger model trained on more varied text would likely capture that tone and sarcasm better, reducing the risk of misreading a negative review as positive.
- **Context length:** MiniLM truncates at ~256 tokens, so if I move to longer documents (full Reddit threads instead of single reviews) I'd want a model with a larger input window so chunks don't get silently cut off.
- **Multilingual support:** Not important for my current corpus (all English), but a multilingual model would matter if I expanded to international-student forums.
- **Latency:** A hosted API model adds a network round-trip per query and depends on their uptime, whereas MiniLM is instant and offline. For a responsive student-facing app I'd weigh that latency (and rate limits) against the accuracy gain.

For this project the tradeoff lands in MiniLM's favor — free, local, fast, and accurate enough for short reviews. I'd only upgrade if I scaled up to longer or messier documents where retrieval quality started to slip.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->
    
| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which CS professor at Widener is known for tough grading? | The system should identify the professor most frequently described as a tough grader in the reviews (e.g., "Professor X is consistently described as strict and assigns heavy workloads."). |
| 2 | Which professor is praised for clear explanations? | The system should name the professor most often associated with clarity in teaching (e.g., "Professor Y is repeatedly mentioned as explaining concepts clearly."). |
| 3 | Which professor gives the most homework? | The system should identify the professor whose reviews mention heavy homework loads the most. |
| 4 | Which professor is the most supportive or approachable? | The system should return the professor most frequently described as helpful, supportive, or approachable in student comments. |
| 5 | What do students say about the difficulty of CS courses overall? | The system should summarize common themes (e.g., "Students say CS courses are challenging but fair, with difficulty depending heavily on the professor."). |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.There are a few things that could go wrong with my system. First, some of the documents I’m using might be noisy or inconsistent. Student reviews can be sarcastic, exaggerated, or just unclear, so the model might misunderstand the tone and pull the wrong meaning from them. This could lead to answers that don’t really match what the reviews were actually saying.

2.Another issue is that the retriever might grab off‑topic chunks. For example, if someone asks about which professor is the hardest, the system might accidentally return comments about unrelated things like classroom conditions or parking. This would make the final answer less accurate.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
                     [ Document Loader (Python) ]
                           │
                           ▼
              [ Chunking Function (AI-assisted) ]
                           │
                           ▼
        [ Embedding Generator (Groq Embedding Model) ]
                           │
                           ▼
            [ Vector Store (FAISS - Python Library) ]
                           │
                           ▼
        [ Retriever Function (AI-assisted Python code) ]
                           │
                           ▼
       [ LLM Answer Generation (Groq LLM / RAG Pipeline) ]

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->will use AI tools to help implement during Milestone 3 and 4:

I will use AI tools in a targeted way to help implement each part of my RAG pipeline. For loading documents and generating embeddings, I will use Claude by giving it the relevant sections of my planning.md so it can produce functions that read my .txt files, chunk them according to my chosen size and overlap, and embed them using MiniLM. I will verify these steps by printing sample outputs and checking vector dimensions. For building the FAISS vector store and retriever, I will again use Claude to generate the setup code, then confirm correctness by reloading the index and testing retrieval on sample queries. For assembling the full RAG pipeline with Groq’s Llama‑3 model, I will provide Claude with my retrieval requirements so it can create a working qa_chain, which I will test using my evaluation questions. Finally, I will use Copilot to help write a small evaluation script that runs multiple queries through the pipeline, and I will verify the results by comparing them to the expected answers in my Evaluation Plan.

**Milestone 3 — Ingestion and chunking:**
In this milestone, I built the ingestion pipeline that loads my raw text files and splits them into meaningful chunks. I implemented a document loader that reads all .txt files from the data/ folder, then applied my chosen chunking strategy (size 400, overlap 50) to break the documents into overlapping segments that preserve context. I verified this step by printing sample chunks and confirming the overlap and boundaries were correct. By the end of Milestone 3, I had a clean list of text chunks ready for embedding.

**Milestone 4 — Embedding and retrieval:**
For Milestone 4, I generated embeddings for all chunks using MiniLM (HuggingFaceEmbeddings), then stored them in a FAISS vector index. I saved the index to a vectorstore/ directory and confirmed it loaded correctly by checking that the number of vectors matched the number of chunks. I then created a retriever configured to return the top‑k most similar chunks for any query. I tested retrieval with sample questions to ensure the correct professor reviews were being returned. By the end of this milestone, my retrieval system was fully functional.

**Milestone 5 — Generation and interface:**
in Milestone 5, I connected my retriever to an LLM to complete the RAG pipeline. I used Groq’s Llama‑3 model, authenticated through my .env file, and combined it with my FAISS retriever using LangChain’s RetrievalQA chain. I verified the full pipeline by asking several questions and confirming that the answers were grounded in the retrieved source documents. I then built a simple Streamlit interface (app.py) that lets users enter a question, see the generated answer, and view the supporting chunks. This completed the end‑to‑end RAG system.