FROM sabbir1cse/ubuntu-python-pip-supervisor:latest

COPY ./v2_src /home/src
WORKDIR /home/src
RUN pip install urllib3[secure] requests flask bs4 lxml werkzeug checksumdir pycrypto 

EXPOSE 23344
CMD ["python","OT_server.py"]
