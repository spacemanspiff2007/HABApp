FROM python:3.7-alpine

VOLUME [ "/config"]

WORKDIR /usr/src/app

RUN apk add --no-cache \
# Support for Timezones
    tzdata \
# ujson won't compile without these libs
    musl-dev \
    gcc

RUN pip3 install HABApp

CMD [ "python", "-m", "HABApp", "--config", "/config" ]
