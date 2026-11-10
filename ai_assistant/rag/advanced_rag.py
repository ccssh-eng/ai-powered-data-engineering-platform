# ============================================================
# Advanced RAG Assistant — Module 7
# Base documentaire + embeddings + assistant technique
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

# ── ChromaDB ─────────────────────────────────────────────────
CHROMA_PATH = "ai_assistant/rag/chroma_db_v2"
COLLECTION_NAME = "infra_docs_v2"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def get_collection():
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )


# ── Chunking intelligent ──────────────────────────────────────
def chunk_by_section(text: str, source: str) -> list:
    """Découpe par sections markdown (##) pour préserver le contexte."""
    chunks = []
    current_section = ""
    current_title = "Introduction"

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_section.strip():
                chunks.append({
                    "text": current_section.strip(),
                    "title": current_title,
                    "source": source,
                })
            current_title = line[3:].strip()
            current_section = line + "\n"
        else:
            current_section += line + "\n"

    if current_section.strip():
        chunks.append({
            "text": current_section.strip(),
            "title": current_title,
            "source": source,
        })

    return chunks


def chunk_by_words(text: str, source: str,
                   size: int = 300, overlap: int = 50) -> list:
    """Découpe par mots avec chevauchement pour fichiers non-markdown."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk_text = " ".join(words[i:i + size])
        if chunk_text.strip():
            chunks.append({
                "text": chunk_text,
                "title": f"chunk_{i}",
                "source": source,
            })
    return chunks


# ── Indexation ────────────────────────────────────────────────
EXCLUDE = {".venv", "__pycache__", ".git", "airflow/logs",
           "chroma_db", "chroma_db_v2", ".gitignore"}
TEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml"}
CODE_EXTENSIONS = {".py", ".sh"}


def should_index(path: Path) -> bool:
    for ex in EXCLUDE:
        if ex in str(path):
            return False
    return path.suffix in TEXT_EXTENSIONS | CODE_EXTENSIONS


def index_documents(project_root: str = "."):
    """Indexe tous les documents avec chunking intelligent."""
    collection = get_collection()
    root = Path(project_root)

    # Réinitialiser
    if collection.count() > 0:
        chroma_client.delete_collection(COLLECTION_NAME)
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )

    print("\n📚 Indexation avec chunking intelligent...")
    total_chunks = 0

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or not should_index(file_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue

            rel = str(file_path.relative_to(root))

            # Chunking selon le type
            if file_path.suffix == ".md":
                chunks = chunk_by_section(content, rel)
            else:
                chunks = chunk_by_words(content, rel)

            if not chunks:
                continue

            ids = [f"{rel}::{i}" for i in range(len(chunks))]
            docs = [c["text"] for c in chunks]
            metas = [{"source": c["source"], "title": c["title"],
                      "type": file_path.suffix} for c in chunks]

            collection.add(documents=docs, ids=ids, metadatas=metas)
            total_chunks += len(chunks)
            print(f"  ✅ {rel} → {len(chunks)} chunk(s)")

        except Exception as e:
            print(f"  ⚠️  {file_path.name}: {e}")

    print(f"\n📊 Total : {total_chunks} chunks indexés\n")


# ── Recherche ─────────────────────────────────────────────────
def search(query: str, n: int = 5, doc_type: str = None) -> list:
    """Recherche sémantique avec filtre optionnel par type."""
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    kwargs = {
        "query_texts": [query],
        "n_results": min(n, count),
    }
    if doc_type:
        kwargs["where"] = {"type": doc_type}

    results = collection.query(**kwargs)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]
    return list(zip(docs, metas, distances))


# ── Assistant RAG ──────────────────────────────────────────────
ASSISTANT_SYSTEM = """Tu es un assistant technique expert sur cette infrastructure.
Réponds en français, de façon précise et concise.
Base-toi UNIQUEMENT sur la documentation fournie.
Si l'information n'est pas dans la documentation, dis-le clairement.
Pour les commandes, utilise des blocs de code.
"""


def ask(question: str, verbose: bool = False) -> str:
    """Répond à une question via RAG."""
    results = search(question, n=5)

    if not results:
        return "❌ Aucun document indexé. Lancez --index d'abord."

    # Filtrer par pertinence (distance < 1.5)
    relevant = [(doc, meta, dist) for doc, meta, dist in results if dist < 1.5]

    if not relevant:
        relevant = results[:2]

    if verbose:
        print("\n📎 Sources utilisées :")
        for _, meta, dist in relevant:
            print(f"   • {meta['source']} / {meta['title']} (score: {dist:.3f})")

    context = "\n\n---\n\n".join([
        f"[{meta['source']} — {meta['title']}]\n{doc}"
        for doc, meta, _ in relevant
    ])

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ASSISTANT_SYSTEM},
            {"role": "user", "content": f"Documentation :\n{context}\n\nQuestion : {question}"}
        ],
        temperature=0.1,
        max_tokens=700,
    )
    return response.choices[0].message.content


# ── Interface interactive ──────────────────────────────────────
def print_help():
    print("\n📖 Commandes :")
    print("  /sources  — affiche les sources de la prochaine réponse")
    print("  /stats    — statistiques de la base vectorielle")
    print("  /reindex  — réindexe le projet")
    print("  quit      — quitter\n")


def show_stats():
    collection = get_collection()
    count = collection.count()
    print(f"\n📊 Base vectorielle : {count} chunks indexés")
    if count > 0:
        sample = collection.get(limit=3)
        sources = set(m["source"] for m in sample["metadatas"])
        print(f"   Exemples de sources : {', '.join(sources)}\n")


def main():
    if "--index" in sys.argv:
        index_documents(".")
        print("✅ Indexation terminée. Relancez sans --index.\n")
        return

    collection = get_collection()
    if collection.count() == 0:
        print("⚠️  Base vide. Indexation automatique...\n")
        index_documents(".")

    print("\n" + "=" * 60)
    print("🔍 Advanced RAG Assistant — Module 7")
    print(f"   {collection.count()} chunks dans la base vectorielle")
    print("=" * 60)
    print_help()

    verbose = False

    while True:
        try:
            user_input = input("Question > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input or user_input == "quit":
            break

        if user_input == "/sources":
            verbose = True
            print("   (sources affichées pour la prochaine question)")
            continue

        if user_input == "/stats":
            show_stats()
            continue

        if user_input == "/reindex":
            index_documents(".")
            continue

        print("\n🤖 Réponse >\n")
        print(ask(user_input, verbose=verbose))
        verbose = False
        print()


if __name__ == "__main__":
    main()
