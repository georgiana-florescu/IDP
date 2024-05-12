# Use the official Python image as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code into the container at /app
COPY . /app/

# Expose port 7000 to the outside world
EXPOSE 7000

# Command to run the FastAPI application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7000"]
