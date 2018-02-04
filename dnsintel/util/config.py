import os
import json
import importlib.util
from typing import List, Dict

from logzero import logger

class Config(object):
    """docstring for Config"""
    def __init__(self):
        self.path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../../', 'config.json'))
        self._output_location = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../../', 'output/'))
        self.download_location = os.path.abspath(os.path.join(self._output_location, "download"))
        self.modules_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'modules'))
        self.force = False
        self.selected_module = ""
        self.FORMAT = ""

        if not os.path.exists(self.path):
            print("config file does not exists")
            quit()
        try:
            if not os.path.exists(self.download_location):
                os.makedirs(self.download_location)
        except OSError as e:
            logger.error(e)
            quit()

        self.configuration = {}   
        self.parse_config()

        self.modules = {}
        self.loaded_modules = {}
        self.BLACKHOLE = self.configuration['BLACKHOLE']
        self.BLACKLIST_FILE = self.configuration['BLACKLIST_FILE']

    @property
    def output_location(self):
        return self._output_location

    @output_location.setter
    def output_location(self, location):
        self._output_location = location

    def parse_config(self):
        try:
            with open(self.path, "r") as f:
                self.configuration = json.load(f)
        except Exception as e:
            logger.error(e)
            quit()

    def get_sources(self) -> List[Dict]:
        lol = [ source for source in self.configuration["sources"] ]
        return lol[0]

    def find_modules(self) -> Dict:
        if os.path.exists(self.modules_path):
            for module in os.listdir(self.modules_path):
                module_name = module.replace(".py", "")
                if module_name in self.get_sources():
                    if self.configuration["sources"][0][module_name]['ENABLED']:
                        self.modules[module] = os.path.join(self.modules_path, module)
        return self.modules

    def load_module(self, module_name: str, module_path: str) -> bool:
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location("Module", module_path)
            if spec is None:
                logger.warn(f"The module {module_name} needs to have a class called Module")
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.loaded_modules[module_name] = module.Module()
            return True
        else:
            logger.warn(f'Module: {module_name} not found')
            return False

    def load_modules(self) -> Dict:
        loaded_modules = self.find_modules()
        if loaded_modules:
            for module, path in loaded_modules.items():
                module_name = module.replace(".py", "")
                self.load_module(module_name, path)
        else:
            logger.info("No modules found")
        return self.loaded_modules
        





        