# talkd/dialog

Humanized Conversation API (using LLM)

> conversations in a human way without exposing that it's a LLM answering

For more information, check our [documentation](https://dialog.talkd.ai)!

## Quick Start

To use this project, you need to have a `.csv` file with the knowledge base and a `.toml` file with your prompt configuration.

We recommend that you create a folder inside this project called `data` and put CSVs and TOMLs files over there.

### `.csv` knowledge base

**fields:**

- category
- subcategory: used to customize the prompt for specific questions
- question
- content: used to generate the embedding

**example:**

```csv
category,subcategory,question,content
faq,promotions,loyalty-program,"The company XYZ has a loyalty program when you refer new customers you get a discount on your next purchase, ..."
```

To load the knowledge base into the database, make sure the database is up and then, inside `src` folder, run `make load-data path="../data/know.csv"` (or pass another path to you .csv).

### `.toml` prompt configuration

The `[prompt.header]`, `[prompt.suggested]`, and `[fallback.prompt]` fields are mandatory fields used for processing the conversation and connecting to the LLM.

The `[prompt.fallback]` field is used when the LLM does not find a compatible embedding in the database; that is, the `[prompt.header]` **is ignored** and the `[prompt.fallback]` is used. Without it, there could be hallucinations about possible answers to questions outside the scope of the embeddings.

> In `[prompt.fallback]` the response will be processed by LLM. If you need to return a default message when there is no recommended question in the knowledge base, use the `[prompt.fallback_not_found_relevant_contents]` configuration in the `.toml` *(project configuration)*.

It is also possible to add information to the prompt for subcategories and choose some optional llm parameters like temperature (defaults to 0.2) or model_name, see below for an example of a complete configuration:

```toml
[model]
temperature = 0.2
model_name = "gpt-3.5-turbo"

[prompt]
header = """You are a service operator called Avelino from XYZ, you are an expert in providing
qualified service to high-end customers. Be brief in your answers, without being long-winded
and objective in your responses. Never say that you are a model (AI), always answer as Avelino.
Be polite and friendly!"""

suggested = "Here is some possible content that could help the user in a better way."

fallback = "I'm sorry, I couldn't find a relevant answer for your question."

fallback_not_found_relevant_contents = "I'm sorry, I couldn't find a relevant answer for your question."

[prompt.subcategory.loyalty-program]

header = """The client is interested in the loyalty program, and needs to be responded to in a
salesy way; the loyalty program is our growth strategy."""
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
