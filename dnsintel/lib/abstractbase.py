#!/usr/local/bin/env python3.7

import abc
import os
import click

from typing import List, Dict, Tuple, Generator, NamedTuple

from peewee import chunked
from logzero import logger
from dnsintel.lib.config import Config
from dnsintel.lib.sqlpeewee import db, Log, MalwareDomains
from dnsintel.lib.util import download, multi_download


class AbstractBase(object):
    """Abstract class containing common methods and skeleton for modules"""

    def __init__(self):
        self.config = Config()
        self.BLACKLIST_FILE = ""
        self.BLACKHOLE = ""
        self.CHUNK_SIZE = 1000
        self.load_config()
        self.db = db

    __metaclass__ = abc.ABCMeta

    def load_config(self):
        """
        Load some configuration options
        :return:
        """
        self.BLACKHOLE = self.config.BLACKHOLE
        self.BLACKLIST_FILE = self.config.BLACKLIST_FILE

    def load(self, config: Dict) -> Tuple:
        """
        Load URL configuration from config.json

        :param config: Dictionary that holds URL(s)
        :return Files: Named tupe - (location=file_path, hash=file_hash)
        """
        if "URL" in config:
            file = download(config["URL"])
            return file
        return ()

    def multi_load(self, config: Dict) -> List[Dict]:
        """Load URLs config.json

        Download multiple files from multiple URLs
        
        :param config: Dictionary that holds URL(s)
        :return: List of dictionaries
        """
        if "URLS" in config:
            files = multi_download(config["URLS"])
            return files
        return []

    def check_exists(self, file: NamedTuple) -> bool:
        """
        Check if a file has been previously downloaded by querying the database with the files's hash.
        :param file: Named tuple
        :return: True if file has been downloaded, otherwise false.
        """
        try:
            if Log.get(Log.hash == file.hash):
                click.secho("[-] This file has already been parsed, specify -f to ignore.", fg="red")
                os.remove(file.location)
                return True
        except Exception as e:
            logger.error(e)
        return False

    def extract(self, gen: Generator):
        """
        Saves the content of the gen to DB. gen is a DomainIntel Object.
        :param gen: DomainIntel generator object
        """
        temp = []
        while True:
            try:
                item = next(gen)
            except StopIteration:
                break
            else:
                if MalwareDomains.select().where(MalwareDomains.domain == item.domain).exists():
                    continue

                if len(temp) == self.CHUNK_SIZE:
                    with db.atomic():
                        for batch in chunked(temp, 200):
                            temp = [{"domain": malware_domain.domain, "type": malware_domain.type,
                                        "reference": malware_domain.reference} for malware_domain in batch]
                            MalwareDomains.insert_many(temp).execute()
                    temp.clear()
                temp.append(item)

        if temp:
            with db.atomic():
                for batch in chunked(temp, 200):
                    temp = [{"domain": malware_domain.domain, "type": malware_domain.type,
                                "reference": malware_domain.reference} for malware_domain in batch]
                    MalwareDomains.insert_many(temp).execute()

    @abc.abstractmethod
    def transform(self, path: str, type=""):
        """ Transform the data to fit our needs """
        return

    @abc.abstractmethod
    def run(self, config: Dict):
        """ Run the entire flow """
        return
