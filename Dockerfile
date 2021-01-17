FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
RUN python manage.py migrate; python manage.py loaddata mock_data/dump.json
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
