FROM python:3.6

WORKDIR /app

COPY requirements.txt  requirements.txt 

RUN pip install -r requirements.txt 
RUN apt-get -yqq update && apt-get -yqq install docker.io
touch /app/plex_rcs.log
RUN ln -sf /dev/stdout /app/plex_rcs.log

copy plex_rcs.py plex_rcs.py

CMD ["python", "/app/plex_rcs.py", "--config=/app/config/config.yml", "--logfile=/app/config/rclone.log"]
