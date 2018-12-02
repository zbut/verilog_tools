from auto_tb import AutoTb
from include_parser import IncludeParser


module_path = r""
inc_path = r""
tb_path = r""

include_parser = IncludeParser(inc_path)
mp = AutoTb(module_path)


mp.dump_tb_to_file(tb_path, include_parser)