# syntax=docker/dockerfile:1


ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1


ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y wget

# Download and extract Vale
RUN wget https://github.com/errata-ai/vale/releases/download/v3.0.7/vale_3.0.7_Linux_64-bit.tar.gz \
    && mkdir /opt/vale \
    && tar -xvzf vale_3.0.7_Linux_64-bit.tar.gz -C /opt/vale \
    && rm vale_3.0.7_Linux_64-bit.tar.gz


# Add Vale to PATH
ENV PATH="/opt/vale:${PATH}"

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


WORKDIR /docs

COPY ./docs .
COPY app.py .


# Run the application.
CMD python app.py
