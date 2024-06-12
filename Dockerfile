FROM python:3.12.3-slim
LABEL org.opencontainers.image.source https://github.com/talkdai/dialog
LABEL org.opencontainers.image.licenses MIT

RUN useradd --user-group --system --create-home --no-log-init talkd
RUN export PATH="/home/talkd/.local/bin:$PATH"

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=on
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1

USER talkd
WORKDIR /app

COPY poetry.lock pyproject.toml README.md /app/
COPY pytest.ini /app/src/

USER root
RUN pip install -U pip poetry

RUN  poetry config virtualenvs.create false && \
    poetry install --only main

USER talkd

COPY /static /app/static
COPY /etc /app/etc
COPY /src /app/src

USER root

RUN chmod +x /app/etc/run.sh
RUN chmod +x /app/etc/run-tests.sh

WORKDIR /app/src

CMD [ "/app/etc/run.sh" ]
