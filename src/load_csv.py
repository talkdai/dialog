import argparse

import pandas as pd
from llm import generate_embeddings
from models import CompanyContent
from models.db import session
from sqlalchemy import text
import hashlib

def load_csv_and_generate_embeddings(path):
    df = pd.read_csv(path)
    necessary_cols = ["category", "subcategory", "question", "content"]
    for col in necessary_cols:
        if col not in df.columns:
            raise Exception(f"Column {col} not found in {path}")

    df = df[necessary_cols]

    # Create primary key column using category, subcategory, and question
    df["primary_key"] = df.apply(lambda row: hashlib.md5(
        (
            row["category"] + row["subcategory"] + row["question"]
        ).encode()).hexdigest(), axis=1)

    df_in_db = pd.read_sql(
        text(f"SELECT category, subcategory, question, content FROM {CompanyContent.__tablename__}"),
        session.get_bind()
    )

    # Create primary key column using category, subcategory, and question for df_in_db
    df_in_db["primary_key"] = df_in_db.apply(
        lambda row: hashlib.md5(
            (
                row["category"] + row["subcategory"] + row["question"]
            ).encode()).hexdigest(), axis=1)

    # Filter df for keys present in df and not present in df_in_db
    df_filtered = df[~df["primary_key"].isin(df_in_db["primary_key"])]

    print("Generating embeddings for new questions...")
    print("New questions:", len(df_filtered))

    df_filtered.drop(columns=["primary_key"], inplace=True)
    df_filtered["embedding"] = generate_embeddings(df_filtered["content"])
    df_filtered.to_sql(
        CompanyContent.__tablename__,
        session.get_bind(),
        if_exists="append",
        index=False
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=False,
                        default="./know.csv")
    args = parser.parse_args()

    load_csv_and_generate_embeddings(args.path)
