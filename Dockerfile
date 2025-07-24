FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/golang-migrate/migrate/releases/download/v4.17.1/migrate.linux-amd64.tar.gz | tar xvz \
    && mv migrate /usr/local/bin/migrate \
    && chmod +x /usr/local/bin/migrate

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]