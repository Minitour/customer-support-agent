"""Startup ingestion helpers — runs only if collections are empty."""
import json
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.core.config import settings
from app.vectorstore.client import get_chroma_client

EMBEDDING_MODEL = "text-embedding-3-small"
POLICY_COLLECTION = "policy"
PRODUCTS_COLLECTION = "products"


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )


def get_policy_vectorstore() -> Chroma:
    client = get_chroma_client()
    return Chroma(
        client=client,
        collection_name=POLICY_COLLECTION,
        embedding_function=_get_embeddings(),
    )


def get_products_vectorstore() -> Chroma:
    client = get_chroma_client()
    return Chroma(
        client=client,
        collection_name=PRODUCTS_COLLECTION,
        embedding_function=_get_embeddings(),
    )


async def ingest_policy_if_empty(policy_dir: str) -> None:
    vs = get_policy_vectorstore()
    existing = vs.get(limit=1)
    if existing["ids"]:
        return

    policy_path = Path(policy_dir)
    if not policy_path.exists():
        return

    docs: list[Document] = []
    for md_file in sorted(policy_path.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if text.strip():
            docs.append(Document(page_content=text, metadata={"source": md_file.name}))

    if not docs:
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    vs.add_documents(chunks)
    print(f"[ingestion] Indexed {len(chunks)} policy chunks from {len(docs)} files.")


async def ingest_products_if_empty(products_json: str) -> None:
    vs = get_products_vectorstore()
    existing = vs.get(limit=1)
    if existing["ids"]:
        return

    if not os.path.exists(products_json):
        print(f"[ingestion] Products JSON not found: {products_json}")
        return

    with open(products_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])
    if not products:
        return

    docs: list[Document] = []
    for p in products:
        text = f"{p['title']}\n{p.get('description', '')}"
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "product_id": str(p["id"]),
                    "category": p.get("category", ""),
                    "brand": p.get("brand", ""),
                    "price": str(p.get("price", 0)),
                },
            )
        )

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        vs.add_documents(chunks[i : i + batch_size])

    print(f"[ingestion] Indexed {len(chunks)} product chunks for {len(products)} products.")
