# Version 0.1.0
FROM continuumio/anaconda
MAINTAINER kanikagera "kanikagera.96@gmail.com"
RUN pip install flask==0.12.1
RUN pip install pymysql==0.7.11
COPY table_service.py /
COPY script2.sh /
ENTRYPOINT ["bash", "/script2.sh"]
