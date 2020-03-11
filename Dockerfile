FROM python:3.8-alpine

VOLUME [ "/config"]

# Install required dependencies
RUN apk add --no-cache \
# Support for Timezones
    tzdata \
# ujson because we don't want to compile ourselves
    py3-ujson

# Always use latest versions
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .

# Install
RUN pip3 install .

CMD [ "python", "-m", "HABApp", "--config", "/config" ]
