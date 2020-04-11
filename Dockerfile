FROM centos:centos7

RUN yum update -y && \
    yum install python3 -y && \
    yum install ca-certificates-2019.2.32-76.el7_7 -y && \
    yum install python3-pip -y && \
    yum clean all

COPY src/server.py .
COPY requirements.txt .

RUN pip3 install virtualenv
RUN /bin/bash -c "virtualenv -p python3 .venv"
RUN source .venv/bin/activate
RUN pip3 install -r requirements.txt

RUN mkdir log

ENTRYPOINT [ "python3", "server.py" ]