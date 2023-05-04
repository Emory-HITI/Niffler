FROM python:3.10.10-bullseye

# install JRE for DCM4CHE
RUN set -eux; \
    apt update && \
    apt install -y openjdk-11-jre

# install DCM4CHE
RUN set -eux; \
    cd /opt; \
    curl -L https://sourceforge.net/projects/dcm4che/files/dcm4che3/5.22.5/dcm4che-5.22.5-bin.zip/download \
         -o dcm4che-5.22.5-bin.zip; \
    unzip dcm4che-5.22.5-bin.zip && \
    rm dcm4che-5.22.5-bin.zip

COPY . /usr/src/app
WORKDIR /usr/src/app

# install required python packages
RUN pip install -r requirements.txt

# create default dicom storage directory
RUN mkdir /opt/niffler-dicom-root

CMD ["python", "MetadataExtractor.py"]
