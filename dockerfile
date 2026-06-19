FROM ghcr.io/astral-sh/uv:alpine3.23

COPY . /usr/Pro5t-Bot
WORKDIR /usr/Pro5t-Bot

RUN uv sync

CMD [ "uv", "run", "bot.py" ]
