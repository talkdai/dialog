# Quick Start

## Running the project

We recommend you use the **docker `compose`** version to set up your environment, as this will simplify the process of setting up the environment and all its dependencies, you just need to **copy and paste** our docker `compose` available below:

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

> to avoid the risk of using an outdated version of `﻿compose`, we recommend that you get the `﻿yaml` from the main source [here](https://github.com/talkdai/dialog/blob/main/docker-compose.yml).

Your `.env` file should have the following keys:

```
DATABASE_URL=postgresql://talkdai:talkdai@pgvector/talkdai
OPENAI_API_KEY=sk-KEY_HERE
DIALOG_DATA_PATH=/data/your-knowledge-base.csv
PROJECT_CONFIG=/data/your-prompt-config.toml
```

> we recommend using the [`.env.sample`](https://github.com/talkdai/dialog/blob/main/.env.sample) file; it probably contains all the variables necessary to set up your environment.

### `pgvector` - Postgres

We use the [pgvector](https://github.com/pgvector/pgvector) extension of PostgreSQL to generate embeddings of questions and answers. If you are setting up PostgreSQL outside docker `compose`, you need to enable the pgvector extension.

```psql
CREATE EXTENSION IF NOT EXISTS pgvector;
```

### Docker

The **dialog** docker image is distributed in [GitHub Container Registry](https://github.com/orgs/talkdai/packages/container/package/dialog) with the tag `latest`.

**image:** `ghcr.io/talkdai/dialog:latest`
