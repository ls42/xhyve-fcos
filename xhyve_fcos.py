import requests
import logging
from os.path import join
#from subprocess import run, PIPE

DOWNLOAD_DIR = "./static/" # Make configurable via cli args
RELEASE_JSON_URL = "https://builds.coreos.fedoraproject.org/streams/stable.json"


class FCOSXhyve:
    def __init__(self, outdir: str, json_url: str):
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

        self.outdir = outdir
        self.json_url = json_url

        self.get_links()

    def get_links(self):
        """Parse the JSON release file into a list of files to download"""
        parsed_json = requests.get(self.json_url).json()
        download_formats = parsed_json['architectures']['x86_64']['artifacts']['metal']['formats']
        self.list = [
            download_formats['pxe']['kernel']['location'],
            download_formats['pxe']['initramfs']['location'],
            download_formats['raw.xz']['disk']['location']
        ]
        logging.info("download list created")

    def download(self):
        """downloads all neccessary files for booting fcos on xhyve"""
        for url in self.list:
            file_name = url.split('/')[-1:][0]
            output_file_name = join(self.outdir, file_name)
            logging.info(f"downloading file {file_name}")

            r = requests.get(url, stream=True)
            with open(output_file_name, "wb") as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)


if __name__ == "__main__":
    fcos = FCOSXhyve(DOWNLOAD_DIR, RELEASE_JSON_URL)
    fcos.download()

