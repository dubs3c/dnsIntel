from typing import Dict

from logzero import logger

from dnsintel.lib.abstractbase import AbstractBase
from dnsintel.lib.sqlpeewee import MalwareDomains


class Module(AbstractBase):

    def __init__(self):
        super().__init__()

    def transform(self, path: str, type=""):
        try:
            with open(path, "r") as file:
                for line in file:
                    if not line.startswith(("#", "Malvertising", "\n", "\r")):
                        domain = ""
                        line = line.replace("\n","")
                        if type:
                            domain = MalwareDomains(domain=line, type=type, reference="DisconnectMe")
                        yield domain
        except IOError as e:
            logger.error(e)


    def run(self, config: Dict):
        files = self.multi_load(config)
        if files:
            for object in files:
                data = self.transform(object["File"].location, object["Type"])
                self.extract(data)