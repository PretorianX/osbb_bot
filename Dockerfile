# Use a more recent official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install dependencies from requirements.txt and clean up in one layer to keep the image size small
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && \
    apt-get install -y cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and set permissions for the crontab file
COPY osbb_bot_cron /etc/cron.d/osbb_bot_cron
RUN chmod 0644 /etc/cron.d/osbb_bot_cron && \
    crontab /etc/cron.d/osbb_bot_cron

# Run the command on container startup
CMD ["cron", "-f"]
