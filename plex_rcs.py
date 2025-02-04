#!/usr/bin/python3
#
# Helper script
#
import os
import sys
import re
import argparse
import yaml
import time
from datetime import datetime
from multiprocessing import Pool
from subprocess import run
from plexapi.myplex import PlexServer
from sh import tail


def config(file):
    global servers, cfg

    with open(file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile,Loader=yaml.FullLoader)['plex_rcs']

    servers = []
    for server in cfg['servers']:
        try:
            plex = PlexServer(
                "http://{0}:{1}".format(server['host'], server['port']), server['token'])
            servers.append(plex)
        except:
            sys.exit("Failed to connect to plex server {0}:{1}.".format(
                server['host'], server['port']))
            
def build_sections():
    global paths

    # Build our library paths dictionary
    for section in servers[0].library.sections():
        for l in servers[0].library.section(section.title).locations:
            paths.update({l: section.key})

def scan(folder):
    directory = os.path.abspath("{0}/{1}".format(cfg['media_root'].rstrip("\\").rstrip("/"), folder))

    # Match the new file with a path in our library
    # and trigger a scan via a 'Plex Media Scanner' call
    found = False

    for p in paths:
        if p in directory:
            found = True
            section_id = paths[p]
            print("Processing section {0}, folder: {1}".format(section_id, directory))

            for server in servers:
                try:
                    # Use run for non-blocking
                    run(["/usr/lib/plexmediaserver/Plex Media Scanner", "--scan", "--refresh", "--section", section_id, "--directory", directory])
                except:
                    print("Error executing command")

    if not found:
        print("Scanned directory '{0}' not found in Plex library".format(directory))


def tailf(logfile):
        print("Starting to monitor {0} with pattern for rclone {1}".format(logfile, cfg['backend']))

        # Validate which backend we're using
        if cfg['backend'] == 'cache':
                # Use cache backend
                for line in tail("-Fn0", logfile, _iter=True):
                        if re.match(r".*(mkv:|mp4:|mpeg4:|avi:) received cache expiry notification", line):
                                f = re.sub(r"^(.*rclone\[[0-9]+\]: )([^:]*)(:.*)$",r'\2', line)
                                print("Detected new file: {0}".format(f))
                                scan(os.path.dirname(f))

        elif cfg['backend'] == 'vfs':
                # Use vfs backend
                timePrev = ''
                for line in tail("-Fn0", logfile, _iter=True):
                        if re.match(r".*: invalidating directory cache", line):
                                files = re.search(r": (.*)\:", line)
                                f = files.group(1)
                                timeCurr = re.sub(r"^.*\s([0-9]+:[0-9]+:[0-9]+)\s.*\s:\s.*:\sinvalidating directory cache",r'\1', line)

                                if timeCurr != timePrev:
                                        print("Detected directory cache expiration: {0}".format(f))
                                        scan(os.path.dirname(f))
                                        timePrev = timeCurr

def find_log():
    if args.logfile:
        lf = args.logfile
        if not os.path.isfile(lf):
            print("Log file '{0}' does not exist.".format(args.logfile))
            sys.exit(1)
    else:
        lf = cfg['log_file']
        if not os.path.isfile(lf):
            print("Log file {0} does not exist.".format(lf))
            sys.exit(1)

    return lf

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="plex_rcs_helper.py", description="Small helper script to update a Plex library section by scanning a specific directory.")
    parser.add_argument("-d", "--directory", dest="directory",
                        metavar="directory", help="Directory to scan")
    parser.add_argument("-l", "--logfile", dest="logfile", metavar="logfile",
                        help="Log file to monitor (default /var/log/syslog)")
    parser.add_argument("-c", "--config", dest="config",
                        metavar="config", help="config file")
    parser.add_argument("--test", action='store_true', help="Test config")
    args = parser.parse_args()

    # Initialize our paths dict
    paths = {}

    # Configuration file
    if args.config:
        cf = args.config
        if not os.path.isfile(cf):
            print("Configuration file '{0}' does not exist.".format(
                args.config))
            sys.exit(1)
    else:
        cf = "{0}/config.yml".format(
            os.path.dirname(os.path.realpath(__file__)))
        if not os.path.isfile(cf):
            print("Configuration file '{0}' does not exist.".format(
                os.path.dirname(os.path.realpath(__file__))))
            sys.exit(1)
    # Main
    if args.test:
        config(cf)
        find_log()
    elif args.directory:
        config(cf)
        find_log()
        build_sections()
        scan(args.directory)
    else:
        config(cf)
        lf = find_log()
        print("Found rclone logfile: {0}".format(lf))
        build_sections()
        print("Import of libraries from Plex complete. Starting up...")
        tailf(lf)
