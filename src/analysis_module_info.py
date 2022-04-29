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

class _InstanceBase(anytree.NodeMixin):
    def __init__(self, name: str, parent: Optional['_InstanceBase'] = None):
        super(_InstanceBase, self).__init__()
        self.name = name
        self.parent = parent

class BranchInstance(_InstanceBase):
    def __init__(self, name: str, module_info: Optional[verible_verilog_syntax.SyntaxData] = None,
        parent: Optional['_InstanceBase'] = None, children: Optional[list['_InstanceBase']] = None):
        super().__init__(name, parent)
        self.module_info = module_info
        self.children = children if children is not None else []

    def RenderTree(self) -> None:
        for pre, _, node in anytree.RenderTree(self):
            treestr = u'%s%s' % (pre, node.name)
            instance_type = node.module_info['name'] if node.__class__.__name__ != 'UnfoundedInstance' else '-'
            print(f'{treestr.ljust(8)} ({instance_type}): {node.__class__.__name__}')

class RootInstance(BranchInstance):
    def __init__(self, name: str, module_info: Optional[verible_verilog_syntax.SyntaxData] = None,
        children: Optional[list['_InstanceBase']] = None):
        super().__init__(name, module_info, None, children)

class LeafInstance(_InstanceBase):
    def __init__(self, name: str, module_info: Optional[verible_verilog_syntax.SyntaxData] = None,
        parent: Optional['_InstanceBase'] = None):
        super().__init__(name, parent)
        self.module_info = module_info

class UnfoundedInstance(_InstanceBase):
    def __init__(self, name: str, parent: Optional['_InstanceBase'] = None):
        self.parent = parent
        super().__init__(name, parent)

class AnalysisModuleInfo:
    def __init__(self, syntax_data: dict[str, verible_verilog_syntax.SyntaxData]):
        self.modules_info = {}
        for file_path, file_data in syntax_data.items():
            self.modules_info = self.process_file_data(file_path, file_data)

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

    def _top_module(self) -> list[str]:
        name = []

        for child_name, child_info in self.modules_info.items():
            parents_name = []
            for parent_name, parent_info in self.modules_info.items():
                if child_name != parent_name:
                    if (child_name in parent_info['instances']['type']):
                        parents_name.append(parent_name)

            if len(parents_name) == 0:
                name.append(child_name)
        return name

    def _hierarchy(self, top_modules: list[str]) -> dict[str, RootInstance]:
        def hierarchy(current_name: str) -> Any:
            if current_name in self.modules_info:
                current_module = self.modules_info[current_name]
                if current_module['instances']['type']:
                    children = [
                        hierarchy(child)
                        for child in current_module['instances']['type']
                    ]
                    return BranchInstance(current_name, current_module, children=children)
                else:
                    return LeafInstance(current_name, current_module)
            else:
                return UnfoundedInstance(current_name)

        data = {}
        for top_module in top_modules:
            if top_module in self.modules_info:
                current_module = self.modules_info[top_module]
                if current_module['instances']['type']:
                    children = [
                        hierarchy(child)
                        for child in current_module['instances']['type']
                    ]
                    data[top_module] = RootInstance(top_module, current_module, children)
                else:
                    data[top_module] = RootInstance(top_module, current_module, children=None)
            else:
                data[top_module] = UnfoundedInstance(top_module)
        return data

    def parse_top_module(self) -> list[str]:
        return self._top_module()

    def parse_hierarchy(self) -> dict[str, RootInstance]:
        top_modules = self._top_module()
        return self._hierarchy(top_modules)

def setting_verible_path() -> str:
    current_dir = pathlib.Path(__file__).resolve().parent.joinpath('..', 'verible')
    os_dir = pathlib.Path('win64/verible-verilog-syntax.exe') if platform.system() == 'Windows' \
        else pathlib.Path('CentOS-7.9.2009-Core-x86_64/verible-verilog-syntax')

    return str(current_dir / os_dir)

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} VERILOG_FILE [VERILOG_FILE [...]]')
        return 1

    parser_path = setting_verible_path()
    files = sys.argv[1:]

    parser = verible_verilog_syntax.VeribleVerilogSyntax(executable=parser_path)
    analyzer = AnalysisModuleInfo( parser.parse_files(files) )
    data = analyzer.parse_hierarchy()
    for instance_name, instance_data in data.items():
        instance_data.RenderTree()

if __name__ == '__main__':
    sys.exit(main())
