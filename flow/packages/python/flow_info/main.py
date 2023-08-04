#! /usr/bin/python3.9
############################################################
# File Name: main.py
# Author: anping.chen
# Email: capjiaer@163.com
# Created Time: Fri 10 Feb 2023 10:26:52 AM CST
############################################################
import shutil
import sys
import os
import argparse
import git
import subprocess, time
from shutil import copytree, rmtree, move
file_dir = os.path.dirname(os.path.realpath(__file__))
package_dir = os.path.dirname(file_dir)
sys.path.append(package_dir)
from dependency.main import GetUserInfo, DependencyIni


class GetFlowInfo:
    def __init__(self):
        super(GetFlowInfo, self).__init__()
        self.ini_info = "ENGINEERING DEVELOPMENT PLATFORM"

    def get_ini_info(self):
        print("========= Engineering Development Platform =========")
        print(self.ini_info)
        print("========= Engineering Development Platform =========")


class FlowIni:
    def __init__(self):
        super(FlowIni, self).__init__()

    @staticmethod
    def create_makefile(info_dict, block_name="block_name", mode="flow_ini", dependency_info_dict="dependency"):
        print('[EDP_INFO] Generating dependency and makefile...')
        if mode == "flow_ini":
            makefile_path = os.getcwd() + "/" + info_dict[block_name] + "/main/Makefile"
        elif mode == "flow":
            makefile_path = os.getcwd() + "/Makefile"
        if os.path.exists(makefile_path):
            os.remove(makefile_path)
        # Eventually, Makefile creation base on sequence info and pre_setup info
        for ele in info_dict['sequence']:
            if mode == "flow_ini":
                target_info_path = info_dict[block_name] + "/flow/initialize/config/project/" + ele
                dependency_yaml = os.getcwd() + "/" + target_info_path + "/dependency.yaml"
            elif mode == "flow":
                target_info_path = os.getcwd() + "/flow/initialize/config/project/" + ele
                dependency_yaml = target_info_path + "/dependency.yaml"
            DependencyIni(dependency_yaml).create_dependency(makefile_path, ele, os.path.dirname(dependency_yaml), info_dict, mode=dependency_info_dict)

    @staticmethod
    def gen_args():
        options = argparse.ArgumentParser()
        options.add_argument("-c", "--config", required=False, type=str, default="user_config.yaml",
                             help="users need to prepare a config file for flow initialization")
        options.add_argument("-b", "--branch", required=False, type=str, default="main",
                             help="the branch information is required")
        args = options.parse_args()
        return args

    @staticmethod
    def copytree(source_dir, target_dir):
        # Copy all files in source_dir to target_dir
        for root, dirs, files in os.walk(source_dir):
            target_root = os.path.join(target_dir, os.path.relpath(root, source_dir))
            os.makedirs(target_root, exist_ok=True)
            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_root, file)
                if os.path.exists(source_file):
                    shutil.copy2(source_file, target_file)

    @staticmethod
    def refresh_flow(dict_in, source_dir, branch, git_url="http://172.30.9.210:8899/flowdev/edp.git", git_branch="master", username="username", password="password"):
        source_path = os.getcwd().split("/" + dict_in["block_name"] + "/", 1)[0]
        block_dir = source_path + "/" + dict_in["block_name"]
        flow_dir = block_dir + "/" + dict_in['nick_name'] + "/" + branch + '/flow'

        if os.path.isdir(flow_dir) is True:
            rmtree(flow_dir)
        if os.path.isdir(flow_dir) is False:
            # Here should be git clone, but now just copy
            FlowIni.auto_git(git_url, flow_dir + "/main_pack", branch=git_branch, username=username, password=password)
            # git.Repo.clone_from(git_url, flow_dir + "/main_pack", branch=git_branch)
            source_dir = flow_dir + "/main_pack/flow/"
            FlowIni.copytree(source_dir, flow_dir)
            print("Git clone succeeded:", git_branch)
        cfg_dir = flow_dir + "/initialize/config/project/"
        # all copied to local and if not required, then remove
        for ele in os.listdir(cfg_dir):
            if ele != dict_in["project_name"]:
                rmtree(cfg_dir + ele)
        for ele in os.listdir(cfg_dir + dict_in["project_name"]):
            source = cfg_dir + dict_in["project_name"] + "/" + ele
            shutil.move(source, cfg_dir)
        rmtree(cfg_dir + dict_in["project_name"])
        print("Flow updated and refreshed")

    @staticmethod
    def dir_gen(source_dir, dict_in, block_name="block_name", project_name="project_name", branch="main", refresh=True, git_url="http://172.30.9.210:8899/flowdev/edp.git", git_branch="master", username="username", password="password"):
        source_path = os.getcwd().split("/" + dict_in[block_name] + "/", 1)[0]
        block_dir = source_path + "/" + dict_in[block_name]
        target_dir = block_dir + "/" + dict_in['nick_name'] + '/' + branch
        flow_dir = target_dir + '/flow'
        if branch != "main":
            target_dir = os.path.dirname(os.getcwd()) + "/" + branch
        # Working directory setup
        required_dir = ['data', 'logs', 'rpts', 'tune', 'hooks', 'libs', 'cmds', 'config', 'pass', 'runs']
        for ele in required_dir:
            set_ele = target_dir + "/" + ele
            if os.path.isdir(set_ele) is False:
                os.makedirs(set_ele)
        # Copy readme file
        os.system('cp ' + source_dir + "/Readme.md" + " " + target_dir + "/")
        if refresh:
            FlowIni.refresh_flow(dict_in, source_dir, branch, git_url=git_url, git_branch=git_branch, username=username, password=password)
        print("")
        print('Details please refer to ' + target_dir + '/' + dict_in['nick_name'] + '/Readme.md')

    @staticmethod
    def auto_git(repo_url, destination_path, branch, username='username', password='password'):
        # this function helps do git init
        # Check if exist the "~/.git-credentials"
        check_file = os.path.expanduser("~") + '/.git-credentials'
        if os.path.exists(check_file) is False:
            # Init git
            print("Git init for first time setup, log in as \"%s\"" % username)
            os.system("git config --global credential.helper store")
            # Auto init file creation
            with open(check_file, "w") as stream:
                stream.write("http://" + username + ":" + password + "@172.30.9.210%3a8899")
            git.Repo.clone_from(repo_url, destination_path, branch=branch)
        else:
            git.Repo.clone_from(repo_url, destination_path, branch=branch)


if __name__ == '__main__':
    GetFlowInfo().get_ini_info()
