import argparse

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores.pgvector import PGVector

from dialog.settings import COLLECTION_NAME, DATABASE_URL, PROJECT_CONFIG

DEFAULT_METADATA_COLUMNS = PROJECT_CONFIG.get("documents").get("metadata_cols")

def make_embeddings(path: str):
    loader = CSVLoader(path, metadata_columns=DEFAULT_METADATA_COLUMNS)
    docs = loader.load()

    store = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=DATABASE_URL,
    embedding_function=OpenAIEmbeddings(),
    )
    # TODO: add only new documents using a hash of the document for comparison
    store.add_documents(docs, pre_delete_collection=True) 
    print(f"Added {len(docs)} documents to the store.")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=False, default="./know.csv")
    args = parser.parse_args()

    make_embeddings(args.path)
