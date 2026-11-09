# ============================================================
# RAG Assistant — Module 6 Étape 3
# Connecte le LLM à la documentation technique du projet
# ============================================================

import os
import sys
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "qwen/qwen3.8-27b"

# ── ChromaDB (base vectorielle locale) ───────────────────────
CHROMA_PATH = "ai_assistant/rag/chroma_db"
COLLECTION_NAME = "infra_docs"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn,
)

DOCS_EXTENSIONS = {".md", ".yaml", ".yml", ".txt", ".py"}
DOCS_EXCLUDE = {
    ".venv", "__pycache__", ".git", "airflow/logs",
    "chroma_db", "node_modules"
}


def should_index(path: Path) -> bool:
    """Vérifie si le fichier doit être indexé."""
    for excluded in DOCS_EXCLUDE:
        if excluded in str(path):
            return False
    return path.suffix in DOCS_EXTENSIONS


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Découpe le texte en chunks avec chevauchement."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def index_project(project_root: str = "."):
    """Indexe tous les fichiers du projet dans ChromaDB."""
    root = Path(project_root)
    files_indexed = 0
    chunks_indexed = 0

    print(f"\n Indexation du projet : {root.resolve()}")

    # Vider la collection existante
    existing = collection.count()
    if existing > 0:
        print(f"  Réinitialisation ({existing} chunks existants)")
        chroma_client.delete_collection(COLLECTION_NAME)
        collection2 = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )
    else:
        collection2 = collection

    for file_path in root.rglob("*"):
        if not file_path.is_file() or not should_index(file_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue

            chunks = chunk_text(content)
            rel_path = str(file_path.relative_to(root))

            ids = [f"{rel_path}::chunk{i}" for i in range(len(chunks))]
            metadatas = [{"source": rel_path, "chunk": i} for i in range(len(chunks))]

            collection2.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas,
            )

            files_indexed += 1
            chunks_indexed += len(chunks)
            print(f" {rel_path} ({len(chunks)} chunks)")

        except Exception as e:
            print(f"  Ignoré {file_path}: {e}")

    print(f"\n Indexation terminée : {files_indexed} fichiers, {chunks_indexed} chunks\n")
    return collection2


def search_docs(query: str, n_results: int = 4) -> list:
    """Cherche les chunks les plus pertinents."""
    coll = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )
    results = coll.query(
        query_texts=[query],
        n_results=min(n_results, coll.count()),
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    return list(zip(docs, metas))


def ask_rag(question: str) -> str:
    """Répond à une question en utilisant le contexte du projet."""
    chunks = search_docs(question)

    if not chunks:
        return " Aucun document indexé. Lancez d'abord : python rag_assistant.py --index"

    context = "\n\n---\n\n".join([
        f"[{meta['source']}]\n{doc}"
        for doc, meta in chunks
    ])

    prompt = f"""Tu es un assistant expert sur cette infrastructure.
Réponds à la question en te basant UNIQUEMENT sur la documentation fournie.
Si la réponse n'est pas dans la documentation, dis-le clairement.

Documentation :
{context}

Question : {question}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=800,
    )
    return response.choices[0].message.content


def main():
    if "--index" in sys.argv:
        index_project(".")
        print(" Index prêt. Relancez sans --index pour poser des questions.\n")
        return

    coll = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )
    if coll.count() == 0:
        print(" Aucun document indexé. Lancez d'abord :")
        print("   python ai_assistant/rag/rag_assistant.py --index\n")
        return

    print("\n" + "=" * 60)
    print(" RAG Assistant — Documentation du projet")
    print(f"   {coll.count()} chunks indexés")
    print("=" * 60)
    print("Posez vos questions sur l'infrastructure (quit pour quitter)\n")

    while True:
        try:
            question = input("Question > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not question or question == "quit":
            break

        print("\n Réponse >\n")
        print(ask_rag(question))
        print()


if __name__ == "__main__":
    main()
