## Build process setup

Sections `Prerequisites` and `Setup` should be done only once per build host

### Requirements

* Docker CE 20.10.0+ (https://docs.docker.com/install/)

### IMAP Lib Requirements

No specific requirements

### Prerequisites

1. `Docker` should be installed on build host following these instructions:

    https://docs.docker.com/install/linux/docker-ce/centos/#set-up-the-repository

    and

    https://docs.docker.com/install/linux/docker-ce/centos/#install-docker-ce-1

3. Add your build user into docker group (required to manage docker):

    ```
    usermod -aG docker <username>
    ```

    and relogin

4. Start Docker daemon

    ```
    systemctl enable docker
    systemctl start docker
    ```

5. Port 80 on build host should be free (stop nginx/httpd or move to different
port)

### Setup

1. Clone build repo with submodules (uw-imap is just an example - it could be
any build repo):

    ```
    git clone --recursive git@gitlab1.carrierzone.com:web-ongoing/build/uw-imap.git
    cd uw-imap
    ```

### Build process


1. Build images

    ```
    docker compose build
    ```

2. Build packages

    ```
    docker compose up -d
    ```

    command above will start all build serrvices in background. But it is possible
to run any of them or run in foreground etc

3. Wait until command `docker compose ps` returns all services in state 'Exit 0'

### Access RPM packages

1. RPM packages located inside `rpm9rocky` and `rpm9stream` volumes

### Complete build

To complete all build processes run commands:

```
docker compose down
docker compose -f rpmbuild/docker-compose.yml down
```

These commands will stop and remove all containers but not build images (see
`docker images` and `docker rmi` commands manuals)
