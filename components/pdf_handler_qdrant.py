"""
Single-file Streamlit app that handles PDF uploads, chunks text, optionally creates embeddings
(using local sentence-transformers or an external provider placeholder), and upserts to Qdrant.

Save this as `studybuddy_singlefile_app.py` and run:
    pip install streamlit PyPDF2 numpy
    # optional for local embeddings:
    pip install sentence-transformers
    # optional for Qdrant:
    pip install qdrant-client

Run:
    streamlit run studybuddy_singlefile_app.py

This file merges the original `components/pdf_handler_qdrant.py` functionality into one page.
"""

import io
import os
import uuid
from typing import List, Tuple, Optional

import streamlit as st
from PyPDF2 import PdfReader
import numpy as np

# Try local embedding model
try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    _SENTENCE_MODEL = None

# Qdrant client
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except Exception:
    QdrantClient = None
    qmodels = None

# Defaults (can be adjusted in sidebar)
CHUNK_SIZE = 1600
CHUNK_OVERLAP = 200
EMBED_BATCH = 64
UPSERT_BATCH = 64

# Read default collection name from environment variable
DEFAULT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "studybuddy-pdfs")


def _extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            # For scanned PDFs you'd integrate OCR here (pytesseract)
            continue
    return "\n".join(texts)


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def _local_embed(texts: List[str]) -> List[List[float]]:
    """Use sentence-transformers locally."""
    if _SENTENCE_MODEL is None:
        raise RuntimeError(
            "Local sentence-transformers model not available. Install 'sentence-transformers' or configure external embedding."
        )
    embeddings = _SENTENCE_MODEL.encode(texts, show_progress_bar=False)
    return [emb.tolist() for emb in np.array(embeddings)]


def _external_embed(texts: List[str]) -> List[List[float]]:
    """
    Placeholder for external embedding provider (Gemini/Vertex/etc).
    If you want to use Gemini embeddings with GEMINI_API_KEY, implement the provider-specific HTTP call here
    and return a list of vectors (list of list of floats) with length == len(texts).
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("No GEMINI_API_KEY found in environment. Install sentence-transformers or set GEMINI_API_KEY.")
    raise NotImplementedError("External embedding function is not implemented. Implement _external_embed() for your provider.")


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Try local embedding first, then external if available."""
    try:
        return _local_embed(texts)
    except Exception as e:
        st.warning(f"Local embedding failed: {e}. Attempting external embedding...")
        return _external_embed(texts)


def upsert_to_qdrant(collection_name: str, vectors: List[List[float]], metadatas: List[dict], ids: List[str]) -> None:
    """Upsert points to Qdrant in batches. Creates collection if missing."""
    qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")

    if QdrantClient is None:
        raise RuntimeError("qdrant-client not installed. `pip install qdrant-client`")

    client_args = {"url": qdrant_url}
    if qdrant_api_key:
        client_args["api_key"] = qdrant_api_key

    client = QdrantClient(**client_args)

    # Ensure collection exists (create if missing)
    try:
        client.get_collection(collection_name)
    except Exception:
        # infer vector size from first vector (fallback 1536)
        vector_size = len(vectors[0]) if vectors else 1536
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )

    # Upsert in batches
    for i in range(0, len(vectors), UPSERT_BATCH):
        batch_vectors = vectors[i:i + UPSERT_BATCH]
        batch_ids = ids[i:i + UPSERT_BATCH]
        batch_meta = metadatas[i:i + UPSERT_BATCH]
        points = [
            qmodels.PointStruct(id=pid, vector=vec, payload=meta)
            for pid, vec, meta in zip(batch_ids, batch_vectors, batch_meta)
        ]
        client.upsert(collection_name=collection_name, points=points)


def handle_pdf_upload_ui() -> Tuple[str, Optional[str], bool]:
    """
    Streamlit UI function. Returns (combined_text_for_session, user_focus, summarize_clicked).

    - Accepts multiple PDF uploads
    - Optionally uploads chunked embeddings to Qdrant (configured in the sidebar)
    """
    st.header("StudyBuddy — PDF Uploader & Qdrant (single-file)")

    uploaded_files = st.file_uploader("Upload PDFs (you can select multiple)", type=["pdf"], accept_multiple_files=True)

    combine_area = st.empty()
    summarize_clicked = False

    # Qdrant options in sidebar
    st.sidebar.markdown("### Qdrant / Vector DB (optional)")
    qdrant_collection = st.sidebar.text_input("Collection name", value=DEFAULT_COLLECTION)
    do_qdrant = st.sidebar.checkbox("Upload chunks to Qdrant", value=False)
    chunk_size = st.sidebar.number_input("Chunk size (chars)", value=CHUNK_SIZE, min_value=200, max_value=5000, step=100)
    overlap = st.sidebar.number_input("Chunk overlap (chars)", value=CHUNK_OVERLAP, min_value=0, max_value=max(0, chunk_size - 1), step=50)

    user_focus = None

    if uploaded_files:
        all_texts = []
        for f in uploaded_files:
            raw = f.read()
            text = _extract_text_from_pdf_bytes(raw)
            title = getattr(f, "name", "uploaded_pdf")
            all_texts.append((title, text))

        st.write(f"Loaded {len(all_texts)} document(s):")
        for title, text in all_texts:
            st.write(f"- **{title}** — {len(text)} characters")

        # Chunk all docs
        all_chunks = []
        chunk_metas = []
        for title, text in all_texts:
            chunks = _chunk_text(text, chunk_size, overlap)
            for idx, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_metas.append({"source": title, "chunk_index": idx, "char_length": len(chunk)})

        # Combined preview (editable). We limit per doc preview to the first N chars to keep UI responsive.
        combined_preview = "\n\n---\n\n".join([f"# {t}\n\n{txt[:3000]}" for t, txt in all_texts])
        edited = combine_area.text_area("Combined PDF text (editable)", value=combined_preview, height=300)

        # focus input & summarize button
        user_focus = st.text_input("Focus / topic (optional)")

        if st.button("Summarize PDFs"):
            summarize_clicked = True

        # Qdrant upload flow
        if do_qdrant:
            if not all_chunks:
                st.error("No chunks found to upload. Check your PDFs or chunk settings.")
            else:
                st.info(f"Embedding and uploading {len(all_chunks)} chunks to collection `{qdrant_collection}`...")
                vectors = []
                ids = []
                metas = []
                progress = st.progress(0)
                for i in range(0, len(all_chunks), EMBED_BATCH):
                    batch = all_chunks[i:i + EMBED_BATCH]
                    batch_meta = chunk_metas[i:i + EMBED_BATCH]
                    try:
                        batch_vecs = get_embeddings(batch)
                    except Exception as e:
                        st.error(f"Embedding failed: {e}")
                        raise
                    batch_ids = [str(uuid.uuid4()) for _ in batch]
                    vectors.extend(batch_vecs)
                    ids.extend(batch_ids)
                    metas.extend(batch_meta)
                    progress.progress(min(100, int(100 * (i + EMBED_BATCH) / max(1, len(all_chunks)))))

                # Upload to Qdrant
                try:
                    upsert_to_qdrant(qdrant_collection, vectors, metas, ids)
                    st.success(f"Uploaded {len(vectors)} vectors to collection `{qdrant_collection}`.")
                except Exception as e:
                    st.error(f"Qdrant upload failed: {e}")

        return edited, user_focus, summarize_clicked

    # no uploads
    return "", None, False


def summarize_text(text: str, focus: Optional[str] = None) -> str:
    """Lightweight local summarize placeholder. Replace with an LLM call if you have one configured."""
    if not text:
        return ""
    # naive paragraph-level summary: first and last 2 paragraphs, plus focus line if present
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
    selected = paras[:2] + (paras[-2:] if len(paras) > 2 else [])
    summary = "\n\n".join(selected)
    if focus:
        summary = f"Focus: {focus}\n\n" + summary
    return summary


def main():
    st.set_page_config(page_title="StudyBuddy Single-file", page_icon="🧠", layout="wide")

    edited, user_focus, summarize_clicked = handle_pdf_upload_ui()

    if summarize_clicked:
        with st.spinner("Generating summary..."):
            summary = summarize_text(edited, user_focus)
        st.subheader("Summary")
        st.write(summary)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Tips:**\n- For scanned PDFs consider adding OCR (pytesseract).\n- Install `sentence-transformers` if you want local embeddings.\n- Set QDRANT_URL / QDRANT_API_KEY env vars to upload to a remote Qdrant.")


if __name__ == "__main__":
    main()
