FROM python:3.10.10-bullseye

# download and add DCM4CHE
ADD https://sourceforge.net/projects/dcm4che/files/dcm4che3/5.22.5/dcm4che-5.22.5-bin.zip/download /opt/dcm4che-5.22.5-bin.zip
RUN set -eux; \
# install JRE for DCM4CHE, mailutils
    apt update && \
    apt install -y openjdk-11-jre mailutils && \
# extract and install DCM4CHE
    cd /opt; \
    unzip dcm4che-5.22.5-bin.zip && \
    rm dcm4che-5.22.5-bin.zip; \
# create default dicom storage directory
    mkdir -p /opt/data/new-study

COPY . /usr/src/niffler-cold-extraction
WORKDIR /usr/src/niffler-cold-extraction

# install required python packages
RUN pip install -r requirements.txt

CMD ["python", "ColdDataRetriever.py"]
