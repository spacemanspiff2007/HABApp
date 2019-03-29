FROM python:3.7-alpine

VOLUME [ "/config"]

WORKDIR /usr/src/app

# ujson won't compile without these libs
RUN apk add --no-cache \
   musl-dev \
   gcc

RUN pip3 install HABApp

CMD [ "python", "-m", "HABApp", "--config", "/config" ]
