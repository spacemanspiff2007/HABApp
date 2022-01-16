# Docker

## Basic usage

### Pulling image

```bash
docker pull spacemanspiff2007/habapp:latest
```

### Preparing config directory and running HABApp container

```bash
mkdir -p habapp_config

docker run --rm -it --name habapp \
    -v ${PWD}/habapp_config:/habapp/config \
    -e TZ=Europe/Berlin \
    -e USER_ID=9001 \
    -e GROUP_ID=9001 \
    spacemanspiff2007/habapp:latest
```

Parameters explained:
* `--rm` Remove container when stopped
* `-it` Run in interactive mode (Optional) -> You can stop HABApp by pressing STRG+C
* `--name habapp` Give the container an unique name to interact with it
* `-e TZ=Europe/Berlin` give a valid timezone
* `-e USER_ID=9001` User id at which HABApp will run (Optional, default: 9001)
* `-e GROUP_ID=9001` Group id at which HABApp will run (Optional, default: USER_ID)
* `spacemanspiff2007/habapp:latest` Name of the image used

### Stopping container and upgrading

```bash
docker stop habapp

docker pull spacemanspiff2007/habapp:latest
```

### View logs

Add a logging.yml to your configuration directory which makes HABApp to log to stdout you will see the logs when running with parameter `-it` or by running command:

```bash
docker logs -f
```

## Advanced usage

If you want to use some additional python libraries you can do this by writing your own Dockerfile using this image as base image.
Our image is based on the python-slim image so you can install packages by using apt and pip.

Example Dockerfile installing scipy, pandas and numpy libraries:

```Dockerfile
FROM spacemanspiff2007/habapp:latest as buildimage

RUN set -eux; \
# Install required build dependencies (Optional)
	apt-get update; \
	DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
		build-essentials; \
# Prepare python packages
	pip3 wheel \
        --wheel-dir=/root/wheels \
        scipy pandas numpy

FROM spacemanspiff2007/habapp:latest

COPY --from=buildimage /root/wheels /root/wheels

RUN set -eux; \
# Install required runtime dependencies (Optional)
	apt-get update; \
	DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
		bash; \
	apt-get clean; \
	rm -rf /var/lib/apt/lists/*; \
# Install python packages and cleanup
	pip3 install \
    	--no-index \
    	--find-links=/root/wheels \
        scipy pandas numpy; \
	rm -rf /root/wheels
```

Build your image:

```bash
docker build -t my_habapp_extended:latest .
```

Run your container like basic usage by replacing image name `spacemanspiff2007/habapp:latest` by `my_habapp_extended:latest`

```bash
docker run --rm -it --name habapp \
    -v ${PWD}/habapp_config:/habapp/config \
    -e TZ=Europe/Berlin \
    -e USER_ID=9001 \
    -e GROUP_ID=9001 \
    my_habapp_extended:latest
```