FROM ubuntu

RUN apt-get update && apt-get upgrade -y
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install --no-install-recommends --no-install-suggests -y tzdata python3 python-is-python3 python3-pip mailutils sendmail libgdcm3.0 libgdcm-tools python3-gdcm python3-pillow python3-pandas python3-numpy
RUN pip install pydicom pypng pylibjpeg

ARG DICOMHome

COPY . /png-extraction
COPY $DICOMHome /png-extraction/dicom_home
WORKDIR /png-extraction

RUN chmod -R a+rw /png-extraction
RUN chown -R $USER:users /png-extraction
RUN chmod +x ./png-extraction-docker

CMD ["./png-extraction-docker", "--docker"]
