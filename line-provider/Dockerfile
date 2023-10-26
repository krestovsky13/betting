FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /src


RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.6.1
ENV PATH="${PATH}:/root/.local/bin"

COPY ./pyproject.toml ./poetry.lock* /src/
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
