#
# Copyright 2022 Takumi Hoshi.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This code is translated Verible's SystemVerilog Syntax tool in Python into TypeScript.
# the tool is obtained the Apache License, Version 2.0;
#
# Verible's repository at:
#     https://github.com/chipsalliance/verible
'''Print module name, ports, parameters and imports.

Usage: print_modules.py PATH_TO_VERIBLE_VERILOG_SYNTAX \\
                        VERILOG_FILE [VERILOG_FILE [...]]

This example shows how to use ``verible-verilog-syntax --export_json ...``
output to extract information about module declarations found in System Verilog
source files. Extracted information:

* module name
* module port names
* module parameter names
* module imports
* module header code
'''
import sys
import platform
import pathlib
import anytree
from typing import Any, Optional

import verible_verilog_syntax

class InstanceInfo(anytree.NodeMixin):
    def __init__(self, name: str, module_info: Optional[verible_verilog_syntax.SyntaxData] = None,
        parent: Optional['InstanceInfo'] = None, children: Optional[list['InstanceInfo']] = None):
        super(InstanceInfo, self).__init__()
        self.name = name
        self.module_info = module_info
        self.parent = parent
        if children:
            self.children = children

    def RenderTree(self) -> None:
        for pre, _, node in anytree.RenderTree(self):
            treestr = u'%s%s' % (pre, node.name)
            print(treestr.ljust(8), self.module_info['name'])

class AnalysisModuleInfo:
    def process_file_data(self, path: str, data: verible_verilog_syntax.SyntaxData) -> dict[str, dict[str, Any]]:
        '''Print information about modules found in SystemVerilog file.
    
        This function uses verible_verilog_syntax.Node methods to find module
        declarations and specific tokens containing following information:

        * module name
        * module port names
        * module parameter names
        * module imports
        * module header code

        Args:
            path: Path to source file (used only for informational purposes)
            data: Parsing results returned by one of VeribleVerilogSyntax' parse_*
                  methods.
        '''
        if not data.tree:
            return

        modules_info = {}

        # Collect information about each module declaration in the file
        for module in data.tree.iter_find_all({'tag': 'kModuleDeclaration'}):
            module_info = {
                'path': '',
                'name': '',
                'ports': [],
                'parameters': [],
                'imports': [],
                'instances': {
                    'name': [],
                    'type': []
                }
            }

            module_info['path'] = path

            # Find module header
            header = module.find({'tag': 'kModuleHeader'})
            if not header:
                continue

            # Find module name
            name = header.find({'tag': ['SymbolIdentifier', 'EscapedIdentifier']},
                                iter_=anytree.PreOrderIter)
            if not name:
                continue
            module_info['name'] = name.text

            # Get the list of ports
            for port in header.iter_find_all({'tag': ['kPortDeclaration', 'kPort']}):
                port_id = port.find({'tag': ['SymbolIdentifier', 'EscapedIdentifier']})
                module_info['ports'].append(port_id.text)

            # Get the list of parameters
            for param in header.iter_find_all({'tag': ['kParamDeclaration']}):
                param_id = param.find({'tag': ['SymbolIdentifier', 'EscapedIdentifier']})
                module_info['parameters'].append(param_id.text)

            # Get the list of imports
            for pkg in module.iter_find_all({'tag': ['kPackageImportItem']}):
                module_info['imports'].append(pkg.text)

            # Get the list of instances
            #    module_info.instances = {name: [], type: []};
            for inst in module.iter_find_all({'tag': ['kGateInstance']}):
                inst_id = inst.find({'tag': ['SymbolIdentifier', 'EscapedIdentifier']})
                module_info['instances']['name'].append(inst_id.text)
            for type in module.iter_find_all({'tag': ['kInstantiationType']}):
                type_id = type.find({'tag': ['SymbolIdentifier', 'EscapedIdentifier']})
                if not type_id:
                    continue
                module_info['instances']['type'].append(type_id.text)

            modules_info[module_info['name']] = module_info
        return modules_info

    def top_module(self, modules_info: dict[str, dict[str, Any]]) -> list[str]:
        _top_module = []

        for child_name, child_info in modules_info.items():
            parents_name = []
            for parent_name, parent_info in modules_info.items():
                if child_name != parent_name:
                    if (child_name in parent_info['instances']['type']):
                        parents_name.append(parent_name)

            if len(parents_name) == 0:
                _top_module.append(child_name)
        return _top_module

    def hierarchy(self, modules_info: dict[str, verible_verilog_syntax.SyntaxData], top_modules: list[str]) -> None:
        #def transform(module_info)
        for top_module in top_modules:
            children_module = []
            children_module.insert(0, modules_info[top_module]['name'])

            module_info = modules_info[children_module.pop(0)]
            print(module_info)

            if not module_info:
                return None
            if module_info['instances']['type']:
                children = [child_type for child_type in module_info['instances']['type']]
                children_node = InstanceInfo(children[0], module_info=None, parent=None, children=None)
                current_node = InstanceInfo(module_info['name'], module_info, parent=None, children=[children_node])
                current_node.RenderTree()

            #while children_module:
            #    current_node = InstanceInfo(modules_info[top_module]['name'], modules_info[top_module], parent=None)
            #    module_info = modules_info[children_module.pop(0)]
            #    if not module_info:
            #        continue
            #    print(module_info)
            #    if not module_info['instances']:
            #        children_module = module_info['instances']['name'] + children_module
            #        child_nodeInstanceInfo(modules_info[top_module]['name'], modules_info[top_module], parent=None)

    def RenderTree(self, node: InstanceInfo) -> None:
        for pre, _, _node in anytree.RenderTree(node):
            treestr = u'%s%s' % (pre, _node.name)
            print(treestr.ljust(8), node.module_info['name'])

def setting_verible_path() -> str:
    current_dir = pathlib.Path(__file__).resolve().parent.joinpath('..', 'verible')
    os_dir = pathlib.Path('win64/verible-verilog-syntax.exe') if platform.system() == 'Windows' \
        else pathlib.Path('CentOS-7.9.2009-Core-x86_64/verible-verilog-syntax')

    return str(current_dir / os_dir)



def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} PATH_TO_VERIBLE_VERILOG_SYNTAX ' +
              'VERILOG_FILE [VERILOG_FILE [...]]')
        return 1
  
    #parser_path = sys.argv[1]
    parser_path = setting_verible_path()
    files = sys.argv[1:]
  
    parser = verible_verilog_syntax.VeribleVerilogSyntax(executable=parser_path)
    data = parser.parse_files(files)
  
    analyzer = AnalysisModuleInfo()
    modules_info = {}
    for file_path, file_data in data.items():
        modules_info = analyzer.process_file_data(file_path, file_data)

    top_modules = analyzer.top_module(modules_info)
    print(top_modules)
    analyzer.hierarchy(modules_info, top_modules)

if __name__ == '__main__':
    sys.exit(main())