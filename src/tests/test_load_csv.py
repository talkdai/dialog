import csv
import pytest
import tempfile

import load_csv

from unittest.mock import Mock, patch


@pytest.fixture
def csv_file() -> str:
    temp_file = _create_csv()
    return temp_file


def _create_csv(
    columns: list[str] | None = None, data: list[list[str]] | None = None
) -> str:
    temp_file = tempfile.NamedTemporaryFile(
        prefix="test-dialog", suffix=".csv", delete=False
    )

    if not columns:
        columns = ["category", "subcategory", "question", "content", "dataset"]

    if not data:
        data = [
            ["cat1", "subcat1", "q1", "content1", "dataset1"],
            ["cat2", "subcat2", "q2", "content2", "dataset2"],
        ]

    with open(temp_file.name, "w", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)
    return temp_file.name


def test_load_csv(mocker, dbsession, csv_file: str):
    mock_generate_embeddings: Mock = mocker.patch("load_csv.generate_embeddings")
    mock_generate_embeddings.return_value = [
        [0.1] * 1536,
        [0.2] * 1536,
    ]  # 1536 is the expected dimension of the embeddings

    load_csv.load_csv_and_generate_embeddings(csv_file, cleardb=True)

    result = dbsession.query(load_csv.CompanyContent).all()
    assert len(result) == 2


def test_multiple_columns_embedding(mocker, dbsession, csv_file: str):
    mock_generate_embeddings: Mock = mocker.patch("load_csv.generate_embeddings")
    mock_generate_embeddings.return_value = [
        [0.1] * 1536,
        [0.2] * 1536,
    ]  # 1536 is the expected dimension of the embeddings

    load_csv.load_csv_and_generate_embeddings(
        csv_file, cleardb=True, embed_columns=["category", "subcategory", "content"]
    )

    mock_generate_embeddings.assert_called_with(
        [
            "category: cat1\nsubcategory: subcat1\ncontent: content1", 
            "category: cat2\nsubcategory: subcat2\ncontent: content2"
        ],
        embedding_llm_instance=load_csv.EMBEDDINGS_LLM,
    )


def test_clear_db(mocker, dbsession, csv_file: str):
    mock_generate_embeddings: Mock = mocker.patch("load_csv.generate_embeddings")
    mock_generate_embeddings.return_value = [
        [0.1] * 1536,
        [0.2] * 1536,
    ]  # 1536 is the expected dimension of the embeddings

    load_csv.load_csv_and_generate_embeddings(csv_file, cleardb=True)
    initial_run = dbsession.query(load_csv.CompanyContent).all()

    load_csv.load_csv_and_generate_embeddings(csv_file, cleardb=True)
    clear_db_run = dbsession.query(load_csv.CompanyContent).all()

    other_csv_file = _create_csv(
        data=[
            ["cat3", "subcat3", "q3", "content3", "dataset3"],
            ["cat4", "subcat4", "q4", "content4", "dataset4"],
        ]
    )
    load_csv.load_csv_and_generate_embeddings(other_csv_file, cleardb=False)
    dont_clear_db_run = dbsession.query(load_csv.CompanyContent).all()

    assert len(initial_run) == 2
    assert len(clear_db_run) == 2
    assert len(dont_clear_db_run) == 4


def test_ensure_necessary_columns():
    with pytest.raises(Exception):
        load_csv.load_csv_and_generate_embeddings(
            _create_csv(
                columns=["category", "subcategory", "question"],
                data=[["cat1", "subcat1", "q1"]],
            ),
            cleardb=True,
        )  # missing content column
