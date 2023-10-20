FROM ubuntu:latest

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

COPY . .

EXPOSE 5400

RUN pip install -r requirements.txt


CMD [ "python3","main.py" ]