FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
ENTRYPOINT ./.docker/entrypoint.sh $DB_NAME $DB_USER $DB_PASSWORD $DB_IP_ADDRESS $DB_PORT $DB_ENGINE
