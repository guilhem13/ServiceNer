FROM debian:11

ADD . /ServiceNER
WORKDIR /ServiceNER
EXPOSE 6000

COPY requirements.txt .
RUN apt-get update -q -y
RUN apt-get install -y python3-pip libkrb5-dev \
    build-essential libpoppler-cpp-dev pkg-config python3-dev \
    python3 \
    python3-gssapi 

RUN python3 --version
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /ServiceNER
USER appuser

CMD [ "python3", "app.py" ]
