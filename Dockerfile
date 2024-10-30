FROM python:3.12

RUN apt-get update && \
    apt-get install -y gettext && \
    apt-get install -y nano

WORKDIR /bot

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install
COPY . .
WORKDIR /bot/ege_assistant_bot/
CMD ["/bin/bash", "../start_bot.sh"]