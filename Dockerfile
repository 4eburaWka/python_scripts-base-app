FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8080

ENTRYPOINT [ "entrypoint.sh" ]
