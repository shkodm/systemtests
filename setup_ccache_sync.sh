#!/bin/bash

# starts rsync daemon for docker, that allows syncronizing ccache
# between host and containers during image build stage
mkdir -p $HOME/ccache

RSYNC_SERVER_IP=$( ip -4 -o addr show docker0 | awk '{print $4}' | cut -d "/" -f 1 )
RSYNC_CONFIG=$(mktemp)
cat <<EOF > "${RSYNC_CONFIG}"
[precice-docker-cache]
        path = $HOME/ccache
        comment = preCICE docker image cache
        hosts allow = 172.17.0.2
        use chroot = false
        read only = false
EOF
RSYNC_PORT=2342

# start rsync in deamon mode
rsync --port=${RSYNC_PORT} --address="${RSYNC_SERVER_IP}" --config="${RSYNC_CONFIG}" --daemon --no-detach &

CCACHE_REMOTE="rsync://${RSYNC_SERVER_IP}:${RSYNC_PORT}/precice-docker-cache"
