# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
