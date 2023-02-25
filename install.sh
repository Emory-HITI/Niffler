#!/bin/sh
echo "Configuring Niffler"
sudo chmod -R 777 .

name=""

if [[ -e /etc/os-release ]]; then
    . /etc/os-release
    name=$NAME
else
    name="None"
fi

echo "Found distribution: $name"

wget -qO- https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin

PIP=`head -n 1 init/pip.out`
if [ "$PIP" = false ] ; then
    echo "Installing pip and python3..."
    if [ "$name" = "Fedora" ] ; then
        sudo yum install -y python3
        sudo yum install -y python3-pip
    elif [ "$name" = "Arch Linux" ] ; then
        sudo pacman -S --noconfirm python
        sudo pacman -S --noconfirm python-pip
    elif [ "$name" = "Ubuntu" ] ; then
        sudo apt-get install -y python3
        sudo apt-get install -y python3-pip
    fi

    pip install -r requirements.txt
    pip install -i https://test.pypi.org/simple/ HITI-anon-internal
    if command -v conda >/dev/null 2>&1 ; then
        echo "Conda is already installed, skipping..."
    else
        wget https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh
        sh Anaconda3-2020.11-Linux-x86_64.sh -u
        source ~/.bashrc
        rm Anaconda3-2020.11-Linux-x86_64.sh
    fi
    echo "true" > init/pip.out
fi

MISC=`head -n 1 init/misc.out`
if [ "$MISC" = false ] ; then
    echo "Installing gdcm and mail"
    conda install -c conda-forge -y gdcm

    if [ "$name" = "Fedora" ] ; then
        sudo yum install mailx -y
        sudo yum install sendmail sendmail-cf
    elif [ "$name" = "Arch Linux" ] ; then
        sudo pacman -S --noconfirm mailx
        sudo pacman -S --noconfirm sendmail sendmail-cf

    elif [ "$name" = "Ubuntu" ] ; then
        sudo apt-get install -y mailutils
        sudo apt-get install -y sendmail sendmail-cf
    fi

    chmod +x modules/meta-extraction/service/mdextractor.sh
    echo "Disable THP"
    sudo cp init/disable-thp.service /etc/systemd/system/disable-thp.service
    sudo systemctl daemon-reload
    sudo systemctl start disable-thp
    sudo systemctl enable disable-thp
    echo "true" > init/misc.out
fi

DCM4CHE=`head -n 1 init/dcm4che.out`
if [ "$DCM4CHE" = false ] ; then
    echo "Installing jdk and Maven..."
    if [ "$name" = "Fedora" ] ; then
        sudo yum install java-1.8.0-openjdk-devel
        sudo dnf install maven
    elif [ "$name" = "Arch Linux" ] ; then
        sudo pacman -S --noconfirm jdk8-openjdk
        sudo pacman -S --noconfirm maven

    elif [ "$name" = "Ubuntu" ] ; then
        sudo apt install -y openjdk-8-jdk
        sudo apt install -y maven
    fi

    cd ..
    wget https://sourceforge.net/projects/dcm4che/files/dcm4che3/5.22.5/dcm4che-5.22.5-bin.zip/download -O dcm4che-5.22.5-bin.zip
    unzip dcm4che-5.22.5-bin.zip
    rm dcm4che-5.22.5-bin.zip
    cd Niffler
    echo "true" > init/dcm4che.out
fi

MONGO=`head -n 1 init/mongo.out`
if [ "$MONGO" = false ] ; then
    echo "Installing MongoDb..."
    sudo cp init/mongodb-org-4.2.repo /etc/yum.repos.d/

    if [ "$name" = "Fedora" ] ; then
        sudo yum install mongodb-org
    elif [ "$name" = "Arch Linux" ] ; then
        sudo pacman -S --noconfirm mongodb

    elif [ "$name" = "Ubuntu" ] ; then
        sudo apt install -y mongodb
    fi

    sudo systemctl start mongod
    sudo systemctl enable mongod
    mongo init/mongoinit.js
    sudo cp modules/meta-extraction/service/mdextractor.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl start mdextractor.service
    sudo systemctl enable mdextractor.service
    echo "true" > init/mongo.out
fi

SERVICE=`head -n 1 init/service.out`

if [ "$SERVICE" = false ] ; then
    echo "Installing Niffler Frontend"
    pip install -r modules/frontend/requirements.txt
    pip install -i https://test.pypi.org/simple/ HITI-anon-internal
    chmod +x modules/frontend/service/frontend_service.sh
    sudo cp modules/frontend/service/niffler.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl start niffler.service
    sudo systemctl enable niffler.service
    echo "true" > init/service.out
fi
