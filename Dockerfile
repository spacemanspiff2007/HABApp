FROM python:3.9-alpine

VOLUME [ "/config"]

# Install required dependencies
RUN apk add --no-cache \
# Support for Timezones
    tzdata \
# ujson won't compile without these libs
    g++

# Always use latest versions
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .

# Install
RUN pip3 install .

CMD [ "python", "-m", "HABApp", "--config", "/config" ]
