#! /usr/bin/python3.9
############################################################
# File Name: edp_ini.py
# Author: anping.chen
# Email: capjiaer@163.com
# Created Time: Tue 14 Feb 2023 04:20:46 PM CST
############################################################

import argparse
import os, yaml, time, git, sys
file_dir = os.path.dirname(os.path.realpath(__file__))
flow_dir = os.path.dirname(file_dir)
package_dir = flow_dir + "/packages/python"
sys.path.append(package_dir)
from shutil import copyfile, copytree, rmtree
from dependency.main import GetUserInfo, DependencyIni
from lib_ini.gen_libs import GetSortedLib, config_sort
from flow_info.main import FlowIni
from pathlib import Path

# This file is working for the flow initialization, the user_cfg is required

# Step0: Initialize check incase any unexpected error occurs
# GetUserInfo.initialize_check()
# Step0 Done ########################################################################

# Step1: Argparse setup required
args = FlowIni.gen_args()
# Step1 Done ########################################################################

# Step2: Basic directory setup
# 2.1 Check yaml file is correctly
user_cfg_yaml = os.path.abspath(args.config)
DependencyIni(user_cfg_yaml).check_user_config()
# Yml file is correct, then get user_config
user_config = DependencyIni(input_config_file=user_cfg_yaml).return_dict()
branch = os.getcwd() + "/" + user_config["block_name"] + "/" + user_config["nick_name"] + "/" + args.branch
# 2.2 Git download required information
if "git_url" in user_config.keys() and user_config["git_url"] is not None:
	repo_url = user_config["git_url"]
else:
	repo_url = "git@github.com:capjiaer/edp.git"
if "git_branch" in user_config.keys() and user_config["git_branch"] is not None:
	git_branch = user_config["git_branch"]
else:
	git_branch = "main"
source_flow = os.path.dirname(flow_dir)
# Update 20231110
FlowIni.dir_gen(source_flow, user_config, git_url=repo_url, git_branch=git_branch, keep_git=0, required_dirs=["flow/packages/tcl/"])
# Git clone here is required
# Step2 Done ########################################################################

# Step3: Yaml file reset, create tcl version var files
# 3.1 Copy user_config.yaml to workdir
os.system('cp ' + os.getcwd() + "/user_config.yaml" + " " + branch + "/")
# 3.2 Get final yaml && tcl configuration
# All information restored in merged_var
# pre_yaml_list = DependencyIni.get_yaml_list(user_cfg_yaml, pre=True)
yaml_list = DependencyIni.get_yaml_list(user_cfg_yaml, args.branch)
merged_var = DependencyIni().merged_var(*yaml_list)
# Step3 Done ########################################################################
print('EDP initialization finished...')
