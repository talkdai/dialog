import argparse
from typing import Iterable, List, Optional
import hashlib
import csv

from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.documents import Document

from dialog_lib.embeddings.generate import generate_embeddings
from dialog.llm.embeddings import EMBEDDINGS_LLM
from dialog_lib.db.models import CompanyContent
from dialog.db import get_session
from dialog.settings import Settings

import logging

logging.basicConfig(
    level=Settings().LOGGING_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("make_embeddings")

session = next(get_session())
NECESSARY_COLS = ["category", "subcategory", "question", "content"]
PK_METADATA_COLS = ["category", "subcategory", "question"]


def _get_csv_cols(path: str) -> List[str]:
    """Gets the csv columns from a csv file"""
    with open(path) as f:
        reader = csv.DictReader(f)
        return reader.fieldnames


def retrieve_docs_from_vectordb() -> List[Document]:
    """Retrieve all documents from the vector store."""
    company_contents: List[CompanyContent] = session.query(CompanyContent).all()
    return [
        Document(
            page_content=content.content,
            metadata={
                "category": content.category,
                "subcategory": content.subcategory,
                "question": content.question,
            },
        )
        for content in company_contents
    ]


def documents_to_company_content(doc: Document, embedding: float) -> CompanyContent:
    """Transform each langchain's Document and its embedding to a CompanyContent object."""
    return CompanyContent(
        category=doc.metadata.get("category"),
        subcategory=doc.metadata.get("subcategory"),
        question=doc.metadata.get("question"),
        content=doc.page_content,
        embedding=embedding,
        dataset=doc.metadata.get("dataset"),
        link=doc.metadata.get("link"),
    )

def get_document_pk(doc: Document, pk_metadata_fields: Iterable[str]) -> str:
    """Construct a primary key with defined metadata fields"""
    fields = [doc.metadata[field] for field in pk_metadata_fields]
    concatened_fields = "".join(fields)
    return hashlib.md5(concatened_fields.encode()).hexdigest()

def load_csv_with_metadata(
    path: str,
    embed_columns: list[str] = [],
    metadata_columns: List[str] = [],
) -> List[Document]:
    """Load CSV twice, once with specific metadata columns and once with all NECESSARY_COLS"""

    # Load the CSV once to get metadata columns
    loader_metadata = CSVLoader(path, metadata_columns=metadata_columns)
    docs_metadata: List[Document] = loader_metadata.load()

    # Load the CSV again to get all NECESSARY_COLS as metadata
    loader_necessary = CSVLoader(path, metadata_columns=NECESSARY_COLS)
    docs_necessary: List[Document] = loader_necessary.load()

    # Merge documents to ensure all necessary columns are included as metadata
    merged_docs = []
    not_used_metadata_fields = ["row", "source"]
    for doc_meta, doc_necessary in zip(docs_metadata, docs_necessary):
        merged_metadata = {**doc_meta.metadata, **doc_necessary.metadata}
        merged_metadata = {k: v for k, v in merged_metadata.items() if k not in not_used_metadata_fields}
        merged_doc = Document(
            page_content=doc_meta.page_content, metadata=merged_metadata
        )
        merged_docs.append(merged_doc)

    return merged_docs


def load_csv_and_generate_embeddings(
    path, cleardb=False, embed_columns: Optional[list[str]] = None
):
    """
    Load the knowledge base CSV, get their embeddings and store them into the vector store.
    """
    if not embed_columns:
        embed_columns = ["content"]
    metadata_columns = [col for col in _get_csv_cols(path) if col not in embed_columns]
    docs: List[Document] = load_csv_with_metadata(path, embed_columns, metadata_columns)

    logger.info("Metadata columns: %s", metadata_columns)
    logger.info("Embedding columns: %s", embed_columns)
    logger.info("Glimpse over the first doc: %s", docs[0].page_content[:100])

    for col in NECESSARY_COLS:
        if col not in metadata_columns + embed_columns:
            raise Exception(f"Column {col} not found in {path}")

    if cleardb:
        logging.info("Clearing vectorstore completely...")
        session.query(CompanyContent).delete()
        session.commit()

    # Get existing docs
    docs_in_db: List[Document] = retrieve_docs_from_vectordb()
    logging.info(f"Existing docs: {len(docs_in_db)}")
    existing_pks: List[str] = [
        get_document_pk(doc, PK_METADATA_COLS) for doc in docs_in_db
    ]

    # Keep only new keys
    docs_filtered: List[Document] = [
        doc
        for doc in docs
        if get_document_pk(doc, PK_METADATA_COLS) not in existing_pks
    ]
    if len(docs_filtered) == 0:
        return

    logging.info("Generating embeddings for new questions...")
    logging.info(f"New questions: {len(docs_filtered)}")
    logging.info(f"embed_columns: {embed_columns}")

    embedded_docs = generate_embeddings(
        [doc.page_content for doc in docs_filtered],
        embedding_llm_instance=EMBEDDINGS_LLM,
    )
    company_contents: List[CompanyContent] = [
        documents_to_company_content(doc, embedding)
        for (doc, embedding) in zip(docs_filtered, embedded_docs)
    ]
    session.add_all(company_contents)
    session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=False, default="./know.csv")
    parser.add_argument("--cleardb", action="store_true")
    parser.add_argument("--embed-columns", default="content")
    args = parser.parse_args()

    load_csv_and_generate_embeddings(
        args.path, args.cleardb, args.embed_columns.split(",")
    )
