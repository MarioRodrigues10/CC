#!/bin/sh

exit_handler() {
    trap - EXIT
    rm -f "$CONTAINER_PATH"
    docker stop "$CONTAINER_NAME"
    exit
}

xhost +local:root || exit 1

CONTAINER_PATH="$(mktemp)"
CONTAINER_NAME="$(basename "$CONTAINER_PATH")"
trap 'exit_handler' EXIT TERM INT HUP

docker run -itd --rm                               \
    --name "$CONTAINER_NAME"                       \
    -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "$HOME:/mnt"                                \
    --privileged                                   \
    core-7.5.2

ENTRY_POINT="core-gui"
[ "$1" = "--term" ] && ENTRY_POINT="qterminal -e bash"
docker exec -it "$CONTAINER_NAME" $ENTRY_POINT
