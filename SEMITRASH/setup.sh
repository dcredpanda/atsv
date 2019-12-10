#!/usr/bin/env bash

: '
Script works on Ubuntu 16.04 & Ubuntu 14.04
Installation script for docker
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04
'

sudo apt-get remove -y docker docker-engine docker.io

if [ "$(lsb_release -r -s)" == "14.04" ]; then
    sudo apt-get -y update
    sudo apt-get install -y linux-image-extra-$(uname -r) linux-image-extra-virtual
fi

sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update -y
sudo apt-get install -y docker-ce
sudo curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo groupadd docker
sudo usermod -aG docker $USER