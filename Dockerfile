FROM ubuntu:20.04

# Set environment variables
ENV PYTHONUNBUFFERED 1
# Install necessary dependencies
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  postgresql-client \
  libjpeg-dev \
  build-essential \
  libpq-dev \
  zlib1g-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install Solana CLI tools using wget
RUN sh -c "$(curl -sSfL https://release.solana.com/v1.18.1/install)"

# Add Solana binaries to PATH
ENV PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"


COPY . /src
COPY ./requirements.txt /src/tmp/requirements.txt
COPY ./.env /src/.env

WORKDIR /src

RUN python3 -m venv /py && \
  /py/bin/pip install --upgrade pip

# RUN apt-get update && apt-get install -y \
#   postgresql-client \
#   libjpeg-dev \
#   build-essential \
#   libpq-dev \
#   zlib1g-dev \
#   && rm -rf /var/lib/apt/lists/*

RUN /py/bin/pip install --no-cache-dir -r tmp/requirements.txt
RUN pip install psycopg2-binary

ENV PYTHONPATH "/py/lib/python3.x/site-packages:$PYTHONPATH"

RUN /py/bin/pip list

ENV PATH="/py/bin:$PATH"

EXPOSE 5222
CMD ["python", "main.py"]