# talkd/dialog

Humanized Conversation API (using LLM)

> conversations in a human way without exposing that it's a LLM answering

For more information you can use our [documentation](https://dialog.talkd.ai)

## Quick Start

To use this project, you need to have a `.csv` file with the knowledge base and a `.toml` file with your prompt configuration.

We recommend that you create a folder inside this project called `data` and put CSVs and TOMLs files over there.

### `.csv` knowledge base

The knowledge base must have the `document` column, with question and answer together, to build the embeddings. Other fields are optional and are metadata and can be used for better filtering later (WIP). We recommend to start with this example:

**fields:**

- category
- subcategory: used to customize the prompt for specific questions
- question
- content (question answer)
- document (question and answer together, used to build embeddings)

You can indicate metadata columns in the `.toml` configuration (see example beloew)

**example:**

```csv
category,subcategory,question,content
faq,promotions,loyalty-program,"The company XYZ has a loyalty program when you refer new customers you get a discount on your next purchase, ..."
```

These embeddings are created when `dialog` service is getting up.

### `.toml` prompt configuration

The `[prompt.header]`, `[prompt.suggested]`, and `[fallback.prompt]` fields are mandatory fields used for processing the conversation and connecting to the LLM.

The `[fallback.prompt]` field is used when the LLM does not find a compatible embedding on the database, without it, it would hallucinate on possible answers for questions outside of the scope of the embeddings.

It is also possible to add information to the prompt for subcategories and choose some optional llm parameters like temperature (defaults to 0.2) or model_name, see below for an example of a complete configuration:

```toml
[model]
temperature = 0.2
model_name = "gpt-3.5-turbo"

[prompt]
template = """You are an assistant for question-answering tasks.
Use the following pieces of retrieved context (in Documents section) to answer the question.
If you don't know the answer, just say that you don't know.
Use five sentences maximum and keep the answer concise

Act like a service operator called Avelino from XYZ, you are an expert in providing
qualified service to high-end customers. Never say that you are a model (AI), always answer as Avelino.
Be polite and friendly!

\nDocuments:
{context}\n
"""

contextualize_history_template = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

[fallback]
prompt = """I'm sorry, I didn't understand your question. Could you rephrase it?"""

[memory]
memory_size = 2

[documents]
metadata_cols = ['category', 'subcategory', 'question', 'content', 'actions']

[retriever]
top_k = 4
```

### Environment Variables

Look at the [`.env.sample`](.env.sample) file to see the environment variables needed to run the project.

There are other configurations not detailed in `.env.sample`, we recommend you to [read our documentation](https://dialog.talkd.ai/settings#environment-variables) that discusses configuration.

## Run the project

> we assume you are familiar with [Docker](https://www.docker.com/)

```bash
cp .env.sample .env # edit the .env file, add the OPENAI token and the path to the .csv and .toml files
docker-compose up
```
