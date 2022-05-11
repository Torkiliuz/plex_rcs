# Plex rclone cache scanner (plex_rcs)

A small python script that will monitor an rclone log file, waiting for notices of file cache expiration. Upon receiving a notice, a local Plex scan of that folder will be triggered and new media will appear in Plex almost instantly.

This is useful for people who run Plex Media Server on a different server than Sonarr/Radarr/etc.

## Requirements

1. Python 3+
2. Your rclone cache mount must include `--log-level INFO` **OR** if using VFS, it must be `--log-level DEBUG`
3. Your rclone cache mount must include `--syslog` **OR** * if using VFS, it must be `--log-file /path/to/file.log`

## Installation

1. Clone this repo: `git clone https://github.com/Torkiliuz/plex_rcs.git`
2. Install the requirements: `pip3 install -r requirements.txt`

## Configuration



1. Copy the `config.yml.default` to `config.yml`
2. Edit `config.yml` to include your [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/), set your `media_root` setting and any other settings.

## Running plex_rcs

Using `screen` or using the included `plex_rcs.service` systemd service

### Using Linux

Example rclone mount for linux:

`mount gdrive:/ /mnt/media --user-agent="myuseragent/v1" --drive-skip-gdocs --timeout=30m --allow-other --dir-cache-time=72h --log-level=DEBUG --log-file=/path/to/log`


#### Using systemd

1. Edit the included `plex_rcs.service` file and change the path to where the `plex_rcs.py` file is located
2. Copy the systemd file to `/etc/systemd/service`: `sudo cp plex_rcs.service /etc/systemd/service`
3. Reload systemd: `sudo systemctl daemon-reload`
4. Enable the service [auto-starts on boot]: `sudo systemctl enable plex_rcs`
5. Start the service: `sudo systemctl start plex_rcs`

#### Using `screen`

Execute the program using screen:

`/usr/bin/screen -dmS plexrcs /path/to/plex_rcs/plex_rcs.py`

To view the console: `screen -r plexrcs`
