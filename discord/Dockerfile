# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /usr/src/app

# Install any needed packages specified in requirements.txt
# We are also installing the gcc compiler and other build tools
# that are required to build aiohttp from source
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Python dependencies
# You could add --no-cache-dir if you want to keep the docker image size down
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python3", "main.py"]
