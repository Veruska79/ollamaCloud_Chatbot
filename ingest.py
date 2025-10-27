# Erstelle eine bereinigte, finale Version von ingest.py mit allen empfohlenen Anpassungen

import glob
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings

# .env load
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Basisverzeichnis
BASE_DIR = Path(__file__).parent

# Daten- und Vektorpfade
DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "data"))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(BASE_DIR / "vectorstores" / "db_faiss"))

# Datenverzeichnis prüfen
if not Path(DATA_PATH).exists():
    raise FileNotFoundError(f"Datenpfad nicht gefunden: {DATA_PATH}")

# Dateien sicher laden
def load_files(file_pattern, loader_cls):
    files = glob.glob(os.path.join(DATA_PATH, file_pattern))
    if not files:
        logging.warning(f"Keine Dateien gefunden für Muster: {file_pattern}")
        return []

    documents = []

    def safe_load(f):
        try:
            return loader_cls(f).load()
        except Exception as e:
            logging.error(f"Fehler beim Laden von {f}: {e}")
            return []

    with ThreadPoolExecutor() as executor:
        results = executor.map(safe_load, files)
        for result in results:
            documents.extend(result)
    return documents

# Unterstützte Dateitypen
LOADERS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".java": TextLoader
}

# Main function to creates a vector database
def func_build_vector_db():
    documents = []
    for ext, loader in LOADERS.items():
        documents.extend(load_files(f"*{ext}", loader))

    if not documents:
        raise ValueError("No documents found. Ingest process canceled")

    # Chunk the documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
     

    # Initialise embeddings (CPU-based, multilingual)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "mps"},
        encode_kwargs={"normalize_embeddings": True},  # cosine similarity
        #query_instruction="Represent this query for retrieving relevant documents:"
        
    )
    

    # FAISS-Vector database created and saved
    db = FAISS.from_documents(texts, embeddings)
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    db.save_local(VECTOR_DB_PATH)
    logging.info(f"✅ Vector database saved under: {VECTOR_DB_PATH}")

# Entry point for the script
if __name__ == "__main__":
    func_build_vector_db()
