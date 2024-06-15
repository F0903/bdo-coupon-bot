FROM python:3.12

# Install poetry
ENV POETRY_HOME /opt/poetry
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==1.8
RUN $POETRY_HOME/bin/poetry --version

# Copy app
WORKDIR /bdo-coupon-bot
COPY discord_token .
COPY bdo_coupon_bot/ ./bdo_coupon_bot/
COPY poetry.lock .
COPY pyproject.toml .
COPY README.md .

# Install app deps
RUN $POETRY_HOME/bin/poetry install

# Install firefox
RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list
RUN apt-get update && apt-get install -y --no-install-recommends firefox

ENV DOCKER_MODE 1
CMD $POETRY_HOME/bin/poetry run python3 -m bdo_coupon_bot
