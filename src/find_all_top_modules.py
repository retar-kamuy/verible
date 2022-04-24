import json
import sys
import queue

from module_list import ModuleList

class FindAllTopModules:
    def __init__(self):
        self.target_q = queue.Queue()
        self.module_list = ModuleList()

    def json_load(self, _path: str) -> dict[str, str]:
        fp = open(_path, 'r')
        _dict = json.load(fp)
        return _dict

    def input_file_data(self):
        files = ['APB_SLAVE.json', 'APB_SPI_top.json']
        for file in files:
            self.module_list.append(self.json_load(file))

    def put_all(self, items):
        for item in items:
            self.target_q.put(item)

    def run(self) -> list[str]:
        self.input_file_data()
        self.module_list.print_list()
        self.put_all(self.module_list)
        top_modules = []
        while not self.target_q.empty():
            target = self.target_q.get()
            is_top = self.module_list.is_top_module(target.dict['name'])
            if is_top == True:
                top_modules.append(target.dict['name'])
            #else:
            #    self.module_list.remove(target.dict['name'])
        print('Top module is %s' % str(top_modules))

if __name__ == '__main__':
    top_modules = FindAllTopModules()
    sys.exit(top_modules.run())