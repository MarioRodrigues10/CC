FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt

# Install essential packages
RUN apt update  -y                                                                   && \
    apt upgrade -y                                                                   && \
    apt install -y --no-install-recommends                                              \
        ca-certificates qterminal wireshark firefox                                     \
        wget git sudo                                                                   \
        iproute2 iputils-ping iperf3 traceroute                                         \
        python3 python3-pip python3-tk python3-venv                                     \
        software-properties-common                                                      \
        build-essential autoconf pkg-config m4 libtool automake gawk libreadline-dev && \
        apt clean

# Install CORE
ENV PATH="$PATH:/root/.local/bin"
RUN wget https://github.com/coreemu/core/archive/refs/tags/release-7.5.2.tar.gz && \
    tar xzf release-7.5.2.tar.gz && \
    cd core-release-7.5.2 && \
    pip3 install --user pipx && \
    pipx ensurepath && \
    pipx install invoke && \
    inv install -v -l && \
    cd .. && rm -rf core-release-7.5.2 release-7.5.2.tar.gz

# Apply configuration
RUN mkdir "/root/.core"
COPY "prefs.conf" "/root/.core"

# Project's Python version
RUN add-apt-repository -y ppa:deadsnakes/ppa                          && \
    apt update -y                                                     && \
    apt install -y --no-install-recommends python3.12 python3.12-venv

# Cleanup
RUN apt purge -y                                                        \
    wget git                                                            \
    gcc build-essential autoconf pkg-config m4 libtool automake gawk    \
    python3-pip                                                         \
    libreadline-dev                                                  && \
    apt autoremove -y

# Preparation for user
WORKDIR /root
ENTRYPOINT core-daemon
