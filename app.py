import streamlit as st
from rag import qa_chain

st.set_page_config(page_title="Unofficial Guide Chatbot")

st.title("🎓 The Unofficial Guide — RAG Chatbot")
st.write("Ask a question based on your student review documents.")

query = st.text_input("Enter your question:")

if st.button("Ask"):
    if query.strip() == "":
        st.warning("Please enter a question.")
    else:
        result = qa_chain.invoke(query)

        st.subheader("Answer")
        st.write(result["result"])

        st.subheader("Sources")
        for doc in result["source_documents"]:
            st.markdown(f"**Source:** {doc.metadata.get('source', 'unknown')}")
            st.write(doc.page_content)
            st.write("---")
