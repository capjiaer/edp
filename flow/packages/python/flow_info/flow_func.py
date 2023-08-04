#! /usr/bin/python3.9
############################################################
# File Name: flow_func.py
# Author: anping.chen
# Email: anping.chen@joinsilicon.com
# Created Time: Wed 15 Mar 2023 02:54:29 PM CST
############################################################
import argparse
import os, yaml, time, git, sys, re, pathlib
import shutil
file_dir = os.path.dirname(os.path.realpath(__file__))
package_dir = os.path.dirname(file_dir)
sys.path.append(package_dir)
from dependency.main import GetUserInfo, DependencyIni
from lib_ini.gen_libs import GetSortedLib, config_sort
from flow_info.main import FlowIni
from flow_info.flow_func import *


class Flow:
    def __init__(self, input_config_file="", input_info=None):
        super(Flow, self).__init__()

    @staticmethod
    def update_params(branch, mode="flow", yaml_file="full.yaml", tcl_file="full.tcl"):
        main_path = os.getcwd()
        user_cfg_yaml = main_path + "/user_config.yaml"
        yaml_list = DependencyIni.get_yaml_list(user_cfg_yaml, branch=branch, mode=mode)
        merged_var = DependencyIni.merged_var(*yaml_list, info=False)
        target_yaml = os.getcwd() + "/config/" + yaml_file
        DependencyIni.dict2out(merged_var, target_yaml)
        config_sort(os.getcwd() + "/config/", yaml_list, merged_tcl_name=tcl_file, info=False)

    @staticmethod
    def gen_args():
        opts = argparse.ArgumentParser(add_help=True)
        opts.add_argument("-u", "--update", help="update the final config file if user_config.yaml updated", action="store_true")
        opts.add_argument("-r", "--refresh", help="update initial flow if required", action="store_true")
        opts.add_argument("-i", "--info", help="show run target information for each sub flow", action="store_true")
        opts.add_argument("-d", "--debug", help="debug mode, the generated cmd will be translated into a flatten one", action="store_true")
        opts.add_argument("-de", "--debug_enhance", help="debug mode enhance, the generated cmd will be translated into a flatten one, and debug info remained", action="store_true")
        opts.add_argument("-g", "--gen_cmds", help="Gen cmds, the cmds will be generated base on template and input variable yaml", action="store_true")
        opts.add_argument("-b", "--branch", required=False, type=str, help="the branch information is required")
        opts.add_argument("-c", "--config", required=False, type=str, default="user_config.yaml", help="the config information is required")
        opts.add_argument("-by", "--branch_yaml", required=False, type=str, help="the BRANCH CONFIG YAML information is required")
        args = opts.parse_args()
        return args, opts.format_help()

    def get_inout(self, input_info: 'dict|list', dict_in):
        if isinstance(input_info, dict):
            for key, value in input_info.items():
                if "cmd" in value.keys():
                    if key not in dict_in.keys():
                        dict_in[key] = dict()
                    for ele in ["in", "out"]:
                        if ele in value:
                            dict_in[key][ele] = value[ele]
                        else:
                            dict_in[key][ele] = None
                else:
                    self.get_inout(input_info[key], dict_in)
        if isinstance(input_info, list):
            for ele in input_info:
                self.get_inout(ele, dict_in)

    def get_series(self, dependency_yaml, target=None):
        input_dict = DependencyIni(dependency_yaml).return_dict()
        dict_in = dict()
        # Deal with in/out information
        self.get_inout(input_dict, dict_in)
        for key_in in dict_in.keys():
            post_list = list()
            pre_list = list()
            # Initial in/out if not exist
            for key_out in dict_in.keys():
                # in/out can be not only one element, if so, either one element has overlap, the relationship exists
                if dict_in[key_in]['in'] and dict_in[key_out]['out'] and set(dict_in[key_in]['in'].split()) & set(dict_in[key_out]['out'].split()):
                    pre_list.append(key_out)
                if dict_in[key_in]['out'] and dict_in[key_out]['in'] and set(dict_in[key_in]['out'].split()) & set(dict_in[key_out]['in'].split()):
                    post_list.append(key_out)

            dict_in[key_in]['pre'] = pre_list
            dict_in[key_in]['post'] = post_list
        # Added in 2023/03/20 for more details information
        if target is not None:
            if target in list(dict_in.keys()):
                print('The select target is:    %s' % target)
                if len(dict_in[target]["pre"]) != 0:
                    print('The pre_target is:       %s' % " ".join(dict_in[target]["pre"]))
                if len(dict_in[target]["post"]) != 0:
                    print('The post_target is:      %s' % " ".join(dict_in[target]["post"]))
                if "in" in list(dict_in[target].keys()):
                    print("Required input is:       %s" % dict_in[target]["in"])
                if "out" in list(dict_in[target].keys()):
                    print("The generated part will be: %s" % dict_in[target]["out"])
            else:
                print("Target not found, please check your configuration")
                print("Please refer to below targets: ", " ".join(list(dict_in.keys())))
            return None
        return dict_in

    @staticmethod
    def fresh_cmds(pre_cmd, target_dir, merged_dict=None, mode='default', sub_mode="flow", user_cfg_yaml=None, translate=1):
        """
        :param merged_dict: Dictionary input, if merged_dict not None, user_cfg_yaml is ignored
        :param mode:    "default" is set user_cfg_yaml as input, then get all yaml files base on input
                        "single" is just take user_cfg_yaml as input
        :param sub_mode: "edp/dependency/edp_ini" can be selected
        :param user_cfg_yaml:   the yaml file comes from user
        :param pre_cmd:         the pre_cmd required, then gen post_cmds
        :param target_dir:      the post_cmds will generate in target_dir
        :param translate:       decide whether to translate the command line
        :return:
        """
        if merged_dict is None:
            # Get merged_var
            if mode == 'default':
                yaml_list = DependencyIni.get_yaml_list(user_cfg_yaml, mode=sub_mode)
            elif mode == 'single':
                yaml_list = [user_cfg_yaml]
            else:
                print("Only \"default\" or \"single\" mode is supported, please select one of it.")
                exit()
            merged_var = DependencyIni.merged_var(*yaml_list, info=False)
        else:
            merged_var = merged_dict
        target_tcl = os.path.join(target_dir, "var.tcl")
        DependencyIni.dict2out(merged_var, target_tcl, out_type='tcl')
        # Get all var info
        # Get variable names
        var_list = list()
        var_dict = dict()
        with open(target_tcl, 'r') as stream:
            for line in stream.readlines():
                if re.match(r'^\s*set', line):
                    var_name = line.rstrip().split(" ", 2)
                    var_list.append(var_name[1])
                    var_dict[var_name[1]] = var_name[2:]
        var_list = list(set(var_list))

        # Get cmd info
        target_cmd = os.path.join(target_dir, os.path.basename(pre_cmd))
        # pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)
        target_info = open(target_cmd, 'w')
        with open(pre_cmd, 'r') as stream:
            # Deal with ""
            re_str = "(.*[^\s=\(\[\{\"])\"([^\s=\)\]\}\"].*)"
            re_str_en1 = "(.*/)\"\"(.*)"
            re_str_en2 = "(.*)\"\"(/.*)"
            re_str_en3 = "(.*\")\"([^\s\]\}!\|\&><=].*)"
            re_str_en4 = "(.*[^\s\[\{!\|\&><=])\"(\".*)"
            re_list = [re_str, re_str_en1, re_str_en2, re_str_en3, re_str_en4]
            # Replace 3 times to deal with all related "" problem
            # re_str: deal with "xx"/"xx" or {("xx")} problems
            # re_str_en1: deal with /"" problems
            # re_str_en2: deal with ""/ problems
            # re_str_en3/re_str_en4: deal with ""xx or xx"" problems
            for line in stream.readlines():
                for ele in var_list:
                    # incase ele re-set here, remove the ele in the list, and
                    regex1 = re.compile("^set\s+%s" % ele)
                    regex2 = re.compile(".*;(\s+)*set\s+%s" % ele)
                    if regex1.match(line) or regex2.match(line):
                        print("get reset for var", ele, ":", line.rstrip('\n'))
                        print("Ignore", ele, "in the further substitution")
                        var_list.remove(ele)
                    # Detect "$" + ele or "${" + ele + "}" exist or not
                    for pre_ele in ["$" + ele, "${" + ele + "}"]:
                        if pre_ele in line:
                            value = var_dict[ele][0].strip('"')
                            # ignore "" when int/float/list exists
                            if re.match('^\d+(\.)*(\d+)*', value) or re.match('^\[.*\]', value):
                                line = line.replace(pre_ele, var_dict[ele][0].strip('"'))
                            else:
                                # The value is a string, not an int/float/list
                                line = line.replace(pre_ele, var_dict[ele][0])
                                # Detail with rest "" problems
                                for ele_str in re_list:
                                    result = re.match(ele_str, line)
                                    while result:
                                        line = re.sub(ele_str, r'\1\2', line)
                                        result = re.match(ele_str, line)
                target_info.write(line)
        target_info.close()
        os.system('chmod +x %s' % target_cmd)
        os.remove(target_tcl)
        return

    @staticmethod
    def get_cmds(dependency_yaml, pre_cmd_dir, post_cmd_dir, target, merged_var, translate=1):
        cmds_list = []
        if not os.path.exists(dependency_yaml):
            print("Missing dependency file:", dependency_yaml)
        else:
            print("Found Dependency yaml:", dependency_yaml, target)
            required_info = list(set(DependencyIni().get_cmds_info(dependency_yaml, target)))
            for cmd_info in required_info:
                cmd_file = str(pre_cmd_dir) + "/scripts/" + cmd_info
                if os.path.exists(cmd_file):
                    gen_file_dir = os.path.dirname(post_cmd_dir + "/" + target + cmd_file.split(target)[-1].split("/")[-1]) + "/" + target
                    pathlib.Path(gen_file_dir).mkdir(parents=True, exist_ok=True)
                    if translate:
                        # Do translation
                        Flow.fresh_cmds(cmd_file, gen_file_dir, merged_dict=merged_var)
                    else:
                        # Just copy
                        shutil.copyfile(cmd_file, gen_file_dir + "/" + cmd_info)
                    print("[EDP_INFO] Gen command:", gen_file_dir + "/" + os.path.basename(cmd_file))
                    cmds_list.append(gen_file_dir + "/" + os.path.basename(cmd_file))

                else:
                    print("[EDP_WARNING] Missing required command:", cmd_file)
        return cmds_list


if __name__ == '__main__':
    config_yaml = "/home/chenanping/edp/case_try/dc_try/test/t1.yaml"
    cmd = "/home/chenanping/edp/case_try/dc_try/test/t1.tcl"
    my_dir = "/home/chenanping/edp/case_try/dc_try/test/post_cmd"

    # config_yaml = "/home/chenanping/edp/case_try/dc_try/dc_cfg.yaml"
    # cmd = "/home/chenanping/edp/case_try/dc_try/dc.tcl"
    # my_dir = "/home/chenanping/edp/case_try/dc_try/post_cmd"
    Flow().gen_cmds(config_yaml, cmd, my_dir, mode='single')
