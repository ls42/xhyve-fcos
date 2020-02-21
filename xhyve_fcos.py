import requests
import logging
import re
import json
import uuid
import subprocess as sp
from os.path import join

DOWNLOAD_DIR = "./static/"  # TODO: Make configurable via cli args


class FCOSXhyve:
    def __init__(self, outdir: str):
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

        self.outdir = outdir

        # Properties
        self.download_location = ""
        self.list = []
        self.initrd_file = ""
        self.kernel_file = ""
        self.disk_file = ""
        self.config = {}

        # Setup
        self._load_config()
        self._get_links()
        self._parse_files()

    def _load_config(self):
        def defaults(data):
            item = "hypervisor"
            if item not in data:
                data[item] = "hyperkit"
            item = "uuid"
            if item not in data:
                data[item] = uuid.uuid4()
            item = "cores"
            if item not in data:
                data[item] = 1
            item = "memory"
            if item not in data:
                data[item] = 1
            item = "net"
            if item not in data:
                data[item] = "-s 2:0,virtio-net"
            item = "stream"
            if item not in data:
                data[item] = "stable"
            item = "ignition_url"
            if item not in data:
                data[item] = "http://192.168.64.1:8000/default.ign"
                # `python -m http.server --bind 192.168.64.1`
            return data

        with open("./settings.json", "r") as f:
            self.config = json.load(f, object_hook=defaults)

    def _get_links(self):
        """
        Parse the JSON release file into a list of files to download

        We assume, that all two files are located in the same directory.
        If that's not the case, downloading will fail.
        """
        json_url = f"https://builds.coreos.fedoraproject.org/streams/{self.config['stream']}.json"
        parsed_json = requests.get(json_url).json()
        download_pxe = parsed_json["architectures"]["x86_64"]["artifacts"]["metal"]["formats"][
            "pxe"
        ]
        self.download_location = download_pxe["kernel"]["location"].rsplit("/", maxsplit=1)[0]
        self.list = [
            download_pxe["kernel"]["location"].rsplit("/", maxsplit=1)[1],
            download_pxe["initramfs"]["location"].rsplit("/", maxsplit=1)[1],
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

        # 1. Give list to sp.run() and start {hypervisor}
        stream = self.config['stream']
        ignition_url = self.config['ignition_url']
        hypervisor = self.config['hypervisor']
        xhyve_args = [
            "sudo",
            f"{hypervisor}",
            "-U",
            str(self.config['uuid']),
            "-m",
            f"{self.config['memory']}G",
            "-c",
            f"{self.config['cores']}",
            "-A",
            "-s",
            "2:0,virtio-net",
            "-s",
            "0:0,hostbridge",
            "-s",
            "31,lpc",
            "-l",
            "com1,stdio",
            "-f",
            f'kexec,{self.outdir}{self.kernel_file},{self.outdir}{self.initrd_file},"earlyprintk=serial '
            f'ip=dhcp rd.neednet=1 console=tty0 console=ttyS0 ignition.platform.id=metal ignition.firstboot '
            f'ignition.config.url={ignition_url} '
            f'coreos.inst.stream={stream}"',
        ]
        # sp.run(xhyve_args, shell=True, check=True)
        logging.info("running xhyve")
        logging.info(" ".join(xhyve_args))


def main():
    fcos = FCOSXhyve(DOWNLOAD_DIR)
    fcos.create()


if __name__ == "__main__":
    main()
