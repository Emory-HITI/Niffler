FROM ravirahar/arch-python-gdcm
ARG DICOMHome="/opt/data/new-study"

COPY . /png-extraction
COPY $DICOMHome /png-extraction/dicom_home
WORKDIR /png-extraction

RUN chmod -R a+rw /png-extraction
RUN chown -R $USER:users /png-extraction
RUN chmod +x ./png-extraction-docker

CMD ["./png-extraction-docker", "--docker"]
