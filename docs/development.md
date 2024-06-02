# Dialog API Development

We are very glad that you are interested in developing and helping our project to become successful.

## Good practices

We like well organized code (sometimes we fail in this, but we are improving), so in order to help you do a successful PR we are writing this doc.

Our coding style try to follow as much as possible from PEP8 and we use `black` and `isort` to fix coding styling issues.

## Local Development setup

We've used Python and bundled packages with `poetry`, now it's up to you - ⚠️ we're not yet at the point of explaining in depth how to develop and contribute, [`Makefile`](Makefile) may help you and also reading our [current issues](https://github.com/talkdai/dialog/issues).

> **notes:** we recommend using `docker-compose` or our `dev-container` to develop the project or please proceed with setting up the local environment at **your own risk**.

### Creating new/altering tables or columns

All of the current available database migrations and tables are handled by `alembic` inside the `dialog-lib` package, so if you need to create a new table or alter a column, you can create a new migration inside this project.

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

Running tests on the project is simple, just use our `test-build` available in Makefile.

```bash
make test-build
```

Right now our coverage is pretty limited, we would like to have more code covered as soon as possible.


## Commits

Since we are using semantic versioning on the project, we are looking forward for good commit messages and,
on those commits, we are expecting to have certain tags on minor or major updates (so we can update the version automatically).

    - #minor: for minor updates
    - #major: for major updates
    - All else will be considered a patch