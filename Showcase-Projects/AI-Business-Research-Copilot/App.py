# App.py

import streamlit as st
from langchain_community.llms.ollama import Ollama
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import WebBaseLoader

# ----------------------
# Streamlit Page Settings
# ----------------------
st.set_page_config(page_title="AI Business Research Copilot", layout="wide")
st.title("🧠 AI Business Research Copilot")
st.markdown(
    "Add URLs of websites to extract information and ask questions using a local AI model."
)

# ----------------------
# Sidebar - How to Use
# ----------------------
with st.sidebar:
    st.header("📖 How to Use")
    st.markdown("""
1. **Add URLs**: Enter a website URL and click **Add URL**. You can add multiple URLs.
2. **View URLs**: Click on **Current URLs** to see all added URLs.
3. **Process URLs**: Click **Process URLs** to fetch and store content from the websites.
4. **Ask Questions**: Type your question in the input box and click **Get Answer**.
5. **View Answer**: The AI will provide a concise answer based on the processed websites.
""")

# ----------------------
# Initialize Session State
# ----------------------
if "urls" not in st.session_state:
    st.session_state.urls = []

# ----------------------
# URL Input Form
# ----------------------
with st.form(key="url_form", clear_on_submit=True):
    url_input = st.text_input("Enter URL to add", placeholder="https://example.com")
    submitted = st.form_submit_button("Add URL")
    if submitted and url_input.strip():
        st.session_state.urls.append(url_input.strip())
        st.success(f"Added URL: {url_input.strip()}")

# ----------------------
# Display Added URLs
# ----------------------
with st.expander("🔗 Current URLs"):
    if st.session_state.urls:
        for i, u in enumerate(st.session_state.urls, start=1):
            st.write(f"{i}. {u}")
    else:
        st.write("No URLs added yet.")

# ----------------------
# LLM and Embeddings Setup
# ----------------------
llm = Ollama(model="llama3.2:1b")  # Local Ollama LLM
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# ----------------------
# Process URLs
# ----------------------
if st.button("Process URLs"):
    if not st.session_state.urls:
        st.warning("Please add at least one URL first!")
    else:
        all_docs = []
        for url in st.session_state.urls:
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                all_docs.extend(docs)
            except Exception as e:
                st.error(f"Failed to load {url}: {e}")

        if all_docs:
            vectordb = Chroma.from_documents(all_docs, embeddings)
            st.session_state.vectordb = vectordb
            st.success("✅ URLs processed and vector store created!")
        else:
            st.error("No documents were loaded from the URLs.")

# ----------------------
# Ask Questions Section
# ----------------------
st.subheader("Ask a Question")
user_question = st.text_input("Enter your question here", placeholder="E.g., What are the key insights?")

if st.button("Get Answer"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    elif "vectordb" not in st.session_state:
        st.warning("Please process URLs first!")
    else:
        retriever = st.session_state.vectordb.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff"
        )
        try:
            answer = qa_chain.run(user_question)
            st.success("✅ Answer generated:")
            st.write(answer)
        except Exception as e:
            st.error(f"Error while generating answer: {e}")
