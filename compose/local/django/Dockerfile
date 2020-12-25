FROM python:3.8.5-alpine3.12

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

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt
COPY . /code/

COPY ./compose/production/tech/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

ENTRYPOINT ["/entrypoint"]