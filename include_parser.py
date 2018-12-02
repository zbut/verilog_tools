import re
from collections import OrderedDict


class IncludeParser(object):
    """
    Parses a given verilog file with macro definitions
    """
    _MACRO_RE = "\s*`define\s*(?P<name>\w*)\s+(?P<definition>[\w '`+-]+)"

    def __init__(self, file_path):
        self._macros = OrderedDict()
        self._macros_resolved = {}
        with open(file_path) as f:
            data = f.read()
        self._parse_include_data(data)
        self._resolve_macro_values()

    def _parse_include_data(self, include_data):
        """
        Parses the data given as text
        """
        for mo in re.finditer(self._MACRO_RE, include_data):
            definition = mo.group("definition")
            if definition.isnumeric():
                numeric_definition = int(definition)
            elif "'d" in definition:
                numeric_definition = int(definition[definition.find("'d") + 2:])
            elif "'b" in definition:
                numeric_definition = int(definition[definition.find("'b") + 2:], 2)
            elif "'h" in definition:
                numeric_definition = int(definition[definition.find("'h") + 2:], 16)
            else:
                numeric_definition = definition
            if not isinstance(numeric_definition, int):
                numeric_definition = numeric_definition.replace("`", "")
            self._macros[mo.group("name")] = numeric_definition

    def _resolve_macro_values(self):
        """
        Go over the macros that do not have their number configured and
        evaluate them using the other macros
        """
        #print(self._macros)
        for macro, definition in self._macros.items():
            if not isinstance(definition, int):
                if ":" in definition or "{" in definition:
                    continue
                print(macro, definition)
                definition = eval(definition, self._macros_resolved)
            assert isinstance(definition, int)
            self._macros_resolved[macro] = definition

    def get_macros_dict(self):
        return self._macros_resolved
