# Use Python 3.11 as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/services/backend/

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip3 \
    && pip3 install -r requirements.txt

COPY /src /src

# Specify the command to run on container start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]