import requests
import hashlib
import uuid
import collections
import os
import time
import subprocess
from typing import List, Dict, NamedTuple, Generator
from logzero import logger
from .config import Config

config = Config()


def download(url: str) -> NamedTuple:
    """
    Download a file from a URL
    :param url: URL
    :return: Named tuple containing (location=file_location, hash=file_hash)
    """
    File = collections.namedtuple('File', 'location hash')
    try:
        request = requests.get(url, timeout=3)
    except Exception as e:
        logger.error(e)
    else:
        content = request.content
        sha256 = hashlib.sha256(content).hexdigest()
        output_file = os.path.join(config.download_location, str(uuid.uuid4()) + ".txt")
        with open(output_file, "wb") as f:
            f.write(content)
        return File(location=output_file, hash=sha256)
    return ()


def multi_download(urls: List) -> List[Dict]:
    """
    Download files from a list of URLs
    :param urls: List of URLs
    :return: List of dicts containing two keys, File and Type.
    'File' is a named tuple while 'Type' is a string from config.json
    """
    downloads = []
    for url in urls:
        data = {"File": download(url['URL']), "Type": url['TYPE']}
        downloads.append(data)
    return downloads


def get_timestamp() -> str:
    """
    Get current timestamp
    :return: timestamp
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def dnsmasq(domain: str) -> str:
    """
    Return a domain in dnsmasq format
    :param domain: domain
    :return: dnsmasq address block
    """
    domain = domain.replace("\n", "")
    return f'address=/{domain}/{config.BLACKHOLE}\n'


def bind(domain: str) -> str:
    pass


def append_to_blacklist(domains: List):
    """
    Appends a list of domains to the blacklist file
    :param domains: List of DomainIntel objects
    """
    with open(config.BLACKLIST_FILE, "a") as f:
        f.write("".join([x.domain_formated for x in domains]))


def restart_dnsmasq():
    """
    Restart the dnsmasq service, requires root
    :return:
    """
    try:
        status = subprocess.run(["sudo", "systemctl", "restart", "dnsmasq"], check=True)
    except Exception as e:
        logger.error(f"Could not restart dnsmasq: {e}")
        quit()
    return status


def reload_blacklist_file(generator: Generator):
    """
    Saves the content of the generator to the blacklist file. generator is a DomainIntel Object.
    :param generator: DomainIntel generator object
    """
    if os.path.exists(config.BLACKLIST_FILE):
        os.remove(config.BLACKLIST_FILE)
    for gen in generator:
        append_to_blacklist(gen)


def restart_bind():
    """
    Restart the bind service, requires root
    :return:
    """
    try:
        status = subprocess.run(["sudo", "systemctl", "restart", "named"], check=True)
    except Exception as e:
        logger.error(f"Could not restart bind: {e}")
        quit()
    return status

