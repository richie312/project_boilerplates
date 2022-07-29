FROM ubuntu:latest
MAINTAINER Accenture Megatron ATCI "https://innersource.accenture.com/projects/ATCIMEXR"

RUN apt-get update \
  && apt -y upgrade \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR .

COPY . .

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
