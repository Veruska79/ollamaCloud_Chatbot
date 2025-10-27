## app.py
import chainlit as cl
from ollama import Client
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
#from dotenv import load_dotenv
import re

DB_FAISS_PATH = "vectorstores/db_faiss"
MODEL = "gpt-oss:20b-cloud"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 10

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer using ONLY the provided context. "
    "If the answer is not in the context, only say you don't know and nothing else.\n\n"
    "Even if the user insist on a question outside the context, you must just say you don't know. "
    "Cite sources by bracket number like [1], [2] next to the text that uses those sources, where appropriate."
    "At the end of your answer, if you used any sources, please list them in a 'Sources' section."
)
USER_TEMPLATE = "Question: {question}\n\nContext:\n{context}"

def build_context(docs):
    parts = []
    for i, d in enumerate(docs, 1):
        parts.append(f"[{i}] {d.metadata.get('source','')} — {d.page_content.strip()}")
    return "\n\n".join(parts)

def summarize_sources(docs, max_chars=140):
    lines = []
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "(no source)")
        preview = d.page_content.strip().replace("\n", " ")
        if len(preview) > max_chars:
            preview = preview[:max_chars] + "…"
        lines.append(f"[{i}] {src} — {preview}")
    return "\n".join(lines) if lines else "(no sources)"

@cl.on_chat_start
async def on_chat_start():
    # Build retriever once per session
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vs = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    #retriever = vs.as_retriever(search_kwargs={"k": TOP_K})
    retriever = vs.as_retriever(search_type="mmr",search_kwargs={"k": TOP_K, "fetch_k": 80, "lambda_mult": 0.7})

    client = Client()

    # Session state
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    cl.user_session.set("messages", messages)
    cl.user_session.set("retriever", retriever)
    cl.user_session.set("client", client)
    cl.user_session.set("last_docs", [])

    await cl.Message(
        content="Chat ready. Ask a question. Click **Reset** to clear history.",
        actions=[cl.Action(name="reset", value="reset", label="Reset",payload={})]
    ).send()

@cl.action_callback("reset")
async def on_reset(action: cl.Action):
    cl.user_session.set("messages", [{"role": "system", "content": SYSTEM_PROMPT}])
    cl.user_session.set("last_docs", [])
    await cl.Message(content="🔄 Conversation history cleared.").send()

@cl.on_message
async def on_message(msg: cl.Message):
    question = msg.content.strip()
    if not question:
        await cl.Message(content="Please enter a question.").send()
        return

    messages = cl.user_session.get("messages")
    retriever = cl.user_session.get("retriever")
    client: Client = cl.user_session.get("client")

    # Retrieve docs
    docs = retriever.get_relevant_documents(question)
    cl.user_session.set("last_docs", docs)
    context = build_context(docs)

    # Append user turn
    messages.append({"role": "user", "content": USER_TEMPLATE.format(question=question, context=context)})

    # Call Ollama (non-streaming for async simplicity)
    try:
        resp = client.chat(model=MODEL, messages=messages, stream=False, options={"temperature": 0.1})
        answer = resp["message"]["content"]
    except Exception as e:
        answer = f"[Error calling model: {e}]"

    # Append assistant turn
    messages.append({"role": "assistant", "content": answer})
    cl.user_session.set("messages", messages)

    # Reply and show sources
    await cl.Message(content=answer).send()
    #await cl.Message(content="**Sources**\n" + summarize_sources(docs)).send()
    #ans_low = answer.lower()
    if docs and re.search(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]", answer): #and ("don't know" not in ans_low and "not in the context" not in ans_low and "not aware"):
        await cl.Message(content="**Sources**\n" + summarize_sources(docs)).send()