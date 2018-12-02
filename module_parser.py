import re
import logging
import sys

logger = logging.getLogger(__name__)


class Wire(object):
    """
    A wire definition in the design
    """
    def __init__(self, name, width):
        self.name = name
        self.width = width
        self.width_numeric = None

    def update_numeric_width(self, eval_dict):
        """
        Tries to find the numeric width of the wire using parameters and macros
        :param eval_dict: A dict of parmeters and they expressions
        """
        # If width is already a number, do nothing
        if isinstance(self.width, int):
            self.width_numeric = self.width
            return
        self.width_numeric = eval(self.width.replace("`", ""), eval_dict)
        if not isinstance(self.width_numeric, int):
            logger.error("Could not evaluate width {} of wire {}".format(self.width_numeric, self.name))


class Input(Wire):
    pass


class Output(Wire):
    pass


class Parameter(object):
    def __init__(self, name, default_value):
        self.name = name
        self.default_value = default_value


class ModuleParser(object):
    _MODULE_RE = r"^module\s+(?P<module_name>\w+)\s+(?:(?P<parameters>#\(.*?\)))\s*\((?P<interface>.*?)\);\s*(?P<body>.*?)endmodule"
    _PARAMETERS_RE = r"parameter\s+(?P<param_name>\w+)\s*=\s*(?P<default_value>[-\d\w \+*`]+)"
    _INPUT_RE = r"input\s+(?:wire)\s*(?P<width>\[.*?\])?\s*(?P<name>\w+)"
    _OUTPUT_RE = r"output\s+(?:wire|reg)\s*(?P<width>\[.*?\])?\s*(?P<name>\w+)"

    def __init__(self, file_path):
        self._parameters = []
        self._inputs = []
        self._outputs = []
        with open(file_path) as f:
            data = f.read()
        self._parse_module_data(data)

    def _parse_module_data(self, data):
        # First, parse the module data
        mo = re.search(self._MODULE_RE, data, re.MULTILINE + re.DOTALL)
        if not mo:
            logger.critical("Could not parse module. Do you have a special module file?")
            sys.exit(1)
        # Parse parameters
        if "parameters" in mo.groupdict():
            self._parse_parameters(mo.group("parameters"))
        # Parse interface
        self._parse_interface(mo.group("interface"))

    def _parse_parameters(self, parameters_text):
        """
        Parse the test of the parameters part of the module
        :param parameters_text: The parameters text
        """
        for mo in re.finditer(self._PARAMETERS_RE, parameters_text):
            self._parameters.append(Parameter(mo.group("param_name"), mo.group("default_value")))

    def _parse_interface(self, interface_data):
        """
        Parse the interface data
        :param interface_data: Text of the interface
        """
        # Look for inputs
        for mo in re.finditer(self._INPUT_RE, interface_data):
            self._inputs.append(Input(mo.group("name"), self.parse_width(mo.group("width"))))
        # Look for outputs
        for mo in re.finditer(self._OUTPUT_RE, interface_data):
            self._outputs.append(Output(mo.group("name"), self.parse_width(mo.group("width"))))

    @staticmethod
    def parse_width(width_text):
        """
        Parses the width text of an input/output
        :param width_text: Width text such as P_ADDR_WIDTH - 1 : 0
        :return: The width of the signal as a text. (P_ADDR_WIDTH) for the example.
        """
        if width_text is None:
            return "1"
        if ":" in width_text:
            mo = re.search("\s*(?P<width>[\w\s+-<()`*]+)\s*-\s*1\s:", width_text)
            if mo:
                return mo.group("width")
        logging.error("Could not parse width text {}".format(width_text))

    def get_parameters(self):
        return self._parameters

    def get_inputs(self):
        return self._inputs

    def get_outputs(self):
        return self._outputs
