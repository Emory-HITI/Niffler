#!/bin/sh
echo "Configuring Niffler"

PIP=`head -n 1 init/pip.out`
if [ "$PIP" = false ] ; then
    echo "Installing pip"
    sudo yum install python3-pip
    echo "true" > init/pip.out
fi

MONGO=`head -n 1 init/mongo.out`
if [ "$MONGO" = false ] ; then
    echo "Installing mongo"
    sudo cp init/mongodb-org-4.2.repo /etc/yum.repos.d/
    sudo yum install mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
    echo "true" > init/mongo.out
fi

sudo pip3 install -r requirements.txt
