#!/usr/bin/env /bin/sh

WORKDIR=$PWD

# install docker, docker-compose on ubuntu
install() {

    # install curl
    sudo apt install curl

    # add gpg key
    yes | curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

    # add repository to apt resources
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update

    # install docker ce
    sudo apt-get install -y docker-ce

    # install docker-compose
    sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
}

build() {
    cd $WORKDIR && docker build . -t kdds:nlg
}

# (re)start docker stack
run() {
    cd $WORKDIR && docker run -d --name nlg -p 8300:8300 kdds:nlg
}

"$@"
