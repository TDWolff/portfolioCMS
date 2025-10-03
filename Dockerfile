FROM docker.io/python:3.11

WORKDIR /app

# --- [Install python and pip] ---
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip git

# Copy application files
COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Create instances directory with proper permissions
RUN mkdir -p /app/instances && chmod 755 /app/instances

ENV GUNICORN_CMD_ARGS="--workers=1 --bind=0.0.0.0:8454"

EXPOSE 8454

# Define environment variable
ENV FLASK_ENV=production

CMD [ "gunicorn", "main:app" ]