# Pull base image
FROM python:3.9-alpine3.18

# Set environment variables
ENV PYTHONUNBUFFERED 1

COPY . /src
COPY ./requirements.txt /src/tmp/requirements.txt
COPY ./.env /src/.env

WORKDIR /src

RUN python -m venv /py && \
  /py/bin/pip install --upgrade pip && \
  apk add --update --no-cache postgresql-client jpeg-dev && \
  apk add --update --no-cache --virtual .tmp-build-deps \
  build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
  /py/bin/pip install --no-cache-dir -r tmp/requirements.txt && \
  rm -rf /root/.cache/
RUN pip install psycopg2-binary

ENV PYTHONPATH "/py/lib/python3.x/site-packages:$PYTHONPATH"

RUN /py/bin/pip list

ENV PATH="/py/bin:$PATH"

EXPOSE 5222

CMD ["python", "main.py"]