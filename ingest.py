import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

DATA_FOLDER = "data"
INDEX_FOLDER = "faiss_index"

# ── Check data folder ─────────────────────────────────────────────────────────
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    print(f"❌ Created '{DATA_FOLDER}/' folder — it is empty!")
    print("👉 Add your PDF or TXT career documents inside the 'data/' folder and run this script again.")
    exit()

files = os.listdir(DATA_FOLDER)
if not files:
    print(f"❌ The '{DATA_FOLDER}/' folder is empty!")
    print("👉 Add your PDF or TXT career documents inside the 'data/' folder and run this script again.")
    exit()

print(f"📂 Found files in data/: {files}")

# ── Load documents ────────────────────────────────────────────────────────────
documents = []

# Load PDFs
pdf_loader = DirectoryLoader(DATA_FOLDER, glob="**/*.pdf", loader_cls=PyPDFLoader)
documents += pdf_loader.load()

# Load TXT files
txt_loader = DirectoryLoader(DATA_FOLDER, glob="**/*.txt", loader_cls=TextLoader)
documents += txt_loader.load()

if not documents:
    print("❌ No PDF or TXT files could be loaded. Check your files.")
    exit()

print(f"✅ Loaded {len(documents)} document(s).")

# ── Split into chunks ─────────────────────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"✅ Split into {len(chunks)} chunks.")

# ── Create embeddings and save FAISS index ────────────────────────────────────
print("⏳ Creating embeddings (this may take a minute on first run)...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local(INDEX_FOLDER)

print(f"✅ FAISS index saved to '{INDEX_FOLDER}/' — You are ready to run the app!")
