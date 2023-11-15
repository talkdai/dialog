import argparse

import pandas as pd

from llm import generate_embeddings
from models import CompanyContent
from models.db import session

from sqlalchemy import text

def load_csv_and_generate_embeddings(path):
    df = pd.read_csv(path)
    necessary_cols = ["question", "content"]
    for col in necessary_cols:
        if col not in df.columns:
            raise Exception(f"Column {col} not found in {path}")

    df = df[necessary_cols]

    df_in_db = pd.read_sql(
        text(f"SELECT question, content FROM {CompanyContent.__tablename__}"),
        session.get_bind()
    )

    df = df[~df["question"].isin(df_in_db["question"])]

    print("Generating embeddings for new questions...")
    print("New questions:", len(df))

    df["embedding"] = generate_embeddings(df["content"])
    df.to_sql(
        CompanyContent.__tablename__,
        session.get_bind(),
        if_exists="append",
        index=False
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=False, default="/data/data.csv")
    args = parser.parse_args()

    load_csv_and_generate_embeddings(args.path)
