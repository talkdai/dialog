# talkd/dialog

For programmers, who are interested in AI who are deploying RAGs without knowledge on server maintenance, Dialog is an App to simplify LLM deploys, letting you spend less time coding and more time training your model.

This repository serves an API focused on letting you deploy any LLM you want, based on the structure provided by [dialog-lib](https://github.com/talkdai/dialog-lib).

We started as a way to humanize RAGs, but we are expanding for broader approaches on better RAG deployment and maintenance.

For more information, check our [documentation](https://dialog.talkd.ai)!

## Running the project

We assume you are familiar with [Docker](https://www.docker.com/), if you are not, this [amazing tutorial](https://www.youtube.com/watch?v=pTFZFxd4hOI&ab_channel=ProgrammingwithMosh) will help you. Follow the [Quick Start](##quick-start) for setup and then run

```bash
docker-compose up
```
it will start two services: 
- `db`: where the PostgresSQL database runs to support chat history and document retrieval for [RAG](https://en.wikipedia.org/wiki/Prompt_engineering#Retrieval-augmented_generation);
- `dialog`: the service with the api.

## Quick Start

To use this project, you need to have a `.csv` file with the knowledge base and a `.toml` file with your prompt configuration.

We recommend that you create a folder inside this project called `data` and put CSVs and TOMLs files over there.

### `.csv` knowledge base

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

See [our documentation](https://dialog.talkd.ai/settings#csv-knowledge-base) for more options about the the knowledge base, including embedding more coluns together.


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

suggested = "Here is some possible content 
that could help the user in a better way."

fallback = "I'm sorry, I couldn't find a relevant answer for your question."

fallback_not_found_relevant_contents = "I'm sorry, I couldn't find a relevant answer for your question."

[prompt.subcategory.loyalty-program]

header = """The client is interested in the loyalty program, and needs to be responded to in a
salesy way; the loyalty program is our growth strategy."""
```

### Environment Variables

Look at the [`.env.sample`](.env.sample) file to see the environment variables needed to run the project. While the `.csv` contains only the knowledge base, the `.toml` contains some llm parameters and prompts, and finally the `.env` contains the OpenAI token, paths and some project parameters. We recommend you to [read our documentation](https://dialog.talkd.ai/settings#environment-variables) that discusses configuration.

## Maintainers

We are thankful for all of the contributions we receive, mostly are reviewed by this awesome maintaining team we have:

 - [avelino](https://github.com/avelino)
 - [vmesel](https://github.com/vmesel)
 - [walison17](https://github.com/walison17)
 - [lgabs](https://github.com/lgabs/)

made with 💜 by [talkd.ai](https://talkd.ai)
