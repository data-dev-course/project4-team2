# Use Python 3.11 slim image as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /services/backend

# Copy local files to the container
COPY . .

# Install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# Install dependencies from Pipfile
RUN pipenv install --deploy --system

# Specify the command to run on container start
CMD ["python3.11", "entrypoint.py"]