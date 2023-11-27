import re, os, subprocess, tkinter


class TranslateCmd:
	def __init__(self, in_file):
		super(TranslateCmd, self).__init__()
		self.input_file = in_file

	def info_replace(self, dir_list, replace_str, pattern):
		required_file_name = re.match(pattern, replace_str).group(1)
		# get file name
		util_file_name = None
		for dirs in dir_list:
			for root, util_dirs, files in os.walk(dirs):
				for file in files:
					file_path = os.path.join(root, file)
					if os.path.basename(file_path) == required_file_name:
						util_file_name = file_path
		if util_file_name:
			# Do replacements
			with open(util_file_name) as stream:
				info = stream.read()
			return info
		else:
			print("EDP_ERROR: Cannot find util file " + required_file_name + " skip util replacement")
			return replace_str

	def util_apply(self, util_dir_list, pattern=r'^#\s+import\s+util\s+(.*)\s*'):
		# Apply the util transformation into the command
		# eg:
		#   # import util step1.tcl
		# Read in information
		recursion_flag = 0
		with open(self.input_file) as stream:
			stream_info = stream.readlines()
		# Write out information
		with open(self.input_file, "w") as stream:
			for line in stream_info:
				if re.search(pattern, line):
					line = self.info_replace(util_dir_list, line, pattern)
					if isinstance(line, list):
						for ele in line:
							stream.write(ele)
							if re.search(pattern, ele):
								recursion_flag = 1
				else:
					stream.write(line)
		# Update 20231124
		if recursion_flag:
			self.util_apply(util_dir_list, pattern)

	def count_symbol(self, input_str, ini_num, add_syn="{", minus_syn="}"):
		for i, c in enumerate(input_str):
			if c == add_syn:
				ini_num = ini_num + 1
			elif c == minus_syn:
				ini_num = ini_num - 1
		return ini_num

	def transform_info(self, input_str, mode="tcl"):
		# python and tcl mode supported
		if mode == "python":
			for ele in ["\""]:
				input_str = input_str.replace(ele, "\\" + ele)
			input_str = "print(\"" + input_str + "\")" + "\n"
		elif mode == "tcl":
			for ele in ["\"", "$", "{", "}", "[", "]", "(", ")"]:
				input_str = input_str.replace(ele, "\\" + ele)
			input_str = "puts \"" + input_str + "\"" + "\n"

		return input_str

	def translate_cmd(self, output_file="", file_type="tcl", start_pattern="initialize finished", end_pattern="initialize started"):
		symbol = 0
		remain_flags = True
		in_circular = False
		mark_insert = False
		# setup tags for if/while/for/foreach/else
		pattern1 = r'if\s*\{\s*.*\s*\}\s*\{'
		pattern2 = r'while\s*\{\s*.*\s*\}\s*\{'
		pattern3 = r'for\s*\{\s*.*\s*\}\s*\{'
		pattern4 = r'foreach\s*.*\{'
		# else statement may contain in if statement
		pattern_else = r'\}\s*else\s*\{'
		pattern_elseif = r'\}\s*else\s*if\s*\{'
		# mark_pattern is required for var initialization
		# "?!" means case-insensitive
		start_pattern_en = r"(?i)#\s*%s" % start_pattern
		# print(start_pattern_en)
		end_pattern_en = r"(?i)#\s*%s" % end_pattern
		# print(end_pattern_en)

		# Refresh target_file
		if output_file != "":
			if os.path.exists(output_file):
				os.remove(output_file)
			target_stream = open(output_file, 'w')
		else:
			target_file = os.path.dirname(self.input_file) + "/transformed.tcl"
			if os.path.exists(target_file):
				os.remove(target_file)
			target_stream = open(target_file, 'w')

		with open(self.input_file) as f:
			for line in f:
				line = line.rstrip()
				if re.search(start_pattern_en, line):
					# print("find start_mark pattern", line)
					# The line above mark_pattern will not be translated
					mark_insert = True
				if re.search(end_pattern_en, line):
					print("find end_mark pattern", line)
					# The line below end_pattern will not be translated
					mark_insert = False
				if mark_insert:
					# get else statement?
					else_statement = re.search(pattern_else, line) or re.search(pattern_elseif, line)
					# get if/while/for/foreach statement?
					cycle_statement = False
					# turn off foreach and while
					# for ele in [pattern1, pattern2, pattern3, pattern4]:
					for ele in [pattern1]:
						if re.search(ele, line):
							cycle_statement = True
					symbol = self.count_symbol(line, symbol)
					# Initialization done
					# if not cycle_statement and not symbol and not else_statement:
					if not cycle_statement and not else_statement and symbol != 0:
						line = line.lstrip()
						target_stream.write(self.transform_info(line, mode=file_type))
					elif cycle_statement and symbol == 1:
						in_circular = True
						target_stream.write(line.lstrip() + "\n")
					elif else_statement and symbol == 1:
						target_stream.write(line.lstrip() + "\n")
					elif symbol == 0:
						if in_circular:
							target_stream.write(line.lstrip() + "\n")
						else:
							target_stream.write(self.transform_info(line, mode=file_type))
						in_circular = False
					else:
						target_stream.write(self.transform_info(line, mode=file_type))
				else:
					target_stream.write(line.lstrip() + "\n")
					target_stream.write(self.transform_info(line, mode=file_type))
		# Get transform.tcl
		target_stream.close()

	def main_func(self, translated_file=None, debug=False):
		# Get filetype
		tail_info = self.input_file.split(".")[-1]
		if tail_info == "py":
			file_type = "python"
			interpreter = "python3"
		elif tail_info == "cmd" or tail_info == "tcl":
			file_type = "tcl"
			interpreter = "tclsh"
		else:
			interpreter = None
			file_type = None

		# The mid_file is translate_cmd's output_file here
		# Go to the working dir
		main_workdir = os.getcwd()
		work_dir = os.path.dirname(self.input_file)
		os.system("cd %s" % work_dir)
		mid_file = os.path.dirname(self.input_file) + "/" + os.path.basename(self.input_file) + ".mid"
		self.translate_cmd(output_file=mid_file, file_type=file_type)

		if not translated_file:
			translated_file = self.input_file

		TranslateCmd.translate_file(self.input_file, mid_file, translated_file, interpreter, debug=debug)
		os.system("cd %s" % main_workdir)

	@staticmethod
	def translate_file(in_file, mid_file, translated_file, interpreter=None, debug=False):
		if interpreter:
			try:
				output = subprocess.check_output([interpreter, mid_file], stderr=subprocess.STDOUT)
				os.system("%s %s > %s" % (interpreter, mid_file, translated_file))
				if not debug:
					os.remove(mid_file)
			except subprocess.CalledProcessError as e:
				os.system("%s %s 2 >& %s" % (interpreter, mid_file, translated_file))
				print("[EDP_ERROR] Gen cmd %s failed, please try to debug and fix it" % in_file)
				if not debug:
					os.remove(mid_file)
					# os.remove(in_file)


	###########################################################################
	## This function works for switch tcl file into a python dict after source
	## Return a python_dict contains all var_info from the source interp
	## Example:
	## You may also filter the env not required if you want:
	## get_dict_interp(tcl_file, fill_pattern="str1|str2|etc") -> a dict returned
	## But if dict.keys() contains "tk_/err/tcl_/auto/env/argv0/str1/str2/etc"
	## these info will be ignored
	###########################################################################
	@staticmethod
	def get_dict_interp(tcl_file, fill_pattern_source="tk_|err|tcl_|auto|env|argv0", fill_pattern=""):
		tcl_interp = tkinter.Tcl()
		# Source script in the interp then the interp get all required information
		tcl_interp.eval("source {}".format(tcl_file))
		info_dict = dict()
		# Get all vars name
		info_lists = list(tcl_interp.eval("info vars").split(" "))
		if fill_pattern != "":
			# Check fill_pattern which is not required
			fill_pattern_source = fill_pattern_source + "|" + fill_pattern

		for ele in info_lists:
			result = re.search(fill_pattern_source, ele)
			if not result:
				# All not filterd ele:
				# Check if array or not in the tcl vars
				if int(tcl_interp.eval("array exists {}".format(ele))) == 1:
					info_dict[ele] = dict()
					# Get this array info and restore it into the dict
					tcl_dict = list(tcl_interp.eval("array names {}".format(ele)).split())
					for tcl_key in tcl_dict:
						var_name = ele + "(" + tcl_key + ")"
						if int(tcl_interp.eval("info exist {}".format(var_name))) == 1:
							info_dict[ele][tcl_key] = TranslateCmd.reset_value(tcl_interp.getvar(var_name))
				else:
					# Switch some result to str value, cause return "_tkinter.Tcl_Obj"
					info_dict[ele] = TranslateCmd.reset_value(str(tcl_interp.getvar(ele)))
		return info_dict


	@staticmethod
	def modify_input_info(input_info, map_dict={"<<:":":>>"}):
		# Return a listt base on the input_info and map_dict
		map_list = []
		if map_dict:
			for each_key in map_dict.keys():
				map_list.append(each_key + input_info + map_dict[each_key])
		return map_list



	###########################################################################
	## This function works for switch python dict into a tcl file replacement
	## if required, the input is the python_dict
	## and input_tcl, output is output_tcl
	## Example:
	## input_dict = {"abc:""abc_value", "a":"2"}
	## input_tcl: a tcl_file if contains $abc, then it will be replaced
	## output_tcl: will be generated line by line from input_tcl
	## dict_replace_tclfile(input_dict, input_tcl, output_tcl)
	###########################################################################
    @staticmethod
	def dict_replace_tclfile(input_dict, input_tcl, output_tcl, map_dict={"<<:":":>>"}, warning_info=1):
		pattern = r"\$(\S+)\(?\S*\)?"
		pattern_list = TranslateCmd.modify_input_info(pattern, map_dict)
		pattern = "|".join(pattern_list)
		pattern_dict = r"(\S+)\((\S+,)*(\S+)\)"
		transform_info = list()
		with open(input_tcl, "r") as stream:
			for line in stream:
				if not re.match(r"\s*#", line):
					var_info = re.findall(pattern,line)
					if var_info:
						for ele in var_info:
							# Check if this ele in the dict
							# The match_info here is a turple in the list
							# Example: match_info can be"[("keymain", "subkey", "subkey2", "subkey3")]"
							match_info = re.findall(pattern_dict,ele)
							if match_info:
								match_info[0] = [ele for ele in match_info[0] if ele]
								# De replacement for $array_name(var1,var2,var3..)
								replace_flag = TranslateCmd.get_value(match_info[0], input_dict)
								# Update 20231120 for debug strip
								if isinstance(replace_flag, str):
									replace_flag.strip()
								# Add strip() function in 20231108
								# Here var without "$", refill it with "\$"
								#"\(" and "\)" replace "(" and ")" works for re module
								ele_pattern_mid = "|".join(TranslateCmd.modify_input_info("\$" + ele, map_dict))
								ele_pattern_list = ele_pattern_mid.replace("(","\(").replace(")","\)")
								if replace_flag:
									line = re.sub(ele_pattern_list, replace_flag, line)
								elif replace_flag == "":
									line = re.sub(ele_pattern_list, "", line)
								else:
									if warning_info:
										print("EDP_VAR_WARNING: \"{}\" MISSING: {} by {}".format(ele, line, input_tcl))
							else:
								# Do replacement for $varname
								replace_flag = TranslateCmd.get_value(ele, input_dict)
								if isinstance(replace_flag, str):
									replace_flag.strip()
								# Add strip() function 20231108
								# Here is bug for tkinter module
								# The return value is not string type, so a switch is required
								# Maybe bug here, casue the return value can be _tkinter.Tcl_Obj
								# Here var without "$", refill it with "\$"
								#"\(" and "\)" replace "(" and ")" works for re module
								ele_pattern_list = "|".join(TranslateCmd.modify_input_info("\$" + ele, map_dict))
								if replace_flag:
									# Deal with replace_flag if it is a simple list 20231121
									if isinstance(replace_flag, (list, tuple)):
										replace_flag = " ".join(replace_flag)
									line = re.sub(ele_pattern_list, replace_flag, line)
								elif replace_flag == "":
									line = re.sub(ele_pattern_list, "", line)
								else:
									if warning_info:
										print("EDP_VAR_WARNING: \"{}\" MISSING: {} by {}".format(ele, line, input_tcl))

				transform_info.append(line)

		# Base on the transform_info list, write the info into the output tcl
		with open(output_tcl, "w") as stream:
			for ele in transform_info:
				stream.write(ele)
		return

	###########################################################################
	## This function works for base on input info, it will be recognized as
	## input_dict's key and get dict_value, if tuple_switch:
	## then the input_info will be switched as tcl list, input_info can be string
	## or list/tuple
	## Example:
	## input_info = "abc"
	## input_dict = {"abc": "abc_value", "a":"2"}
	## get_value(input_info, input_dict, tuple_switch=1) -> "abc_value"
	###########################################################################
	@staticmethod
	def get_value(input_info, input_dict, tuple_switch=1):
		# The input info can be list, tulpe or string
		# if string:
		if isinstance(input_info,str):
			if input_info in input_dict.keys():
				final_info = input_dict[input_info]
			else:
				return None
			# Do tuple_switch
			if tuple_switch:
				final_info = TranslateCmd.switch_tuple2tcl_list(final_info)
			if isinstance(final_info, list) and len(final_info) == 1:
				final_info = final_info[0]
			return(final_info)
		elif isinstance(input_info, list) or isinstance(input_info, tuple):
			# Maybe a logic bug here?
			for ele in input_info:
				# Delete "," in the list value
				ele = ele.strip(",")
				if ele !="":
					if ele in input_dict.keys():
						input_dict = input_dict[ele]
					else:
						return None

			if tuple_switch:
				final_info = TranslateCmd.switch_tuple2tcl_list(input_dict)
			return final_info
		else:
			return None

	###########################################################################
	## This function works for transform python tuple into tcl list
	## Example:
	## input_info = ("a","b","c")
	## switch_tuple2tcl_list(input_info) -> [list "a" "b" "c"]
	###########################################################################
	@staticmethod
	def switch_tuple2tcl_list(input_info):
		if isinstance(input_info, tuple):
			input_info = " ".join(map(str, input_info))
			input_info = "[list " + input_info + "]"
		return input_info

	@staticmethod
	def rm_brackets(str_in):
		str_in = re.sub(r"\^{", "", str_in)
		str_in = re.sub(r"\}$", "", str_in)
		return str_in

	@staticmethod
	def nested(str_in):
		#Check if str_in is nested
		split_flag = 0
		for ele in str_in:
			if ele == "{":
				split_flag = split_flag + 1
				if split_flag == 2:
					return 1
			elif ele == "}":
				split_flag = split_flag -1
		return 0

	@staticmethod
	def str2list(str_in):
		# Switch tcl based "list" into python "list" if "{  }" has been used in tcl value
		split_flag = 0
		str_ini = ""
		list_ini = list()
		str_count = 0

		if re.match(r"^\{.*\}$", str_in):
			# String only: {xxx} -> xxx
			if " " not in str_in:
				str_in = TranslateCmd.rm_brackets(str_in)
			# {a b} {c d}
			if not TranslateCmd.nested(str_in):
				# {a b}
				if not re.search(r"\{|\}", str_in[1:-1]):
					str_in = TranslateCmd.rm_brackets(str_in)
			# {{a b} c d}
			else:
				str_in = TranslateCmd.rm_brackets(str_in)

		if " " in str_in:
			for ele in str_in:
				str_count = str_count + 1
				if ele == "{":
					split_flag = split_flag + 1
				elif ele == "}":
					split_flag = split_flag - 1

				if ele.isspace() and split_flag == 0:
					if str_ini:
						list_ini.append(str_ini)
					str_ini = ""
				else:
					# if touch end
					str_ini = str_ini + ele
					if str_count == len(str_in):
						list_ini.append(str_ini)
						str_ini = ""
			return list_ini
		else:
			return str_in


    @staticmethod
	def reset_value(input_str):
		# Debug 20231120, filter the empty value if exist
		ini_list = TranslateCmd.str2list(input_str)
		if isinstance(ini_list, list):
			if len(ini_list) == 1:
				ini_list = ini_list[0]
				return ini_list
			for i, ele in enumerate(ini_list):
				ini_list[i] = TranslateCmd.reset_value(ele)
		return ini_list


if __name__ == "__main__":
	# input_file = "/home/chenanping/edp/case_try/nbio_pcie_t/run_01/main/cmds/pnr_innovus/init.cmd"
	input_file = "/home/chenanping/others/test/cmd_flatten/t1.tcl"
	# TranslateCmd(input_file).main_func(debug=True)
	TranslateCmd(input_file).main_func(debug=True)
	# generate translated output

