from jinja2 import Environment, PackageLoader
from module_parser import ModuleParser
import os
import logging
import random

logger = logging.getLogger(__name__)
TEMPLATE_PATH = "tb_template.v"


class AutoTb(object):
    NOF_RAND_VALUES = 3000

    def __init__(self, file_path):
        # Parse the verilog file
        module_parser = ModuleParser(file_path)
        self.parameters = module_parser.get_parameters()
        self.inputs = module_parser.get_inputs()
        self.outputs = module_parser.get_outputs()
        self.inst_name = os.path.splitext(os.path.basename(file_path))[0]
        self.tb_name = self.inst_name + "_tb"
        # Build a dict from the parameters
        parameters_dict = {parameter.name: parameter.default_value for parameter in self.parameters}
        self._parameters_dict = {}
        for name, default_value in parameters_dict.items():
            self._parameters_dict[name] = eval(default_value, {}, parameters_dict)
        self.clk_input = self._find_clk_signal()
        self.found_clk = self.clk_input is not None
        self.rst_input = self._find_rst_signal()
        self.found_rst = self.rst_input is not None
        self.is_rst_negative = self.rst_input.name.endswith("_n") if self.found_rst else None
        self.list_of_input_dicts = []

    def _find_clk_signal(self):
        for input_wire in self.inputs:
            if "clk" in input_wire.name.lower() or "clock" in input_wire.name.lower():
                return input_wire
        logger.error("Could not find clk signal")

    def _find_rst_signal(self):
        for input_wire in self.inputs:
            if "rst" in input_wire.name.lower() or "reset" in input_wire.name.lower():
                return input_wire
        logger.error("Could not find rst signal")

    def dump_tb_to_file(self, tb_path, include_parser=None):
        """
        Dumps a test bench to the given path
        :param tb_path: The path to dump the tb to
        :param include_parser: Optional IncludeParser object to be used for width evaluation
        :return:
        """
        eval_dict = dict(self._parameters_dict)
        if include_parser is not None:
            eval_dict.update(include_parser.get_macros_dict())
        for input_wire in self.inputs:
            input_wire.update_numeric_width(eval_dict)
        for output_wire in self.outputs:
            output_wire.update_numeric_width(eval_dict)
        self._create_values_for_inputs()
        env = Environment(loader=PackageLoader('verilog_tools', 'templates'))
        template = env.get_template(TEMPLATE_PATH)
        tb_data = template.render(TB=self)
        tb_file = open(tb_path, "w")
        tb_file.write(tb_data)

    def _create_values_for_inputs(self):
        for i in range(self.NOF_RAND_VALUES):
            inputs_dict = {}
            for input_signal in self.inputs:
                if (self.found_clk and input_signal.name == self.clk_input.name) or \
                        (self.found_rst and input_signal.name == self.rst_input.name):
                    continue
                value = random.randrange(0, 1 << input_signal.width_numeric, 1)
                inputs_dict[input_signal] = value
            self.list_of_input_dicts.append(inputs_dict)


