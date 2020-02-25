from setuptools import setup

setup(
    name='xhyve_fcos',
    url='https://github.com/ls42/xhyve-fcos',
    version='0.0.1',
    description='xhyve wrapper for Fedora CoreOS',
    author='Stephan Brauer',
    author_email='stephan@ps1.sh',
    install_requires=['requests'],
    packages=["xhyve_fcos"],
    entry_points={
        'console_scripts': ['xhyve-fcos=xhyve_fcos.xhyve_fcos:main'],
    },
)
