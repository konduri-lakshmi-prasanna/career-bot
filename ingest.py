import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Paths based on your project structure
DATA_PATH = "data/"
DB_FAISS_PATH = "faiss_index/"

def build_knowledge_base():
    print("🚀 Scanning data folder...")
    
    # TextLoader specifically handles the .txt files mentioned in your structure
    # DirectoryLoader coordinates loading all file types
    pdf_loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    txt_loader = DirectoryLoader(DATA_PATH, glob='*.txt', loader_cls=TextLoader)
    
    documents = pdf_loader.load() + txt_loader.load()
    print(f"✅ Loaded {len(documents)} files.")

    # Split text into chunks so the AI can find specific sections
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, 
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(documents)

    # Create Embeddings (The 'Mathematical' version of your text)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Save to the 'faiss_index' folder shown in your screenshot
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(DB_FAISS_PATH)
    print("✨ Knowledge base is ready!")

if __name__ == "__main__":
    build_knowledge_base()