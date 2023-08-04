#! /usr/bin/python3.9
############################################################
# File Name: build_tech.py
# Author: anping.chen
# Email: anping.chen@joinsilicon.com
# Created Time: Thu 11 May 2023 03:51:56 PM CST
############################################################
# import util python_env.py

main_dir = os.path.abspath(os.getcwd() + "/../../")
libs_dir = os.path.join(main_dir, "libs")
libs_dir_config_source = os.path.join(libs_dir, "config")
libs_dir_config_target = os.path.join(libs_dir, "lists")

full_yaml = main_dir + "/config/full.yaml"
merged_var = DependencyIni().merged_var(full_yaml)
# Deal with libs
GetSortedLib.link_libs(merged_var['libs_info'], main_dir)
# Gen all lists base on libs/config/
if "libs_key_info" in merged_var.keys():
	keyword_list = merged_var['libs_key_info']
else:
	keyword_list = ["lef", "ndm", "verilog", "db"]
for key_word in keyword_list:
	# Get *.list
	key_word = key_word + ".list"
	GetSortedLib.gen_merged_lists(libs_dir_config_source, libs_dir_config_target, key_word)

