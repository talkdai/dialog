# dialog

Humanized Conversation API (using LLM)

> proportional conversation in a human way without exposing that you are an LLM answering

## Configurantions

To use the project, you need to have the `.csv` file with the knowledge base and the `.toml` file with the prompt configuration.

### `.csv` knowledge base

**fields:**

- category
- subcategory: used to customize the prompt for specific questions
- question
- content: used to generate the embeding

**example:**

```csv
category,subcategory,question,content
faq,promotions,loyalty-program,"The company XYZ has a loyalty program when you refer new customers you get a discount on your next purchase, ..."
```

### `.toml` prompt configuration

The `[prompt.header]` and `[prompt.suggested]` fields are mandatory fields used for processing the conversation and connecting to LLM.
It is also possible to add information to the prompt for subcategories, see below for an example of a complete configuration:

```toml
[prompt]
header = """You are a service operator called Avelino from XYZ, you are an expert in providing
qualified service to high-end customers. Be brief in your answers, without being long-winded
and objective in your responses. Never say that you are a model (AI), always answer as Avelino.
Be polite and friendly!"""

suggested = "Here is some possible content that could help the user in a better way."

[prompt.subcategory.loyalty-program]

header = """The client is interested in the loyalty program, and needs to be responded to in a
salesy way; the loyalty program is our growth strategy."""
```

### environment variables

Look at the [`.env.example`](.env.example) file to see the environment variables needed to run the project.

## Run the project

> we assume you are familiar with [Docker](https://www.docker.com/)

```bash
cp .env.example .env # edit the .env file, add the OPENAI token and the path to the .csv and .toml files
docker compose up
```

After uploading the project, go to the documentation `http://localhost:8000/docs` to see the API documentation.

### local development

We've used python and bundled packages with `poetry`, now it's up to you - ⚠️ we're not yet at the point of explaining in depth how to develop and contribute, [`Makefile`](Makefile) can help.
