import csv
import pytest
import tempfile
import hashlib

from langchain_core.documents import Document

import load_csv
from dialog_lib.db.models import CompanyContent

from unittest.mock import MagicMock, Mock, patch


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

def test_documents_to_company_content():
    # Create a mock Document object
    doc = Document(
        page_content="This is a test content.",
        metadata={
            "category": "test_category",
            "subcategory": "test_subcategory",
            "question": "test_question",
            "dataset": "test_dataset",
            "link": "http://test_link"
        }
    )
    
    # Define a mock embedding
    embedding = [0.1] * 1536  # Example embedding

    # Call the function to test
    company_content = load_csv.documents_to_company_content(doc, embedding)

    # Check that the output is as expected
    assert company_content.category == "test_category"
    assert company_content.subcategory == "test_subcategory"
    assert company_content.question == "test_question"
    assert company_content.content == "This is a test content."
    assert company_content.embedding == embedding
    assert company_content.dataset == "test_dataset"
    assert company_content.link == "http://test_link"

def test_get_csv_cols(csv_file: str):
    columns = load_csv._get_csv_cols(csv_file)
    expected_columns = ["category", "subcategory", "question", "content", "dataset"]
    assert columns == expected_columns

def test_get_document_pk():
    # Create a mock Document object
    doc = Document(
        page_content="This is a test content.",
        metadata={
            "category": "test_category",
            "subcategory": "test_subcategory",
            "question": "test_question",
            "dataset": "test_dataset",
            "link": "http://test_link"
        }
    )
    
    # Define the fields to be used for primary key generation
    pk_metadata_fields = ["category", "subcategory", "question"]

    # Call the function to test
    pk = load_csv.get_document_pk(doc, pk_metadata_fields)

    # Manually create the expected hash
    concatened_fields = "test_categorytest_subcategorytest_question"
    expected_pk = hashlib.md5(concatened_fields.encode()).hexdigest()

    # Check that the output is as expected
    assert pk == expected_pk

def test_load_csv_with_metadata(csv_file: str):
    metadata_columns = ["category", "subcategory", "question", "dataset"]
    embed_columns = ["content"]
    
    # Call the function to test
    docs = load_csv.load_csv_with_metadata(csv_file, embed_columns, metadata_columns)

    # Check that the output is as expected
    assert len(docs) == 2
    assert docs[0].page_content == "content: content1"
    assert docs[0].metadata == {
        "category": "cat1",
        "subcategory": "subcat1",
        "question": "q1",
        "dataset": "dataset1",
        "content": "content1",
    }
    assert docs[1].page_content == "content: content2"
    assert docs[1].metadata == {
        "category": "cat2",
        "subcategory": "subcat2",
        "question": "q2",
        "dataset": "dataset2",
        "content": "content2",
    }

def test_retrieve_docs_from_vectordb(mocker):
    # Create mock CompanyContent objects
    mock_company_contents = [
        CompanyContent(
            id=1,
            category="cat1",
            subcategory="subcat1",
            question="What is cat1?",
            content="Content for cat1",
            embedding="0.1 0.2 0.3",  # Mock embedding data
            dataset="dataset1",
            link="http://link1"
        ),
        CompanyContent(
            id=2,
            category="cat2",
            subcategory="subcat2",
            question="What is cat2?",
            content="Content for cat2",
            embedding="0.4 0.5 0.6",  # Mock embedding data
            dataset="dataset2",
            link="http://link2"
        )
    ]

    # Mock the query and its all() method
    mock_query: Mock = mocker.patch("load_csv.session")
    load_csv.session.query.return_value.all.return_value = mock_company_contents

    # Call the function to test
    docs = load_csv.retrieve_docs_from_vectordb()

    # Check that the output is as expected
    assert len(docs) == 2
    assert docs[0].page_content == "Content for cat1"
    assert docs[0].metadata == {
        "category": "cat1",
        "subcategory": "subcat1",
        "question": "What is cat1?"
    }
    assert docs[1].page_content == "Content for cat2"
    assert docs[1].metadata == {
        "category": "cat2",
        "subcategory": "subcat2",
        "question": "What is cat2?"
    }
