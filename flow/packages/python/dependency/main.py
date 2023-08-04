#! /usr/bin/python3.9
############################################################
# File Name: get_user_info.py
# Author: anping.chen
# Email: capjiaer@163.com
# Created Time: Tue 07 Feb 2023 10:46:35 AM CST
############################################################
import json

import yaml, os, re, sys, time
from yaml.loader import FullLoader
from pathlib import Path


# The input_data shall be a dictionary|list, the makefile shall be a str, the return value is None
class GetUserInfo:
    def __init__(self):
        super().__init__()

    def get_selection(self, dict_info, keyword='project'):
        print("")
        for proj_name, foundry in dict_info.items():
            print("select " + keyword + " : " + proj_name)

        # Waiting for user input as the selection info
        user_info_project = input('select info: ')
        if user_info_project not in dict_info.keys():
            print("project not found, please reselect")
            # Recursion here unless user's selection is correct
            self.get_selection(dict_info, keyword="project")

        # Return info for the user's selection
        foundry = list(dict_info[user_info_project].keys())[0]
        node = list(dict_info[user_info_project].values())[0]
        return user_info_project, foundry, node

    @staticmethod
    def initialize_check():
        print("U are working on The Engineering Development Platform")
        print("Please check your working directory")
        print("Are U sure that you want to do the initialization?")
        print("Y/N?")
        input_info = input()
        if input_info.upper() == "Y":
            print("Initialization start")
        else:
            print("Initialization canceled")
            exit()
        time.sleep(1)


# All the packages and functions works for flow ini will be settled in the DependencyIni class
class DependencyIni:
    # merged_var:               working for return a dictionary contains all the information
    # return_dict:              working for return a dictionary contains user_cfg information only
    # check_user_config:        working for check the user_cfg information
    # yaml2tcl/json2tcl:        working for convert yaml to tcl and json to tcl
    # stream2tcl_io:            working for convert dict to tcl
    # get_cfg_info/show_cfg_info:           working for show the user_cfg information
    # get_target_info:                      working for get the target information
    # create_dependency/gen_dependency:     working for create makefile dependency
    def __init__(self, input_config_file="", input_info=None):
        super(DependencyIni, self).__init__()
        self.mode_list = None
        self.config_file = input_config_file
        self.pre_key = ""
        self.cmd_list = []
        if input_config_file != "" and os.path.exists(input_config_file):
            with open(input_config_file, 'r') as stream:
                if os.path.splitext(input_config_file)[1] == ".yaml":
                    self.data_ini = yaml.load(stream, Loader=FullLoader)
                elif os.path.splitext(input_config_file)[1] == ".json":
                    self.data_ini = json.load(stream)
                else:
                    print("The file format is not supported, only yaml and json are supported")
                    exit()
        if input_info is not None:
            if isinstance(input_info, dict):
                self.data_ini = input_info
            else:
                print("The input_info argument must be a dict, please recheck the input information")
                exit()

    @staticmethod
    def get_yaml_list(user_yaml, branch, pre=False, mode='flow_ini'):
        """
        :param branch: a branch name is required
        :param user_yaml: a yaml file working for flow ini, all required yaml will be set in the list
        :param pre: whether return the pre yaml list
            if False, return all yaml files
            if True, return only flow/project/user yaml files
        :param mode:
            flow_ini    > works for flow_ini, flow initialization
            flow         > works for workflow usage
            dependency  > works for return dependency yaml files
        :return: a yaml file list
        """
        user_config = DependencyIni(input_config_file=user_yaml).return_dict()
        if mode == "flow_ini":
            check_dir = os.path.dirname(user_yaml)
            dir_branch = check_dir + "/" + user_config["block_name"] + "/" + user_config["nick_name"] + "/" + branch
            config_info = dir_branch + "/flow/initialize/config/project"
        elif mode == "flow" or mode == "dependency":
            dir_branch = os.path.dirname(user_yaml)
            config_info = dir_branch + "/flow/initialize/config/project"
        else:
            print("mode not supported, please check your configuration")
            exit()

        flow_yaml = config_info + "/main/flow_ini.yaml"
        project_yaml = config_info + "/main/main.yaml"
        pre_var_list = [flow_yaml, project_yaml, user_yaml]
        # pre_var_list = [flow_yaml, project_yaml, main_branch + "/user_config.yaml"]
        pre_var = DependencyIni().merged_var(*pre_var_list, info=False)
        config_yaml_list = list()
        dependency_list = list()
        for func_list in pre_var['sequence']:
            func_cfg_yaml = Path(dir_branch)/"flow/initialize/config/project"/func_list/"config.yaml"
            dependency_yaml = Path(dir_branch)/"flow/initialize/config/project"/func_list/"dependency.yaml"
            if os.path.exists(func_cfg_yaml):
                config_yaml_list.append(str(func_cfg_yaml))
                dependency_list.append(str(dependency_yaml))
        final_yaml_list = config_yaml_list + pre_var_list
        if mode != "dependency":
            if pre:
                return pre_var_list
            else:
                return final_yaml_list
        else:
            return dependency_list

    @staticmethod
    def merge_dicts(dict1, dict2):
        """
        递归合并两个字典，其中字典中的子字典也会被递归合并。
        如果两个字典中有相同的键，后面的字典的键值对会覆盖前面的字典的键值对。
        """
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DependencyIni.merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def merged_var(*args: str, cfg_path="", info=True):
        final_var = {}
        for ele in args:
            if info:
                print("File loading: ", ele)
            with open(ele, 'r') as var_info:
                if os.path.splitext(ele)[1] == ".yaml":
                    var_dict = yaml.load(var_info, Loader=FullLoader)
                elif os.path.splitext(ele)[1] == ".json":
                    var_dict = json.load(var_info)
                else:
                    print("The file format is not supported, only yaml and json are supported")
                    exit()
                if var_dict is not None:
                    final_var = DependencyIni.merge_dicts(final_var, var_dict)

        if cfg_path != "":
            with open(cfg_path, "w") as saved_info:
                if os.path.splitext(cfg_path)[1] == ".yaml":
                    saved_info.write(yaml.dump(final_var, allow_unicode=True, sort_keys=False))
                    print("Yaml file generated: ", cfg_path)
                elif os.path.splitext(cfg_path)[1] == ".json":
                    saved_info.write(json.dumps(final_var, sort_keys=False))
                    print("Json file generated: ", cfg_path)
                else:
                    print("The output format is not supported, only yaml and json are supported")
                    exit()
        return final_var

    def return_dict(self):
        """
        :return: the cfg file dictionary, this function is required for flow initialisation
        """
        return self.data_ini

    def check_user_config(self):
        # Make sure have a copy in the ini directory
        if os.path.isfile(self.config_file) is False:
            print("user_config.yaml is not exist, please check your run directory, a \"user_config.yaml\" is required")
            exit()
        # Check if required info exist
        ini_dict_key = self.data_ini.keys()
        for ele in ["project_name", "block_name", "nick_name"]:
            if ele not in ini_dict_key:
                print("[INI_ERROR] Please check your user_cfg, key %s is required" % ele)
                exit()

    def yaml2tcl(self, yaml_in, tcl_out, mode='a+'):
        """
        :param mode: a+ or w
        :param yaml_in: the input yaml file
        :param tcl_out: the output tcl file
        :return: None
        """
        # print("[YAML_TRANS] file transformation finished ->", yaml_in)
        with open(yaml_in, 'r') as stream:
            data_ini = yaml.load(stream, Loader=FullLoader)
            key_list = data_ini.keys()

        with open(tcl_out, mode) as stream:
            stream.write("# " + str(yaml_in) + "\n\n")
            self.stream2tcl_io(data_ini, stream, key_list)
            stream.write("\n")
            stream.close()

    def json2tcl(self, json_in, tcl_out, mode='a+'):
        """
        :param mode: a+ or w
        :param json_in: the input json file
        :param tcl_out: the output tcl file
        :return: None
        """
        print("file transformation finished ->", json_in)
        with open(json_in, 'r') as stream:
            data_ini = json.load(stream)
            key_list = data_ini.keys()

        with open(tcl_out, mode) as stream:
            stream.write("# " + str(json_in) + "\n\n")
            self.stream2tcl_io(data_ini, stream, key_list)
            stream.write("\n")
            stream.close()
        print("Generated tcl file ->", tcl_out)

    @staticmethod
    def dict2out(dict_in, file_out, out_type='yaml'):
        """
        :param dict_in: the input dict info
        :param file_out: the output file directory
        :param out_type: 'yaml' or 'json' is supported, 'tcl' also supported, yaml is the default
        :return: None
        """
        if out_type == 'yaml':
            with open(file_out, 'w') as stream:
                stream.write(yaml.dump(dict_in, allow_unicode=True, sort_keys=False))
        elif out_type == 'json':
            with open(file_out, 'w') as stream:
                stream.write(json.dumps(dict_in, indent=4, sort_keys=False))
        elif out_type == 'tcl':
            temp_yaml = os.path.dirname(file_out) + "/temp.yaml"
            DependencyIni.dict2out(dict_in, temp_yaml, out_type='yaml')
            DependencyIni().yaml2tcl(temp_yaml, file_out)
            os.remove(temp_yaml)
        else:
            print("The output format is not supported, only yaml and json are supported")
            exit()

    def stream2tcl_io(self, data_ini, output_file, key_list, pre_mark=""):
        """
        :param key_list:        a list of keys for further usage
        :param data_ini:        a dict thus can be transformed
        :param output_file:     a tcl file path
        :param pre_mark:        default empty and not really required, just for recursion
        :return: None
        examples:
            abc:
                a1: b
            -> 
            set abc(a1) b
        """
        if data_ini is not None:
            for ele_key, ele_value in data_ini.items():
                if isinstance(ele_value, (str, int, float, list)):
                    if isinstance(ele_value, (str, int, float)):
                        if self.pre_key == "":
                            # if without pre parry declarations
                            output_file.write("set " + ele_key + " \"" + str(ele_value) + "\"\n")
                        else:
                            # if with pre parry declarations
                            # Delete the first "," here then split the rest string into head and tail
                            # ,pv_calibre,fpperc,topo -> pv_calibre,fpperc,topo -> pv_calibre fpperc,topo
                            sp1, sp2 = self.pre_key.split(",", 1)
                            if re.match(".*,", sp2):
                                head, tail = sp2.split(",", 1)
                                output_file.write(
                                    "set " + head + "(" + tail + ',' + ele_key + ") \"" + str(ele_value) + "\"\n")
                            else:
                                head, tail = sp2, ""
                                output_file.write("set " + head + "(" + ele_key + ") \"" + str(ele_value) + "\"\n")

                    if isinstance(ele_value, list):
                        if self.pre_key == "":
                            # if without pre parry declarations
                            # ele_value = str(ele_value).replace(",", "").replace("{", "[").replace("}", "]").replace(":", "")
                            ele_value = str(ele_value).replace("[", "[list ").replace(",", "")
                            output_file.write("set " + ele_key + " " + str(ele_value) + "\n")
                        else:
                            # if with pre parry declarations
                            sp1, sp2 = self.pre_key.split(",", 1)
                            if re.match(".*,", sp2):
                                head, tail = sp2.split(",", 1)
                                ele_value = str(ele_value).replace("[", "[list ").replace(",", "")
                                output_file.write(
                                    "set " + head + "(" + tail + ',' + ele_key + ") " + str(ele_value) + "\n")
                            else:
                                ele_value = str(ele_value).replace("[", "[list ").replace(",", "")
                                output_file.write("set " + sp2 + "(" + ele_key + ") " + str(ele_value) + "\n")
                            # ele_value = str(ele_value).replace(",", "").replace("{", "[").replace("}", "]").replace(":", "")

                if isinstance(ele_value, dict):
                    self.pre_key = pre_mark + "," + ele_key
                    self.stream2tcl_io(ele_value, output_file, key_list, self.pre_key)
                    # Delete prefix from old key value pairs, if key is in the list ...
                    if ele_key in key_list:
                        self.pre_key = ""

    def get_cfg_info(self):
        """
        Return data_ini info
        """
        return self.data_ini

    def show_cfg_info(self, target: str, mode: str):
        """
        :param target:
        :param mode:
        :return:
        """
        self.mode_list = self.data_ini[target][mode]
        for ele in self.mode_list:
            for ele_key, ele_value in ele.items():
                print(ele_key, "    -> ", ele_value)

    @staticmethod
    def get_target_info(target):
        """
        Get all sub-target info
        :param:
        :return:
        """
        makefile = os.getcwd() + "/Makefile"
        if os.path.isfile(makefile) is False:
            print("Makefile not found, please recheck your Makefile")
            sys.exit(1)
        num = 0
        data_restore = []
        # Get line numbers
        with open(makefile, 'r') as stream:
            file_line_num = len(stream.readlines())

        # Get sub target info
        with open(makefile, 'r') as stream:
            for line in stream.readlines():
                num = num + 1
                start_point = re.match('^#.*' + target + '.*\.yaml', line)
                # start_point = re.match('^(\s)(.*)#.*' + target + '.*\.yaml', line)
                if start_point is not None:
                    start_num = num

                if 'start_num' in vars() and num > start_num:
                    end_point = re.match('^\s*#.*yaml', line)
                    required_info = re.match('^\w*_\w*:', line)
                    if required_info is not None:
                        # Get run_target_info
                        data_restore.append(line.replace(":", "").split()[0])
                    if end_point or num + 1 == file_line_num:
                        return data_restore

    def create_dependency(self, input_file, target, lib_info_path, merged_var, mode=""):
        """
        :param input_file: the makefile path
        :param target: for target declarations, pv_calibre/pnr_innovus/syn_dc etc...
        :param lib_info_path: dependency_yaml directory
        :param merged_var: the merged variable info, all info in the dict
        :param mode:
        :return:
        """
        runs_dir = os.path.dirname(os.path.abspath(input_file)) + "/runs"
        makefile = open(input_file, 'a')
        makefile.write("# " + lib_info_path + "/dependency.yaml\n")
        if self.data_ini is not None:
            if mode != "":
                # Set mode here incase dict information conflicts with dependency.yaml, in base flow, set keyword as "dependency"
                self.mode_list = self.data_ini[target][mode]
            else:
                self.mode_list = self.data_ini[target]
            self.gen_dependency(self.mode_list, makefile, os.path.dirname(input_file) + "/cmds", target, merged_var, runs_dir)
        makefile.close()

    def get_cmds_info(self, dependency_yaml, target):
        out_list = []
        if dependency_yaml != "" and dependency_yaml:
            with open(dependency_yaml, 'r') as stream:
                if os.path.splitext(dependency_yaml)[1] == ".yaml":
                    self.data_ini = yaml.load(stream, Loader=FullLoader)
                elif os.path.splitext(dependency_yaml)[1] == ".json":
                    self.data_ini = json.load(stream)
                else:
                    print("The file format is not supported, only yaml and json are supported")
                    exit()
        dict_info = self.data_ini[target]
        self.get_cmds_list(dict_info, target, out_list)
        return out_list

    def get_cmds_list(self, input_data, target, restore_info_list):
        """
        :param restore_info_list: a list for cmd info
        :param input_data: a dict or list
        :param target: pv_calibre/pnr_innovus ....
        :return: a list return all cmds lists
        """
        if isinstance(input_data, dict):
            for ele_key, ele_value in input_data.items():
                if 'cmd' in ele_value:
                    restore_info_list.append(ele_value['cmd'])
                else:
                    self.get_cmds_list(ele_value, target, restore_info_list)
        if isinstance(input_data, list):
            for ele_value in input_data:
                self.get_cmds_list(ele_value, target, restore_info_list)

    @staticmethod
    def makefile_temp(makefile, target, step_name, run_script, merged_var, info_list=None, dir_path=None):
        """
        :param info_list: list of required information
        :param makefile: a makefile io object
        :param target: the tool target
        :param step_name: here is the step name
        :param run_script: the script to run in the target
        :param merged_var: all info restored in the merged_var
        :param dir_path: if not None, create a directory as target.step_name in dir_path
        :return:
        """
        if dir_path:
            os.makedirs(dir_path + "/" + target + "." + step_name, exist_ok=True)

        if info_list is None:
            # All info in blow list will be separated into info_dict, the makefile gen will base on info_dict
            # pnr_innovus["default"]["span"] -> info_dict["span"]
            # pnr_innovus["init_pnr"]["span"] -> info_dict["span"]
            # Eventually make file gen base on info_dict information in previous part
            info_list = ['cpu_num', 'memory', 'option', 'queue', 'span', 'tool_opt', 'lsf']

        makefile.write("	@echo \"Running: " + target + "." + step_name + "\"\n")
        makefile.write("	@sleep 2s \n")
        info_dict = dict()
        # Init all as empty
        for ele in info_list:
            info_dict[ele] = ""
        # Use default info if exist
        for ele in info_list:
            if "default" in merged_var[target].keys():
                if ele in merged_var[target]['default'].keys():
                    info_dict[ele] = merged_var[target]['default'][ele]
                    if step_name in merged_var[target].keys():
                        if ele in merged_var[target][step_name].keys():
                            info_dict[ele] = merged_var[target][step_name][ele]
        # Use step info if exist
        if step_name in merged_var[target]:
            if 'tool_opt' in merged_var[target][step_name].keys():
                info_dict['tool_opt'] = merged_var[target][step_name]['tool_opt']
        # setup final str for makefile
        cd_str = "@cd runs/%s.%s; " % (target, step_name)
        bsub_str = "bsub -q %s " % (info_dict['queue'])
        ini_str = cd_str + bsub_str
        job_name = target + "." + step_name
        resource_str = " -n %s -R \"rusage[mem=%s] span[hosts=%s]\"" % (info_dict['cpu_num'], info_dict['memory'], info_dict['span'])
        log_str = " |tee -i ../../logs/%s.%s.log;" % (target, step_name)
        gzip_log = " gzip -f ../../logs/%s.%s.log" % (target, step_name)
        if "lsf" in info_dict.keys() and info_dict["lsf"]:
            final_str = "	" + ini_str + "-Ip -J " + job_name + resource_str + " " + info_dict['tool_opt'] + " " + run_script + log_str + gzip_log + "\n"
        else:
            final_str = "	" + cd_str + info_dict['tool_opt'] + " " + run_script + log_str + gzip_log + "\n"
        makefile.write("	@mkdir -p runs/%s.%s\n" % (target, step_name))
        makefile.write(final_str)

    def gen_dependency(self, input_data: 'dict|list', makefile, lib_info_path, target, merged_var, runs_dir=None) -> None:
        """
        :param target:
        :param input_data:
        :param makefile:
        :param lib_info_path:
        :param merged_var: the merged dict contains all information
        :param runs_dir: if specified directory, then related directory will be created
        :return:
        """
        if isinstance(input_data, dict):
            for ele_key, ele_value in input_data.items():
                if "in" in ele_value and ele_value["in"] is not None:
                    makefile.write(ele_key + ": " + ele_value["in"] + "\n")
                    # Below if else just for Makefile's format with 1 \n or 2\n
                    if 'cmd' in ele_value:
                        run_script = lib_info_path + "/" + target + "/" + ele_value['cmd']
                        DependencyIni.makefile_temp(makefile, target, ele_key, run_script, merged_var, None, runs_dir)
                    else:
                        makefile.write("\n")
                else:
                    makefile.write(ele_key + ": " + "\n")
                    # Below if else just for Makefile's format with 1 \n or 2\n
                    if 'cmd' in ele_value:
                        run_script = lib_info_path + "/" + target + "/" + ele_value['cmd']
                        # Something wrong here need update, forbidden user to change some settings, 0508
                        DependencyIni.makefile_temp(makefile, target, ele_key, run_script, merged_var, None, runs_dir)
                    else:
                        makefile.write("\n")

                if "out" in ele_value and ele_value['out'] is not None:
                    # "TAB key" + "run cmds" + "\n" here
                    if "in" in ele_value.keys() and ele_value['in'] is not None:
                        makefile.write(ele_value["out"] + ": " + ele_value["in"] + "\n")
                    else:
                        makefile.write(ele_value["out"] + ": " + "\n")
                    if "cmd" in ele_value:
                        run_script = lib_info_path + "/" + target + "/" + ele_value['cmd']
                        DependencyIni.makefile_temp(makefile, target, ele_key, run_script, merged_var, None, runs_dir)
                    makefile.write("\n")
        if isinstance(input_data, list):
            for ele_value in input_data:
                self.gen_dependency(ele_value, makefile, lib_info_path, target, merged_var, runs_dir)
        return None


if __name__ == '__main__':
    yaml_file = "/home/chenanping/module/python_module/create_makefile/case/lab.yaml"
    tcl_file = "/home/chenanping/module/python_module/create_makefile/case/lab.tcl"

    info_path = "/home/chenanping/module/python_module/create_makefile/case"
    makefile_yaml = info_path + "/make_file.yaml"
    makefile_result = info_path + "/makefile"
    new_dict = dict()
    new_dict['a1'] = 'a1'
    file_yaml = '/home/chenanping/test.yaml'
    DependencyIni.dict2out(new_dict, file_yaml)
