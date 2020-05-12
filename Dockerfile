FROM python:3.8.2-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y libpq-dev gcc netcat

COPY ./requirements /app/requirements
RUN pip install -r /app/requirements/dev.txt

RUN apt-get autoremove -y gcc

ENV USERNAME=app
ENV UID=1000
RUN addgroup --system --gid $UID $USERNAME && adduser --disabled-password --gecos '' --system --gid $UID --uid $UID $USERNAME

COPY ./entrypoint.sh /app/entrypoint.sh
COPY . /app

RUN chown -R $USERNAME:$USERNAME /app

USER $USERNAME

ENTRYPOINT ["/app/entrypoint.sh"]
