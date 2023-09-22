# DockerfileCopy code# Base image
FROM python:3.9.16-bullseye

# Working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update -y

# Copy the rest of the project files
COPY . .

# Expose the server port
EXPOSE 80

# Command to start the server
CMD ["python" ,"-m", "flask", "run", "--host=0.0.0.0"]