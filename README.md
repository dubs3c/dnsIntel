# dnsIntel
**dnsIntel** is a tool for creating custom modules that downloads domains classified as malware or advertising from popular threat intelligence sources, and building a block list which can be used by DNS servers such as DNSMASQ or BIND.

## How to run
1. Clone the repo
2. `pip install -r requirements.txt`
3. `python dnsintel.py`

## Todo
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