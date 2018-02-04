#!/usr/local/bin/env python3.6

import abc
import os
from typing import List, Dict, Tuple, Generator, NamedTuple
import click
from dnsintel.util.sql import SQL
from dnsintel.util.config import Config
from dnsintel.util.util import download, append_to_blacklist, multi_download
from logzero import logger

class AbstractBase(object):
    """Abstract class containing common methods and skeleton for modules"""

    def __init__(self):
        self.config = Config()
        self.BLACKLIST_FILE = ""
        self.BLACKHOLE = ""
        self.CHUNK_SIZE = 1000
        self.cursor = None
        self.force = False
        self.load_config()
        self.db = SQL()

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
            if not self.force:
                if not self.check_exists(file):
                    self.db.save_log(file.hash, file.location)
                    return file
        return ()

    def multi_load(self, config: Dict) -> List[Dict]:
        """
        Download multiple files from multiple URLs
        :param config: Dictionary that holds URL(s)
        :return: List of dictionaries
        """
        if "URLS" in config:
            files = multi_download(config["URLS"])
            filtered = []
            for file in files:
                if not self.force:
                    if not self.check_exists(file["File"]):
                        filtered.append(file)
                        self.db.save_log(file["File"].hash, file["File"].location)
            return filtered
        return []

    def check_exists(self, file: NamedTuple) -> bool:
        """
        Check if a file has been previously downloaded by querying the database with the files's hash.
        :param file: Named tuple
        :return: True if file has been downloaded, otherwise false.
        """
        try:
            if self.db.hash_exists(file.hash):
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
            except StopIteration as e:
                break
            else:
                if self.db.row_exists_by("domain", item.domain):
                    continue
                if len(temp) == self.CHUNK_SIZE:
                    self.db.query_add_many(temp)
                    append_to_blacklist(temp)
                    temp.clear()
                temp.append(item)
        if temp:
            append_to_blacklist(temp)

    @abc.abstractmethod
    def transform(self, path: str, type=""):
        """ Transform the data to fit our needs """
        return

    @abc.abstractmethod
    def run(config: Dict):
        """ Run the entire flow """
        return
