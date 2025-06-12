# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED True
ENV APP_HOME /jmf_llm
WORKDIR $APP_HOME

# Install required system dependencies and upgrade SQLite
RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential wkhtmltopdf \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update library path
ENV LD_LIBRARY_PATH /usr/local/lib

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel

# Install Poetry
RUN pip install poetry

# Copy the project files to the container (including pyproject.toml and poetry.lock)
COPY pyproject.toml poetry.lock /jmf_llm/

# Install Python dependencies via Poetry (no dev dependencies in production)
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application files into the container
COPY . /jmf_llm/

# Expose the port on which the app will run
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]