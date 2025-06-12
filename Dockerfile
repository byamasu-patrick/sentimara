# Use the official Python 3.10 image as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc build-essential wkhtmltopdf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of your application's code into the container
COPY . /app/

# Expose the port that your FastAPI app will run on
EXPOSE 8000

# Command to run your FastAPI application using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
