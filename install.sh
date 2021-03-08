#!/bin/sh
echo "Configuring Niffler"

PIP=`head -n 1 config/pip.out`
if [ "$PIP" = false ] ; then
    echo "Installing pip"
    sudo yum install python3-pip
    echo "true" > config/pip.out
fi

alias python=python3
alias pip=pip3

MONGO=`head -n 1 config/mongo.out`
if [ "$MONGO" = false ] ; then
    echo "Installing mongo"
    sudo cp config/mongodb-org-4.2.repo /etc/yum.repos.d/
    sudo yum install mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
    echo "true" > config/mongo.out
fi
