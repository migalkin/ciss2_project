FROM ubuntu

RUN apt update -y && \
    apt install -y git python python-setuptools openjdk-8-jdk
# create application folder
RUN mkdir /app
# copy source code to application folder
RUN git clone https://github.com/liyakun/nlgserv.git /app && \
    cd /app/ && \
    git checkout ffb4bbf4e340422b6a86f5b712ca2d5903bb6053 && \
    python setup.py install
# export port
EXPOSE 8300
ENTRYPOINT ["java", "-jar", "/app/nlgserv/jython.jar", "/app/nlgserv/_server.py", "0.0.0.0", "8300"]
