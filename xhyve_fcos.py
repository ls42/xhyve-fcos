import json
import requests
from subprocess import run, PIPE
from urllib.request import urlretrieve

DOWNLOAD_DIR = "./static/"
RELEASE_JSON_URL = "https://builds.coreos.fedoraproject.org/streams/stable.json"

requests.get(

# Parse json to check which files to download
# We need
# - a initrd.gz and
# - a vmlinuz file


# run(args=["xhyve", "-h"], check=True)
