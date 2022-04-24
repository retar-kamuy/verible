import sys
sys.path.append('anytree')
sys.path.append('six')
from typing import Optional
from anytree import Node, RenderTree

from module_info import ModuleInfo

class InstanceNode(Node):
    def __init__(self, name: str, _type: str, file: Optional[str] = None, parent: Optional['InstanceNode'] = None):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.type = _type
        self.file = file

class InstanceInfo:
    def __init__(self, module_info: list[dict[str, str]]):
        self.list_of_instance_info = []
        self.list_of_module_info = ModuleInfo(module_info)
        self.top_modules = []

    def set_top_module(self, names: list[str]):
        self.top_modules = names

    def print_tree(self):
        print(RenderTree(self.list_of_instance_info[0]))

    def append(self, name: str, _type: str, file: Optional[str] = None, parent: Optional['InstanceNode'] = None) -> 'InstanceNode':
        new_node = InstanceNode(name, _type, file=file, parent=parent)
        self.list_of_instance_info.append(new_node)
        return new_node

    def main(self):
        for top_module in self.top_modules:
            print(f'top_module = {top_module}')
            module_info = self.list_of_module_info.get_module_info(top_module)
            current_node = self.append(module_info['name'], module_info['name'], file=module_info['file'], parent=None)

            child_names = {'name': [], 'type': []}
            child_names['name'].extend(module_info['instances']['name'])
            child_names['type'].extend(module_info['instances']['type'])
            print(f'child_names = {child_names}')

            search_instances = []
            while child_names['name']:
                print(f'child_names = {child_names}')
                instance_name = child_names['name'].pop(0)
                instance_type = child_names['type'].pop(0)
                module_info = self.list_of_module_info.get_module_info(instance_type)

                if module_info:
                    child_node = self.append(instance_name, instance_type, file=module_info['file'], parent=current_node)
                    child_names['name'][0:0] = module_info['instances']['name']
                    child_names['type'][0:0] = module_info['instances']['type']
                else:
                    child_node = self.append(instance_name, instance_type, parent=current_node)

                #module_info = self.list_of_module_info.get_module_info(instance_type)
            print(RenderTree(current_node))
