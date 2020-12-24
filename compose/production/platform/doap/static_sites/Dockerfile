FROM python:3.7.7-alpine3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    # psycopg2 dependencies
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    # CFFI dependencies: i have no idea what these do but allauth apparently depends on them
    && apk add libffi-dev py-cffi

RUN mkdir /code
WORKDIR /code
RUN pip install --upgrade pip

# COPY requirements.txt /code/
# RUN pip install -r requirements.txt

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/production.txt
COPY . /code/

# trigger the collectstatic via /start
COPY ./compose/production/platform/doap/start /code/start
RUN sed -i 's/\r//' /code/start
RUN chmod +x /code/start

CMD ["/code/start"]

