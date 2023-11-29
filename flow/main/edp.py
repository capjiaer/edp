#! /usr/bin/python3.9
############################################################
# File Name: edp.py
# Author: anping.chen
# Email: anping.chen@joinsilicon.com
# Created Time: Mon 13 Feb 2023 03:51:15 PM CST
############################################################
import shutil
# This file is the main file for JEDP -> Joinsilicon Engineering Development Platform
import sys, argparse, os, json, time, datetime, yaml, pathlib
from pathlib import Path
from shutil import copyfile, copytree, rmtree
from yaml.loader import SafeLoader, FullLoader
file_dir = os.path.dirname(os.path.realpath(__file__))
flow_dir = os.path.dirname(file_dir)
package_dir = flow_dir + "/packages/python"
sys.path.append(package_dir)
from flow_info.flow_func import *
from dependency.main import GetUserInfo, DependencyIni
from translate.translate import *


# ########################################################### 1.1 Check platform basic setup
# Main path check for the JEDP initialization
args, help_info = Flow.gen_args()
user_cfg_yaml = (os.path.abspath(args.config))

# user_cfg_yaml = os.path.join(os.getcwd(), "user_config.yaml")
config_dir = os.path.join(os.getcwd(), "config")
cmds_dir = os.path.join(os.getcwd(), "cmds")
# Initialize the merged_var
branch_info = os.getcwd().split("/")[-1]
yaml_list = DependencyIni.get_yaml_list(user_cfg_yaml, branch_info, mode='flow')
merged_var = DependencyIni().merged_var(*yaml_list, info=False)
# Add tcl_var to support a std alone tcl flow, the tcl file deliverd by key setup_tcl
merged_var = Flow.update_tclvar(merged_var,merged_var['setup_tcl'])
with open(yaml_list[-1], 'r') as stream:
	user_dict = yaml.safe_load(stream)
merged_var = DependencyIni.merge_dicts(merged_var, user_dict)
# Options is required

# Step1: Argparse setup
if len(sys.argv[1:]) == 0:
    print(help_info)
    exit()

# Func1: Get dependency info
if args.info:
    dependency_list = DependencyIni.get_yaml_list(user_cfg_yaml, branch_info, mode='dependency')
    tool_target = []
    for ele in dependency_list:
        tool_target.append(os.path.dirname(ele).split('/')[-1])
    print("supported flow:", " ".join(tool_target))
    for dependency in dependency_list:
        flow_name = os.path.dirname(dependency).split('/')[-1]
        print("FLOW NAME:", flow_name)
        info_dict = Flow().get_series(dependency)
        for key, value in info_dict.items():
            print("%s" % key, str(value).replace('\'', "").replace('[]', "None"))
        print("")
    exit()

# Func2: Set update params
if args.update:
    Flow.update_params(branch_info)
    print("Update params")
    print(config_dir + "/full.tcl updated")
    print(config_dir + "/full.yaml updated")
    exit()

# Func3: Generate/update cmds
if args.gen_cmds:
    # Update yaml file and tcl files
    Flow.update_params(args.branch)
    # Update makefile, search keywords for dict_in[flow][dependency_info_dict] for dependencies
    # such as dict_in["pnr_innovus"]["dependency"]
    FlowIni.create_makefile(merged_var, mode="flow", dependency_info_dict="dependency")
    for dependency_ele in merged_var['sequence']:
        # Dependency information comes from below:
        dependency_yaml = Path(os.getcwd())/"flow/initialize/config"/dependency_ele/"dependency.yaml"
        root_cmd_dir = Path(os.getcwd())/"flow/initialize/cmds"/dependency_ele
        # Tune files information comes from below, copy all tune files to the tune directory
        # Code improve 202231114, use updated function copytree here
        tune_files_source = str(root_cmd_dir) + "/proc"
        tune_files_target = os.getcwd() + "/tune/" + dependency_ele
        # Here set link_mode, which means if users want to modify tunfile, rm old symlink is required, which incase un-expected modify
        FlowIni.copytree(tune_files_source, tune_files_target, link_mode=1)

        translate = (lambda x: 1 if x else 0)(args.debug)
        cmds_list = Flow.get_cmds(dependency_yaml, root_cmd_dir, cmds_dir, dependency_ele, merged_var, translate=translate)
        main_util = os.getcwd() + "/flow/initialize/templates/main_util/"
        for cmd in cmds_list:
            # All in all, the replacement contains 2 steps
            # 2: Replacement base on tcl input in dict(['setup_tcl'])

            # Step1: Do util replacement first
            cmd_split_list = os.path.dirname(cmd).split("/")
            index = cmd_split_list.index("cmds")
            cmd_util = os.getcwd() + "/flow/initialize/cmds/" + cmd_split_list[index+1] + "/util/"
            # Util file will comes from:
            # 1: <workdir>/flow/initialize/templates/main_util
            # 2: <workdir>/flow/initialize/cmds/dependency_ele/util
            util_dir_list = [main_util, cmd_util]
            TranslateCmd(cmd).util_apply(util_dir_list)
            # Do replacement for var replacement
            TranslateCmd.dict_replace_tclfile(merged_var,cmd,cmd)
        print("")

# Func4: Create branch
if args.branch:
    branch_ini = os.path.dirname(os.getcwd())
    if args.branch not in os.listdir(branch_ini):
        print("your branch name is", args.branch)
    else:
        print("[EDP_ERROR]: your branch name is already exist, please create a new branch!")
        exit()
    # Check yaml file is correctly
    if args.branch_yaml and file_exists(args.branch_yaml):
        user_config_yaml = os.path.abspath(args.branch_yaml)
    else:
        print("[EDP_WARNING]: Did not find branch_yaml file, set default yaml file as branch_yaml")
        print("[EDP_INFO]: Your branch yaml is %s" % os.path.abspath(args.config))
        print("[EDP_INFO]: You may try: edp -b <branch_name> -by <branch_yaml> -fv <flow_version>")
        user_cfg_yaml = os.path.abspath(args.config)
    DependencyIni(user_cfg_yaml).check_user_config()
    # Yml file is correct, then get user_config
    user_config = DependencyIni(input_config_file=user_cfg_yaml).return_dict()
    # Initialize branch flow
    branch = branch_ini + "/" + args.branch
    os.makedirs(branch, exist_ok=True)

    source_flow = os.path.dirname(flow_dir)
    # Update 20231115, git get packages dir
    FlowIni.dir_gen(source_flow, user_config, branch=args.branch, refresh=True, required_dirs=["flow/packages/tcl"])
    # Copy args.config to new branch and default set yaml as user_config.yaml
    os.system('cp ' + user_cfg_yaml + " " + branch_ini + "/" + args.branch + "/user_config.yaml")
    # Initial libs
    yaml_list = DependencyIni.get_yaml_list(user_cfg_yaml, branch_info, mode='flow')
    merged_var = DependencyIni().merged_var(*yaml_list)
    # GetSortedLib.link_libs(merged_var['libs_info'], branch)
    # All files in required_link_dir is required
    required_link_dir = ['data', 'hooks', 'pass', 'rpts', 'runs']
    Flow.create_branch(required_link_dir, args.branch)
    print('Branch setup done')

# Func5: Create branch
if args.debug:
    if args.gen_cmds:
        print("The command gen is working on the debug mode")
        print("the generated cmds has been translated if possible")
    else:
        print("\"edp -d\" is not supported along without edp -g")
        print("EDP_ERROR: please try \"edp -g -d\"")
        exit()

# Func6: Flow refresh
if args.refresh:
    FlowIni.refresh_flow(merged_var, os.path.dirname(flow_dir), branch_info)
