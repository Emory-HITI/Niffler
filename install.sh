#!/bin/sh
echo "Configuring Niffler"
echo "Installing pip"
sudo yum install python3-pip
alias python=python3
alias pip=pip3
echo "Installing mongo"
MONGO=`head -n 1 config/mongo.out`
if [ "$MONGO" = true ] ; then
    sudo cp config/mongodb-org-4.2.repo /etc/yum.repos.d/
    sudo yum install mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
    echo "true" > config/mongo.out
fi
