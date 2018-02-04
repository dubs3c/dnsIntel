# dnsIntel
**dnsIntel** is a tool for creating custom modules that downloads domains classified as malware or advertising from popular threat intelligence sources, and building a blocklist which can be used by DNS servers such as DNSMASQ or BIND.

## Motivation
The motivation behind dnsIntel was to protect my own network from malvertising and new threats by blocking on the DNS level. I run DNSMASQ in my homelab and needed a way to automatically block new threats, and so dnsIntel was born.

## How does it work?
dnsIntel tries to be framework which gives you all the necessary tools write a small script that downloads new domains from any source, and updates your DNS server with new domains to block. The `config.json` contains all configuration and sources from which to download from. Everything is stored in a local sqlite database file. dnsIntel will build a blacklist file containing your blocked doamins according to either DNSMASQ or BIND(planned feature) format.

Scripts/modules can be found in the module folder.

### Example output

Here are some examples of using dnsIntel.
#### Usage example:
```
Usage: dnsintel.py [OPTIONS] COMMAND [ARGS]...

  dnsIntel downloads and parses a list of domains from popular threat intel
  sources,     then transforms the list into a blacklist which can be used
  by dnsmasq and BIND.

  -== Made by @mjdubell ==-

Options:
  -l, --loglevel [DEBUG]  Set loglevel
  -m, --module TEXT       Run specific module
  -f, --force             Force download previously downloaded files
  --version               Show the version and exit.
  --help                  Show this message and exit.

Commands:
  run  Run the application
```

#### Running example
```
(venv) λ ~/Desktop/domain_intel/ python dnsintel.py run
[*] Starting dnsIntel...
[!] Running Module: DisconnectMe...
[!] Running Module: MalwareDomains...
[+] dnsIntel Completed
```

#### Blacklist file output example
```
address=/101com.com/192.168.10.4
address=/101order.com/192.168.10.4
address=/123found.com/192.168.10.4
address=/140proof.com/192.168.10.4
address=/180hits.de/192.168.10.4
address=/180searchassistant.com/192.168.10.4
```

## How to run
1. Clone the repo
2. `pip install -r requirements.txt`
3. `python dnsintel.py`

## Future improvements
* Control the local sqlite database from terminal.
* Create a web interface to view the collected data and perform CRUD operations.
* Add tests.

## Contributing
Any feedback or ideas are welcome! Want to improve something? Create a pull request!

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D