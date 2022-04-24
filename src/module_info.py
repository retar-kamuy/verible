import os
import sys
import json
from typing import Optional

from logger import Logger

class ModuleInfo:
    #def __init__(self, dict_data: Optional[dict[str, str]] = None,
    #            file: Optional[str] = None, name: Optional[str] = None,
    #            imports: Optional[list[str]] = None, includes: Optional[list[str]] = None,
    #            instances: Optional[dict[str, str]] = None):
    def __init__(self, module_info: Optional[list[dict[str, str]]] = None):
        self.list_of_module_info = []
        if module_info:
            self.list_of_module_info.extend(module_info)
        #self.dict_data = {
        #    'file': '',
        #    'name': '',
        #    'imports': [],
        #    'includes': [],
        #    'instances': {
        #        'name': [],
        #        'type': []
        #    }
        #}
        self.logger = Logger(__name__, 'DEBUG')

    def load_json(self, file: str) -> dict[str, str]:
        if os.path.isfile(file) != True:
            raise ValueError('%s: Cannot open file "%s"' % self.__class__, file)
        fp = open(file, 'r')
        dict_data = json.load(fp)
        return dict_data

    def set_module_info(self, module_info: Optional[list[dict[str, str]]] = None, json_files: Optional[list[str]] = None):
        if json_files:
            for file in json_files:
                dict_data = self.load_json(file)
                self.list_of_module_info.append(dict_data)
                self.logger.debug('Set module_info "%s"' % dict_data['file'])
                self.logger.debug(json.dumps(dict_data, indent=4))
        else:
            self.list_of_module_info.extend(module_info)

    #def set_module_info(self, file: str, name: str,
    #            imports: Optional[list[str]] = None, includes: Optional[list[str]] = None,
    #            instances: Optional[dict[str, str]] = None):
    #    if name is None:
    #        raise ValueError('%s: Module is None' % self.__class__)
    #    self.dict_data['file'] = file
    #    self.dict_data['name'] = name
    #    self.dict_data['imports'] = imports
    #    self.dict_data['includes'] = includes
    #    if instances is None:
    #        self.dict_data['instances'] = {
    #            'name': [],
    #            'type': []
    #        }
    #    else:
    #        self.dict_data['instances'] = {
    #            'name': instances['name'],
    #            'type': instances['type']
    #        }

    def get_names(self) -> list[str]:
        names = []
        for module_info in self.list_of_module_info:
            names.append(module_info['name'])
        return names

    def get_all_of_module_info(self) -> list[dict[str, str]]:
        return self.list_of_module_info

    def get_module_info(self, name: str) -> dict[str, str]:
        for module_info in self.list_of_module_info:
            if ('name', name) in module_info.items():
                return module_info
        self.logger.warning('Cannot found module name "%s"' % name)
        return None

    def search_top_module(self) -> list[str]:
        top_modules = []
        search_names = self.get_names()

        while search_names:
            self.logger.debug('Search names = %s' % str(search_names))
            module_name = search_names.pop(0)
            parents = self.search_parent(module_name)
            if not parents:
                top_modules.append(module_name)

        return top_modules

    def search_parent(self, child_name: str) -> dict[str, str]:
        child_names = []
        parent_modules = []

        self.logger.debug('Search parents of "%s", candidates = %s' % (
            child_name, str([module_info['name'] for module_info in self.list_of_module_info])))
        for module_info in self.list_of_module_info:
            for i in range(len(module_info['instances']['type'])):
                instance_name = module_info['instances']['name'][i]
                instance_type = module_info['instances']['type'][i]
                if child_name == instance_type:
                    child_names.append(instance_name)
                    parent_modules.append(module_info)
                    self.logger.debug('Hit! Module "%s" is %s parent' % (module_info['name'], child_name))
                    break
        if not parent_modules:
            self.logger.debug('%s is not parent. Therefere, top module' % child_name)

        return parent_modules
