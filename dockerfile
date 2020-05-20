FROM python:3-alpine

RUN mkdir /plex_rcs /nas && cd /plex_rcs && wget https://raw.githubusercontent.com/mattmac24/plex_rcs/master/plex_rcs.py && wget https://raw.githubusercontent.com/mattmac24/plex_rcs/master/requirements.txt

RUN pip install -r /plex_rcs/requirements.txt

CMD [ "python", "/plex_rcs/plex_rcs.py" ]
