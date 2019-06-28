FROM ubuntu
RUN apt update
RUN yes | apt install python3-pip
RUN pip3 install flask flask_cors pyyaml pyopenssl
COPY . /app/
CMD ["python3", "/app/app.py"]
