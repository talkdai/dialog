FROM python:3.11-slim

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=on
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
	apt-get install --no-install-recommends -yq \
  postgresql-client \
  openssh-client \
  iputils-ping \
  vim && \
  apt-get autoremove -y && apt-get clean -y

COPY . /workspace
COPY .devcontainer/bashrc /root/.bashrc

WORKDIR /workspace

RUN pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install

RUN createdb -h localhost -U talkdai -w -e test_talkdai