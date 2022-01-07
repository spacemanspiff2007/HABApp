FROM python:3.9-alpine as buildimage

COPY . /tmp/app_install

ENV GOSU_VERSION=1.14 

RUN set -eux;\
	apk add --no-cache \
# gosu install dependencies
		ca-certificates \
		dpkg \
		gnupg \
# ujson won't compile without these libs
		g++; \
# download gosu
	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
	wget -O /root/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
	wget -O /root/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
# verify the signature
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
	gpg --batch --verify /root/gosu.asc /root/gosu; \
	command -v gpgconf && gpgconf --kill all || :; \
# wheel all packages for habapp
	cd /tmp/app_install; \
	pip wheel --wheel-dir=/root/wheels .

FROM python:3.9-alpine

COPY --from=buildimage /root/wheels /root/wheels
COPY --from=buildimage /root/gosu /usr/local/bin/gosu
COPY container/entrypoint.sh /entrypoint.sh

ENV HABAPP_HOME=/habapp \
    USER_ID=9001 \
    GROUP_ID=9001

RUN set -eux; \
# Install required dependencies
 	apk add --no-cache \
    	bash \
# Support for Timezones
    	tzdata; \
    mkdir -p ${HABAPP_HOME}; \
    mkdir -p ${HABAPP_HOME}/config; \
# install HABApp
    pip3 install \
        --no-index \
        --find-links=/root/wheels \
		habapp; \
# prepare entrypoint script
    chmod +x /entrypoint.sh /usr/local/bin/gosu;
	
WORKDIR ${HABAPP_HOME}
VOLUME ["${HABAPP_HOME}/config"]
ENTRYPOINT ["/entrypoint.sh"]

CMD ["gosu", "habapp", "python", "-m", "HABApp", "--config", "/habapp/config"]
