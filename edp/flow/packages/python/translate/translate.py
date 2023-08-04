import re, os, subprocess


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
		# Read in information
		with open(self.input_file) as stream:
			stream_info = stream.readlines()
		# Write out information
		with open(self.input_file, "w") as stream:
			for line in stream_info:
				if re.search(pattern, line):
					line = self.info_replace(util_dir_list, line, pattern)
				stream.write(line)

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


if __name__ == "__main__":
	# input_file = "/home/chenanping/edp/case_try/nbio_pcie_t/run_01/main/cmds/pnr_innovus/init.cmd"
	input_file = "/home/chenanping/others/test/cmd_flatten/t1.tcl"
	# TranslateCmd(input_file).main_func(debug=True)
	TranslateCmd(input_file).main_func(debug=True)
	# generate translated output

