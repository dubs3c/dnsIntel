import sqlite3
import time
import os
from typing import List, Dict, Generator
from logzero import logger
from dnsintel.lib.domainintel import DomainIntel

class SQL:
    """ Class for handling SQLite3 operations """
    def __init__(self):
        self.DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'db'))
        self.DATABASE = os.path.abspath(os.path.join(self.DATABASE_PATH, 'malware_domains.db'))
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Connect to the sqlite3 database
        :return:
        """
        if not os.path.exists(self.DATABASE_PATH):
            os.mkdir(self.DATABASE_PATH)
        self.conn = sqlite3.connect(self.DATABASE)
        self.cursor = self.conn.cursor()
        self.cursor.row_factory = sqlite3.Row

    def disconnect(self):
        """
        Disconnect from the sqlite3 database
        :return:
        """
        self.conn.close()

    def database_init(self):
        """
        Initialize the database
        :return:
        """
        self.connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS malware_domains (\
            domain text PRIMARY KEY, \
            type text, \
            reference text, \
            created TIMESTAMP) \
            ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS log (\
            hash TEXT PRIMARY KEY, \
            path text, \
            created TIMESTAMP) \
            ''')
        self.conn.commit()
        self.disconnect()

    def hash_exists(self, hash_: str) -> bool:
        """
        Check if a given hash of a file exists in DB
        :param hash_: The hash of a file
        :return: True if exists, otherwise false
        """
        exists = False
        try:
            exists = self.cursor.execute("SELECT 1 FROM log WHERE hash=?", (hash_,)).fetchone() is not None
        except Exception as e:
            logger.error(e)
        return exists

    def row_exists_by(self, field: str, value: str) -> bool:
        """
        Check if a value exists in DB by field name
        :param field: Database field
        :param value: Value to check for
        :return: True if exists, otherwise false
        """
        exists = False
        try:
            exists = self.cursor.execute("SELECT EXISTS (SELECT 1 FROM malware_domains WHERE ?=?)",
                                      (field, value,)).fetchone() is True
        except Exception as e:
            logger.error(e)
        return exists

    def get_domain(self, domain: str) -> Dict:
        self.cursor.execute("SELECT domain, type, reference, created FROM malware_domains WHERE domain=?", (domain,))
        row = self.cursor.fetchone()
        if row is not None:
            return {"domain": row["domain"], "type": row["type"], "reference": row["reference"],
                    "created": row["created"]}
        else:
            return {}

    def get_all_domains(self, format="") -> Generator:
        self.cursor.execute("SELECT domain, type, reference, created FROM malware_domains")
        while True:
            try:
                items = self.cursor.fetchmany(size=1000)
            except StopIteration:
                break
            else:
                if items:
                    domains = [DomainIntel(item["domain"], format, item["type"],item["reference"]) for item in items]
                    yield domains
                else:
                    break


    def query_add(self, domain: str, type: str, reference: str):
        """
        Add a single domain to DB
        :param domain: The domain
        :param type: Type of domain
        :param reference: Which source reported it
        """
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        try:
            self.cursor.execute("INSERT or IGNORE INTO malware_domains(domain, type, reference, created) "
                                "VALUES(?,?,?,?)", (domain, type, reference, created))
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def query_add_many(self, domains: List[DomainIntel]):
        """
        Add a list of domains to DB
        :param domains: List of DomainIntel objects
        """
        temp_list = [(x.domain, x.type, x.reference, x.created) for x in domains]
        if temp_list:
            try:
                self.cursor.executemany("INSERT or IGNORE INTO malware_domains(domain, type, reference, created) "
                                        "VALUES(?,?,?,?)", temp_list)
                self.conn.commit()
            except Exception as e:
                logger.error(e)

    def save_log(self, hash_: str, path: str):
        """
        Save the hash of the file and it's path to the log table
        :param hash_: Hash of the downloaded file
        :param path: Path of the downloaded file
        :return:
        """
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        try:
            self.cursor.execute("INSERT INTO log(hash, path, created) VALUES(?,?,?)", (hash_, path, created))
            self.conn.commit()
        except Exception as e:
            logger.error(e)

