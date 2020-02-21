# xhyve wrapper for Fedora CoreOS

## notes

- Every boot generates new SSH host keys.
- On my laptop it works with xhyve and hyperkit (which comes with docker desktop). YMMV.
- Load fcct, the fcc to ign transpiler, from [https://github.com/coreos/fcct](the official repo)
- `./fcct --pretty --strict < default.fcc > default.ign`
- Copy default.ign to a web server, and insert the url into settings.json
- Recycling the UUID should result in the same IP. Should.

## todo

- accept command line arguments which override settings from settings.json
- find a way to make a configuration persistent (save uuid in a useful way).
- run fcct automatically
- enable persistence (disk images)
- maybe use sqlite which could track UUIDs, corresponding disk images and vm-names (vm-names as cli arguments to select entries from the db)
- start a webserver that delivers the default.ign file
