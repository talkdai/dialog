import argparse
import hashlib

import pandas as pd
from sqlalchemy import text

from dialog_lib.embeddings.generate import generate_embeddings
from dialog.llm.embeddings import EMBEDDINGS_LLM
from dialog_lib.db.models import CompanyContent
from dialog.db import get_session

session = next(get_session())

def load_csv_and_generate_embeddings(path, cleardb=False, embed_columns=("content",)):
    df = pd.read_csv(path)
    necessary_cols = ["category", "subcategory", "question", "content"]
    for col in necessary_cols:
        if col not in df.columns:
            raise Exception(f"Column {col} not found in {path}")

    if "dataset" in df.columns:
        necessary_cols.append("dataset")

    df = df[necessary_cols]

    # Create primary key column using category, subcategory, and question
    df["primary_key"] = df["category"] + df["subcategory"] + df["question"]
    df["primary_key"] = df["primary_key"].apply(
        lambda row: hashlib.md5(row.encode()).hexdigest()
    )

    if cleardb:
        session.query(CompanyContent).delete()
        session.commit()

    df_in_db = pd.read_sql(
        text(
            f"SELECT category, subcategory, question, content, dataset FROM {CompanyContent.__tablename__}"
        ),
        session.get_bind(),
    )

    # Create primary key column using category, subcategory, and question for df_in_db
    new_keys = set(df["primary_key"])
    if not df_in_db.empty:
        df_in_db["primary_key"] = df_in_db["category"] + df_in_db["subcategory"] + df_in_db["question"]
        df_in_db["primary_key"] = df_in_db["primary_key"].apply(
            lambda row: hashlib.md5(row.encode()).hexdigest()
        )
        new_keys = set(df["primary_key"]) - set(df_in_db["primary_key"])

    # Filter df for keys present in df and not present in df_in_db
    df_filtered = df[df["primary_key"].isin(new_keys)].copy()

    print("Generating embeddings for new questions...")
    print("New questions:", len(df_filtered))
    if len(df_filtered) == 0:
        return

    print("embed_columns: ", embed_columns)
    df_filtered.drop(columns=["primary_key"], inplace=True)
    df_filtered["embedding"] = generate_embeddings(
        list(df_filtered[embed_columns].agg('\n'.join, axis=1)),
        embedding_llm_instance=EMBEDDINGS_LLM
    )
    df_filtered.to_sql(
        CompanyContent.__tablename__,
        session.get_bind(),
        if_exists="append",
        index=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=False, default="./know.csv")
    parser.add_argument("--cleardb", action="store_true")
    parser.add_argument("--embed-columns", default="content")
    args = parser.parse_args()

    load_csv_and_generate_embeddings(
        args.path, args.cleardb, args.embed_columns.split(','))
