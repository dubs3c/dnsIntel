from dnsintel.lib.abstractbase import AbstractBase
from dnsintel.lib.domainintel import DomainIntel
from typing import Dict
from logzero import logger

class Module(AbstractBase):

    def __init__(self):
        super().__init__()

    def transform(self, path: str, type=""):
        try:
            with open(path, "r") as file:
                for count, line in enumerate(file):
                    if not line.startswith(("#", "Malvertising", "\n", "\r")):
                        domain = ""
                        if type:
                            domain = DomainIntel(line, self.FORMAT, type, "DisconnectMe")

                        yield domain
        except IOError as e:
            logger.error(e)


    def run(self, config: Dict):
        files = self.multi_load(config)
        for object in files:
            data = self.transform(object["File"].location, object["Type"])
            self.extract(data)