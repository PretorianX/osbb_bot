# Use a more recent official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Run the command on container startup
CMD ["ls"]
