# Dialog

Humanized Conversation API (using LLM)

> conversations in a human way without exposing that it's a LLM answering

## Settings

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

The `[fallback.prompt]` field is used when the LLM does not find a compatible embedding on the database, without it, it would hallucinate on possible answers for questions outside of the scope of the embeddings.

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

[prompt.subcategory.loyalty-program]

header = """The client is interested in the loyalty program, and needs to be responded to in a
salesy way; the loyalty program is our growth strategy."""

[fallback]
prompt = """I'm sorry, I didn't understand your question. Could you rephrase it?"""
```

### Environment Variables

Look at the [`.env.sample`](.env.sample) file to see the environment variables needed to run the project.

## Run the project

> we assume you are familiar with [Docker](https://www.docker.com/)

```bash
cp .env.sample .env # edit the .env file, add the OPENAI token and the path to the .csv and .toml files
docker compose up
```

> **notes:** `DIALOG_DATA_PATH` and `PROJECT_CONFIG` the file path for this variable should prefixed with `/app/` _(mounted folder of the software)_.

After uploading the project, go to the documentation `http://localhost:8000/docs` to see the API documentation.

### Docker

The **dialog** docker image is distributed in [GitHub Container Registry](https://github.com/orgs/talkdai/packages/container/package/dialog) with the tag `latest`.

**image:** `docker pull ghcr.io/talkdai/dialog:latest`

### dev container

If you are using VSCode, you can use the [devcontainer](.devcontainer) to run the project.

When we upload the environment into devcontainer, we upload the following containers:

- `db`: container with the postgres database with **pgvector** extension
- `dialog`: container with the api (the project)

We don't upload the application when the container is started. To upload the application, run the `make run` command inside the container console (bash).

> Remember to generate the embedding vectors and create the `.env` file based on the `.env.sample` file before uploading the application.

```sh
make load-data path="know-base-path.csv"
make run
```

### local development

We've used Python and bundled packages with `poetry`, now it's up to you - ⚠️ we're not yet at the point of explaining in depth how to develop and contribute, [`Makefile`](Makefile) may help you.

> **notes:** we recommend using `docker-compose` to develop the project or please proceed with setting up the local environment at **your own risk**.

#### Creating new/altering tables or columns

If you need to create new tables or columns, you need to run the following command:

```bash
docker compose exec web alembic revision --autogenerate
```

Then, with the generated file already modified with the operations you would like to perform, run the following command:

```bash
docker compose exec web alembic upgrade head
```

In order to the newly created table become available in SQLAlchemy, you need to add the following lines to the file `src/models/__init__.py`:

```python
class TableNameInSingular(Base):
    __table__ = Table(
        "your_db_table_name",
        Base.metadata,
        psql_autoload=True,
        autoload_with=engine,
        extend_existing=True
    )
    __tablename__ = "your_db_table_name"
```

## Extending the default LLM

This project uses as a base LLM implementation the class ChatOpenAI from Langchain. If you want to extend the default LLM, you can create a new class that inherits from AbstractLLM (located in the file src/llm/abstract_llm.py) and override the methods you want to change and add behavior.

To use your custom LLM, just add the environment variable LLM_CLASS to your .env file/environment variables:

```
LLM_CLASS=plugins.my_llm.MyLLMClass
```

If you don't implement your own LLM model or your model doesn't inherit the class from AbstractLLM, the default LLM will be used by default.

## Adding extra routes to the project

The project is extensible and can support extra endpoints. To add new endpoints, you need to create a package inside the `src/plugins` folder and, inside the new package folder, add the following file:

- `__init__.py`: the default package initializer from Python (this file can be empty), but we recommend you to create the router here.

Inside the `__init__.py` file, you need to create a FastAPI router that will be loaded into the app dynamically:

```python
from fastapi import APIRouter

router = APIRouter()

# add your routes here
```

The variable that instantiates APIRouter must be called **router**.

After creating the plugin, to run it, add the environment variable PLUGINS to your .env file:

```bash
PLUGINS=plugins.your_plugin_name # or PLUGINS=plugins.your_plugin_name.file_name if there is another file to be used as entrypoint
```

### WhatsApp Text to Audio Synthesis

We already made a WhatsApp plugin that converts the LLM processed output from the message an user sent, into an audio file and sends it back to the user.

To use this plugin, you need to clone the [WhatsApp Audio Synth repo](https://github.com/talkdai/whats_audio_synth) inside the plugins folder of this repo and add the following environment variables to your .env file:

```bash
WHATSAPP_API_TOKEN=
WHATSAPP_ACCOUNT_NUMBER=
PLUGINS=plugins.whats_audio_synth.main,
```

### Tests

Running tests on the project is simple, just add the flag `TEST=true` to the .env file/environment variables and run the project.

```bash
docker-compose up -d db # run the database
docker-compose up -d dialog # run the api
```
