# Quick Start

## Current Architecture

The current architecture ilustraded below shows how dialog and dialog-lib serve as base abstractions that define how you deploy RAG LLM Apps with little effort. You can basically focus in maintaining and evolve your knowledge base and prompts, and if necessary you can implement your onw plugins to extend fuctionalities.

<p align="center">
    <a href="dialog-architecture.png">
        <img src="dialog-architecture.png" width="500">
    </a>
</p>

## Running the project

We recommend you use the **docker compose** deployment to set up your environment, as this will simplifies the process of setting up the environment and all its dependencies. You just need to **copy and paste** our `docker-compose.yml` available below.

```yml
version: '3.8'
services:
  pgvector:
    image: ankane/pgvector:latest
    ports:
      - 5432:5432
    environment:
      POSTGRES_USER: talkdai
      POSTGRES_PASSWORD: talkdai
      POSTGRES_DB: talkdai
    volumes:
      - ./pgvector:/var/lib/postgresql/data
      - ./db-ext-pgvector.sql:/docker-entrypoint-initdb.d/db-ext-pgvector.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -q -d talkdai -U talkdai"]
      interval: 10s
      timeout: 5s
      retries: 5
  talkd:
    image: ghcr.io/talkdai/dialog:latest
    volumes:
      - ./data:/app/src/data
    ports:
      - 8000:8000
    env_file:
      - .env
    depends_on:
      pgvector:
        condition: service_healthy
    volumes:
      - ./data:/data/
```

> to avoid the risk of using an outdated version of `docker-compose`, we recommend that you get the `yaml` from the main source [here](https://github.com/talkdai/dialog/blob/main/docker-compose.yml).

Your `.env` file should have the following keys, as shown below and also available in our [`.env.sample`](https://github.com/talkdai/dialog/blob/main/.env.sample) file.

```env
DATABASE_URL=postgresql://talkdai:talkdai@pgvector/talkdai
OPENAI_API_KEY=sk-KEY_HERE
DIALOG_DATA_PATH=/data/your-knowledge-base.csv
PROJECT_CONFIG=/data/your-prompt-config.toml
```

### `pgvector` - Postgres

We use the [pgvector](https://github.com/pgvector/pgvector) extension of PostgreSQL to generate embeddings of questions and answers. If you are setting up PostgreSQL outside docker `compose`, you need to enable the pgvector extension.

```psql
CREATE EXTENSION IF NOT EXISTS pgvector;
```

### Docker

The **dialog** docker image is distributed in [GitHub Container Registry](https://github.com/orgs/talkdai/packages/container/package/dialog) with the tag `latest`.

**image:** `ghcr.io/talkdai/dialog:latest`

### Using your custom knowledge base and prompt settings

#### `.csv` knowledge base

The knowledge base has needed columns:

- category
- subcategory: used to customize the prompt for specific questions
- question
- content: used to generate the embedding

**Example:**

```csv
category,subcategory,question,content
faq,promotions,loyalty-program,"The company XYZ has a loyalty program when you refer new customers you get a discount on your next purchase, ..."
```

When the `dialog` service starts, it loads the knowledge base into the database, so make sure the database is up and paths are correct (see [environment variables](##environment-variables) section). Alternatively, inside `src` folder, run `make load-data path="<path-to-your-knowledge-base>.csv"`.

See [our documentation](https://dialog.talkd.ai/settings#csv-knowledge-base) for more options about the the knowledge base, including embedding more columns together.


#### `.toml` prompt configuration

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

suggested = "Here is some possible content
that could help the user in a better way."

fallback = "I'm sorry, I couldn't find a relevant answer for your question."

fallback_not_found_relevant_contents = "I'm sorry, I couldn't find a relevant answer for your question."

[prompt.subcategory.loyalty-program]

header = """The client is interested in the loyalty program, and needs to be responded to in a
salesy way; the loyalty program is our growth strategy."""
```