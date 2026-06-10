import os
import sys
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# Windows consoles default to cp1252, which can't print the curly quotes/dashes
# scraped from the review sites. Force UTF-8 so printing answers never crashes.
sys.stdout.reconfigure(encoding="utf-8")

# Load GROQ_API_KEY from .env into the process environment.
load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)

# Grounded-generation prompt: this is how grounding is ENFORCED. The model is
# told to answer ONLY from the retrieved review chunks and to refuse (with a
# fixed sentence) when those chunks don't contain the answer. This is what
# stops it from using outside knowledge or hallucinating professors/opinions.
REFUSAL = "I don't have information about that in the professor reviews."

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are The Unofficial Guide, an assistant that answers questions about "
        "Widener University CS professors using ONLY the student reviews provided "
        "in the context below.\n\n"
        "Rules:\n"
        "- Use ONLY the information in the context. Do not use any outside knowledge.\n"
        "- Do not invent professors, facts, or opinions that are not in the context.\n"
        "- If the context does not contain enough information to answer the question, "
        f'reply with exactly this sentence and nothing else: "{REFUSAL}"\n\n'
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer (grounded in the reviews above):"
    ),
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},
)


def answer_query(query):
    """Run one query through the RAG pipeline and print the answer + sources."""
    response = qa_chain.invoke({"query": query})

    print("\n--- ANSWER ---\n")
    print(response["result"])

    print("\n--- SOURCES ---\n")
    for doc in response["source_documents"]:
        print(doc.page_content)
        print("-----")
    return response


def main():
    # Query interface.
    #   Input field:  a natural-language question typed at the prompt (string).
    #   Output fields: the grounded ANSWER, followed by the SOURCE chunks the
    #                  answer was drawn from.
    # If a question is passed as a command-line arg, answer it once and exit;
    # otherwise drop into an interactive loop.
    if len(sys.argv) > 1:
        answer_query(" ".join(sys.argv[1:]))
        return

    print("The Unofficial Guide — ask about Widener CS professors.")
    print("Type a question, or 'quit' / 'exit' to leave.\n")
    while True:
        try:
            query = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in {"quit", "exit", "q"}:
            break
        if not query:
            continue
        answer_query(query)
        print()


if __name__ == "__main__":
    main()
