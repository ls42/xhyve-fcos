import requests
import logging
import re
from os.path import join

import subprocess as sp

DOWNLOAD_DIR = "./static/"  # TODO: Make configurable via cli args
RELEASE_JSON_URL = "https://builds.coreos.fedoraproject.org/streams/stable.json"


class FCOSXhyve:
    def __init__(self, outdir: str, json_url: str):
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

        self.outdir = outdir
        self.json_url = json_url

        # Properties
        self.download_location = ""
        self.list = []
        self.initrd_file = ""
        self.kernel_file = ""
        self.disk_file = ""

        # Setup
        self._get_links()
        self._parse_files()

    def _get_links(self):
        """
        Parse the JSON release file into a list of files to download

        We assume, that all three files are located in the same directory.
        If that's not the case, downloading will fail.
        """
        parsed_json = requests.get(self.json_url).json()
        download_formats = parsed_json["architectures"]["x86_64"]["artifacts"]["metal"]["formats"]
        self.download_location = download_formats["pxe"]["kernel"]["location"].rsplit(
            "/", maxsplit=1
        )[0]
        self.list = [
            download_formats["pxe"]["kernel"]["location"].rsplit("/", maxsplit=1)[1],
            download_formats["pxe"]["initramfs"]["location"].rsplit("/", maxsplit=1)[1],
            # download_formats["raw.xz"]["disk"]["location"].rsplit("/", maxsplit=1)[1], # might only need the other two
        ]
        logging.info("download list created")

    def download(self):
        """Download all neccessary files for booting fcos on xhyve"""
        for file_name in self.list:
            output_file_name = join(self.outdir, file_name)
            logging.info(f"downloading file {file_name}")
            r = requests.get(f"{self.download_location}/{file_name}", stream=True)
            with open(output_file_name, "wb") as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)

    def _parse_files(self):
        """Find out which file is the kernel, which the initrd and which the boot image"""
        initrd_pattern = re.compile("fedora-coreos.*initramfs.*", re.IGNORECASE)
        kernel_pattern = re.compile("fedora-coreos.*live-kernel.*", re.IGNORECASE)
        disk_pattern = re.compile("fedora-coreos.*metal.*", re.IGNORECASE)
        for item in self.list:
            if initrd_pattern.match(item):
                self.initrd_file = item
            if kernel_pattern.match(item):
                self.kernel_file = item
            if disk_pattern.match(item):
                self.disk_file = item
        logging.info("files parsed")

    def create(self):
        """Create VM using xhyve"""

        # 1. Create list of command line arguments
        # 2. Give list to sp.run() and start xhyve

        logging.info("running xhyve")


def main():
    fcos = FCOSXhyve(DOWNLOAD_DIR, RELEASE_JSON_URL)
    fcos.create()


if __name__ == "__main__":
    main()
