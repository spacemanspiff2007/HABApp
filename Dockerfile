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

# Install from pip (we don't use that in the github actions because
# the new version might not be available on pypi yet)
# RUN pip3 install habapp

# Install from checked out git branch
RUN pip3 install .

# Start HABApp
CMD [ "python", "-m", "HABApp", "--config", "/config" ]
