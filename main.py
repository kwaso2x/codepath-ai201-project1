import os
import re
import sys
from langchain_community.embeddings import HuggingFaceEmbeddings



# Windows consoles default to cp1252, which can't print the curly quotes and
# non-breaking hyphens scraped from the review sites. Force UTF-8 output.
sys.stdout.reconfigure(encoding="utf-8")


def _hard_split(sentence, max_chunk_size):
    """Fallback: break a single oversized sentence into char-sized pieces
    so it never silently overflows a downstream token limit."""
    return [
        sentence[i:i + max_chunk_size]
        for i in range(0, len(sentence), max_chunk_size)
    ]


def chunk_text(text, max_chunk_size=400, overlap=1):
    """Split text into chunks on sentence boundaries.

    max_chunk_size is measured in characters. overlap is the number of
    trailing sentences carried into the next chunk to preserve context.
    """
    # Naive sentence split: good enough for clean review prose, but it will
    # over-split on abbreviations/decimals (e.g. "Mr.", "3.5"). Swap in
    # nltk.sent_tokenize / spaCy later if the corpus needs it.
    sentences = re.split(r'(?<=[.!?]) +', text.strip())

    # Break any single sentence that's already over the limit, so it can't
    # become an oversized chunk.
    expanded = []
    for sentence in sentences:
        if len(sentence) > max_chunk_size:
            expanded.extend(_hard_split(sentence, max_chunk_size))
        else:
            expanded.append(sentence)
    sentences = expanded

    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        # +1 accounts for the space that joins sentences.
        if current_chunk and current_len + len(sentence) + 1 > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            # Guard the overlap=0 case: list[-0:] is the WHOLE list, not [].
            current_chunk = current_chunk[-overlap:] if overlap > 0 else []
            current_len = sum(len(s) + 1 for s in current_chunk)

        current_chunk.append(sentence)
        current_len += len(sentence) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


folder = "data"

for file in os.listdir(folder):
    if file.endswith(".txt"):
        print(f"\n--- {file} ---\n")
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            text = f.read()
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                print(f"--- Chunk {i + 1} ---")
                print(chunk)
# -----------------------------
# BUILD FULL RAG PIPELINE BELOW
# -----------------------------

# 1. Load all documents into memory
documents = []
for file in os.listdir(folder):
    if file.endswith(".txt"):
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            documents.append(f.read())

# 2. Chunk all documents
all_chunks = []
for doc in documents:
    all_chunks.extend(chunk_text(doc))

print(f"\nTotal chunks: {len(all_chunks)}")

# 3. Create embeddings (CodePath-recommended MiniLM model — runs locally, no API key)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. Build FAISS vector store
from langchain_community.vectorstores import FAISS
vectorstore = FAISS.from_texts(all_chunks, embeddings)

# 5. Save vector store
vectorstore.save_local("vectorstore")

# 6. Test retrieval
query = "Which professor is the easiest?"
results = vectorstore.similarity_search(query, k=3)

print("\n--- Retrieval Test ---\n")
for r in results:
    print(r.page_content)
    print("-----")
