FROM python:3.11

RUN pip install Flask

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENV FLASK_APP main.py

ENV FLASK_ENV development

ENTRYPOINT ["python", "main.py"]

VOLUME /app/storage

EXPOSE 5000



