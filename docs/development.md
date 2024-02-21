# Dialog API Development

We are very glad that you are interested in developing and helping our project to become successful.

## Good practices

We like well organized code (sometimes we fail in this, but we are improving), so in order to help you do a successful PR we are writing this doc.

Our coding style try to follow as much as possible from PEP8 and we use `black` and `isort` to fix coding styling issues.

## Local Development setup

We've used Python and bundled packages with `poetry`, now it's up to you - ⚠️ we're not yet at the point of explaining in depth how to develop and contribute, [`Makefile`](Makefile) may help you and also reading our [current issues](https://github.com/talkdai/dialog/issues).

> **notes:** we recommend using `docker-compose` to develop the project or please proceed with setting up the local environment at **your own risk**.

### Creating new/altering tables or columns

We use alembic to manage migrations inside our application, so if you need to create new tables or columns, you will need to run the following command:

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

## VS Code Dev Container

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

## Running Tests

Running tests on the project is simple, just add the flag `TEST=true` to the .env file/environment variables and run the project.

```bash
docker-compose up -d db # run the database
docker-compose up -d dialog # run the api
```

Right now our coverage is pretty limited, we would like to have more code covered as soon as possible.
