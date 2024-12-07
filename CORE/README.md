# CORE Docker Images

### CORE 7.5.2

This is an older version, used in the professors' VM.

```
$ docker build -t core-7.5.2 .
$ ./core.sh
```

To download things outside of CORE (e.g.: setting up a Python venv), you can use `./core.sh --term`.

### Notes

 - On the host system, `xhost` must be installed and `DISPLAY` must be set.
 - Closing CORE may take a while. This is due to Docker trying to stop the running container.
 - Your `$HOME` directory will be mounted to the container's `/mnt`.
