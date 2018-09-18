#FROM python:2.7-alpine is not work.
#FROM python:2.7
FROM centos:7


RUN yum install -y epel-release
RUN yum install -y python
RUN yum install -y python2-pip
RUN yum install -y mysql

RUN mkdir -p  /root/.pip
ADD source/pip.conf     /root/.pip
#ADD source/sources.list /etc/apt
#RUN apt-get update

RUN mkdir -p  /code/conf
ADD requirements.txt       /code
WORKDIR /code
RUN pip install -r requirements.txt

ADD wisecloud_upgrader.py  /code
#ADD conf/config.ini /code/conf

CMD ["python", "wisecloud_upgrader.py"]