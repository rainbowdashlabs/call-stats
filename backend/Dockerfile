FROM python:3.14-trixie
LABEL authors="nora"

# User Home dir
WORKDIR /root

USER root

# Installation preparations
RUN pip install pipenv

# Copy pipfiles and local dependencies
COPY Pipfile.lock Pipfile  ./

# Sync dependencies to env
RUN python -m pipenv sync

# COPY application
COPY src/ ./src
COPY docker/docker_entrypoint.sh docker_entrypoint.sh

RUN git config --global --add safe.directory '*'

ENTRYPOINT ["bash", "docker_entrypoint.sh"]

HEALTHCHECK --start-period=30s CMD pgrep -f python || exit 1
