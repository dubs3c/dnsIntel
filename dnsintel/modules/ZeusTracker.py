from dnsintel.lib.abstractbase import AbstractBase
from dnsintel.lib.sqlpeewee import MalwareDomains

from logzero import logger

class Module(AbstractBase):

    def __init__(self):
        super().__init__()

    def transform(self, path: str):
        try:
            with open(path, "r") as file:
                for line in file:
                    if line.startswith("#"):
                        continue
                    if len(line.strip()) == 0 :
                        continue

                    line = line.replace("\r", "").replace("\n", "")
                    domain = MalwareDomains(domain=line, type="Zeus", reference="ZeusTracker")
                    yield domain

        except IOError as e:
            logger.error(e)


    def run(self, config):
        file = self.load(config)
        if file:
            data = self.transform(file.location)
            self.extract(data)
