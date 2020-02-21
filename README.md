# xhyve wrapper for Fedora CoreOS

## notes

- load fcct, the fcc to ign transpiler, from [https://github.com/coreos/fcct](the official repo)
- `./fcct --pretty --strict < default.fcc > default.ign`
- copy default.ign to a web server, and insert the url into settings.json
