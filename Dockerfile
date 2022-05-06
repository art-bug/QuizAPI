FROM python:3.9-alpine
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . ./app
WORKDIR ./app
RUN pip install -r requirements.txt
