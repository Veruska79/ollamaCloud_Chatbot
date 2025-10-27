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
from langchain_community.document_loaders import WebBaseLoader

# .env laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Basisverzeichnis
BASE_DIR = Path(__file__).parent

# Daten- und Vektorpfade
#DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "data"))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(BASE_DIR / "vectorstores" / "db_faiss"))

# Datenverzeichnis prüfen
#if not Path(DATA_PATH).exists():
#    raise FileNotFoundError(f"Datenpfad nicht gefunden: {DATA_PATH}")

def load_urls(url_list, loader_cls=WebBaseLoader):
    if not url_list:
        logging.warning("Die URL-Liste ist leer.")
        return []

    documents = []

    def safe_load(url):
        try:
            loader = loader_cls(url)
            return loader.load()
        except Exception as e:
            logging.error(f"Fehler beim Laden von URL {url}: {e}")
            return []

    with ThreadPoolExecutor() as executor:
        results = executor.map(safe_load, url_list)
        for result in results:
            documents.extend(result)

    return documents

urls = [
    "https://www.wsl.ch/en/about-wsl.html",
    "https://www.wsl.ch/en/forest/",
    "https://www.wsl.ch/en/landscape/",
    "https://www.wsl.ch/en/biodiversity/",
    "https://www.wsl.ch/en/natural-hazards/",
    "https://www.wsl.ch/en/snow-and-ice/",
    "https://www.wsl.ch/en/about-wsl/",
    "https://www.wsl.ch/en/about-wsl/projects/?show=100"    
]

# Hauptfunktion: Vektor-Datenbank erstellen
def func_build_vector_db():
    docs = load_urls(urls)
    if not docs:
        raise ValueError("Keine Dokumente gefunden. Ingest-Vorgang abgebrochen.")

    # Dokumente in Chunks aufteilen
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=500)
    texts = text_splitter.split_documents(docs)
       

    # Embeddings initialisieren (CPU-basiert, multilingual)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
    )
    
    

    # FAISS-Vektordatenbank erstellen und speichern
    db = FAISS.from_documents(texts, embeddings)
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    db.save_local(VECTOR_DB_PATH)
    logging.info(f"✅ Vektordatenbank gespeichert unter: {VECTOR_DB_PATH}")

# Einstiegspunkt
if __name__ == "__main__":
    func_build_vector_db()
