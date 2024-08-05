ARG BUILDPLATFORM=linux/amd64
ARG BASE_IMAGE="binhex/arch-base"

FROM --platform=${BUILDPLATFORM} ${BASE_IMAGE}

ARG HERMES_VERSION="v1.10.1"

COPY ./etc /etc/
COPY ./bin /usr/local/bin/

RUN set -eux && \
    pacman -Syyu --noconfirm python-toml && \
    curl -sSL https://github.com/informalsystems/hermes/releases/download/${HERMES_VERSION}/hermes-${HERMES_VERSION}-x86_64-unknown-linux-gnu.tar.gz | \
    tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/* && \
    groupadd -g 1000 hermes && \
    useradd -u 1000 -g 1000 -s /bin/bash -md /hermes hermes

WORKDIR /hermes
ENTRYPOINT [ "/usr/bin/supervisord", "-c", "/etc/supervisord.conf" ]
