#!/bin/sh

echo "Configuring Niffler"
sudo chmod -R 777 .

curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin

PIP=`head -n 1 init/pip.out`
if [ "$PIP" = false ] ; then
    brew install python3
    echo "Installing pip"
    python3 -m ensurepip
    pip3 install -r requirements.txt
    pip3 install -i https://test.pypi.org/simple/ HITI-anon-internal
    wget https://repo.anaconda.com/archive/Anaconda3-2022.10-MacOSX-arm64.sh
    sh Anaconda3-2022.10-MacOSX-arm64.sh -u
    source ~/.zshrc
    rm Anaconda3-2022.10-MacOSX-arm64.sh
    echo "true" > init/pip.out
fi

MISC=`head -n 1 init/misc.out`
if [ "$MISC" = false ] ; then
    echo "Installing gdcm and mail"
    brew install gdcm
    # mailx not availlable for MacOs
    brew install mailutils
    # sendmail-cf not available for MacOS
    chmod +x modules/meta-extraction/service/mdextractor.sh
    # echo "Disable THP"
    # sudo cp init/disable-thp.service /etc/systemd/system/disable-thp.service
    # sudo systemctl daemon-reload
    # sudo systemctl start disable-thp
    # sudo systemctl enable disable-thp
    echo "true" > init/misc.out
fi


DCM4CHE=`head -n 1 init/dcm4che.out`
if [ "$DCM4CHE" = false ] ; then
    echo "Installing JDK"
    brew tap adoptopenjdk/openjdk
    brew install --cask adoptopenjdk8
    echo "Installing Maven"
    brew install maven
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
    brew tap mongodb/brew
    brew install mongodb-community
    brew services start mongodb-community
    brew services enable mongodb-community
    mongosh init/mongoinit.js
    sudo cp modules/meta-extraction/service/mdextractor.plist /Library/LaunchDaemons/
    sudo launchctl load /Library/LaunchDaemons/mdextractor.plist
    sudo launchctl enable system/mdextractor.plist
    echo "true" > init/mongo.out
fi

SERVICE=`head -n 1 init/service.out`
if [ "$SERVICE" = false ] ; then
    echo "Installing Niffler Frontend"
    pip install -r modules/frontend/requirements.txt
    pip install -i https://test.pypi.org/simple/ HITI-anon-internal
    chmod +x modules/frontend/service/frontend_service.sh
    sudo cp modules/frontend/service/niffler.plist /Library/LaunchDaemons/
    sudo launchctl load -w /Library/LaunchDaemons/niffler.plist
    sudo launchctl enable system/niffler.plist
    echo "true" > init/service.out
fi

