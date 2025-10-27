# 🤖 QA Bot – Chainlit + Ollama Cloud Project + gpt-oss
An interactive, locally running question-and-answer chatbot based on a Ollama’s cloud models and modern retrieval methods. 

It is operated via [Chainlit](https://www.chainlit.io/), uses [LangChain](https://www.langchain.com/) for orchestration, [FAISS](https://github.com/facebookresearch/faiss) for fast vector search and state-of-the-art open
source models on Ollama Cloud (https://docs.ollama.com/cloud#python)

---

## 🚀 Project Goals
- Development of a local QA bot that utilises PDF and source text data or web links
- Integration of a multilingual embedding model (DE/EN)
- Integration of an open source model on Ollama Cloud
- Interactive chat interface via Chainlit
- Optional: Protection against jailbreak/bypass prompts

---


## 🛠 Technologies in use

| Technology                 | Description                                                           |
|----------------------------|-----------------------------------------------------------------------|
| **Chainlit**               | UI-Framework for LLMs – makes the chat interface                      |
| **LangChain**              | Retrieval orchestration                                               |
| **FAISS**                  | Vector database for semantic search                                   |
| **Ollama Cloud**           | Allows to run large LLM from Ollama's cloud service                   |
| **HuggingFace Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2` for multilingual embeddings   |

---

## Ollama Cloud set up
 Ollama’s cloud models require an account on ollama.com. Navigate to the chat environment and run the following command in the terminal (internet connection is needed). To sign in or create an account, run:

-"ollama signin"

This will open a page in the default browser with a click button to approve

To run a cloud model, open the terminal and run your selected model:

Example: "ollama run gpt-oss:20b-cloud"

The selected model must be the same used for inference in app.py. 

## ⚙️ Config

### 1. Requirements

- Python ≥ 3.10
- macOS/Linux
- Docker Engine (optional für Container-Betrieb)
- Data:
  - `.env`
  - PDF-Data in the folder `data/`

### 2. Installation (local)

- Installation with conda:

1) Clone the repository and navigate into the project folder
2) Create the Conda environment from the provided YAML file: "conda env create -f project_langchain3.yml"
3) Activate the environment: "conda activate chainlit3"

```bash
conda env create -f project_langchain3.yml
conda activate chainlit3  
```
4) (Optional) Verify that the environment was created successfully: "conda info --envs"
```bash
conda info --envs
```
5) If dependencies are updated, you can refresh the environment at any time using: 
```bash
conda env update -f environment.yml --prune
```

- Installation with venv

```bash
pyenv install 3.12.0
pyenv virtualenv 3.12.0 chainlit
pyenv local chainlit
```
```bash
pip install chainlit
```

## 📄 `ingest.py`: build the vector database

This script processes PDF files and uses LangChain, Hugging Face Embeddings and FAISS to generate a searchable vector database from them.

### Process
1. Load files from `data/`
2. Break down into text sections
3. Create embeddings
4. Save to `vectorstores/db_faiss`

---
Alternatively:

## 📄 `web_ingest.py`: build the vector database from web links provided in the code

This script processes web pages and uses LangChain, Hugging Face Embeddings and FAISS to generate a searchable vector database from them.

### Process
1. Load webpages directly from the script
2. Break down into text sections
3. Create embeddings
4. Save to `vectorstores/db_faiss`

---


## 🧠 `app.py`: Local QA chatbot with Ollama Cloud LLM

This script loads the stored FAISS database and uses a Ollama cloud model to answer user questions.

### Included

- Loading model from Ollama Cloud
- Using LangChain Retrieval and harmony chat configuration prompt (works with latest LLMs like gpt-oss)
- Chat interface via Chainlit

## 📚 LLM Setup

- Model: "gpt-oss:20b-cloud" (or other)
- EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"`
- Embeddings: `paraphrase-multilingual-MiniLM-L12-v2`
- Retrieval: FAISS + LangChain `langchain_community.vectorstores.FAISS`
- Interface: Chainlit
-

---

## 📤 Ingest Pipeline

```bash
make ingest
```
Generate semantic vectors and store them in FAISS.

---

## 🧠 Example of Chat Interaction

```text
🧑‍💻 Question:
What are adaptation limits?

🤖 Answer:
Adaptation limits are he points beyond which further adaptation cannot fully eliminate health risks from heat.....
```

---

## 🧠 Chainlit start

```bash
# Local
python ingest.py
chainlit run app.py -w

```

---

## 📎 Licence

MIT License – feel free to use, learn and build on it 🚀
