#!/bin/sh
echo "Configuring Niffler"
sudo chmod -R 777 .
touch /opt/localdrive/Niffler/modules/meta-extraction/service/service.log
touch /opt/localdrive/Niffler/modules/meta-extraction/service/service-error.log
sudo yum install -y python3
PIP=`head -n 1 init/pip.out`
if [ "$PIP" = false ] ; then
    echo "Installing pip"
    sudo yum install python3-pip
    pip install -r requirements.txt
    wget https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh
    sh Anaconda3-2020.11-Linux-x86_64.sh -u
    source ~/.bashrc
    rm Anaconda3-2020.11-Linux-x86_64.sh
    echo "true" > init/pip.out
fi

MISC=`head -n 1 init/misc.out`
if [ "$MISC" = false ] ; then
    echo "Installing gdcm and mail"
    conda install -c conda-forge -y gdcm
    sudo yum install mailx -y
    sudo yum install sendmail sendmail-cf
    chmod +x modules/meta-extraction/service/mdextractor.sh
    echo "Disable THP"
    sudo cp init/disable-thp.service /etc/systemd/system/disable-thp.service
    sudo systemctl daemon-reload
    sudo systemctl start disable-thp
    sudo systemctl enable disable-thp
    echo "true" > init/misc.out
fi

sudo cp modules/meta-extraction/service/mdextractor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start mdextractor.service
sudo systemctl enable mdextractor.service

DCM4CHE=`head -n 1 init/dcm4che.out`
if [ "$DCM4CHE" = false ] ; then
    echo "Installing JDK"
    sudo yum install java-1.8.0-openjdk-devel
    echo "Installing Maven"
    sudo dnf install maven
    echo "Installing DCM4CHE"
    cd ..
    wget https://sourceforge.net/projects/dcm4che/files/dcm4che3/5.22.5/dcm4che-5.22.5-bin.zip/download -O dcm4che-5.22.5-bin.zip
    unzip dcm4che-5.22.5-bin.zip
    rm dcm4che-5.22.5-bin.zip
    cd Niffler
    echo "true" > init/dcm4che.out
fi

MONGO=`head -n 1 init/mongo.out`
if [ "$MONGO" = false ] ; then
    echo "Installing mongo"
    sudo cp init/mongodb-org-4.2.repo /etc/yum.repos.d/
    sudo yum install mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
    mongo init/mongoinit.js
    echo "true" > init/mongo.out
fi

