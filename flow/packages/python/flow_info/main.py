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
				target_info_path = info_dict[block_name] + "/flow/initialize/config/" + ele
				dependency_yaml = os.getcwd() + "/" + target_info_path + "/dependency.yaml"
			elif mode == "flow":
				target_info_path = os.getcwd() + "/flow/initialize/config/" + ele
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
	def copytree(source_dir, target_dir, link_mode = 0, overwrite = 0):
		"""
		params: source_dir -> copy from dir
		params: target_dir -> copy to dir
		params: link_mode -> if link_mode 1, then the file will be link in the target dir
		params, overwrite -> if overwrite 1, then the link_mode will remove target file first, then re-link, but fi overwrite is 0, then link mode skip files which already exist in the target dir.
		"""

		# Copy all files in source_dir to target_dir
		for root, dirs, files in os.walk(source_dir):
			target_root = os.path.join(target_dir, os.path.relpath(root, source_dir))
			os.makedirs(target_root, exist_ok=True)
			for file in files:
				source_file = os.path.join(root, file)
				target_file = os.path.join(target_root, file)
				if os.path.exists(source_file):
					if link_mode:
						if overwrite:
							if os.path.exists(target_file):
								os.remove(target_file)
						if not os.path.exists(target_file):
							os.symlink(source_file, target_file)
						# Update 20231114, incase users modify it unexpectedly
						os.chmod(source_file, 0o555)
					else:
						shutil.copy2(source_file, target_file)


	@staticmethod
	def refresh_flow(dict_in, source_dir, branch, git_url="git_url", git_branch="master", username="username", password="password", keep_git=0, required_dirs=[]):
		source_path = os.getcwd().split("/" + dict_in["block_name"] + "/", 1)[0]
		block_dir = source_path + "/" + dict_in["block_name"]
		flow_dir = block_dir + "/" + dict_in['nick_name'] + "/" + branch + '/flow'

		FlowIni.git_info_partial(os.path.dirname(flow_dir), keep_git = keep_git, git_branch=git_branch, required_dirs=required_dirs, input_dict=dict_in)

	@staticmethod
	def dir_gen(source_dir, dict_in, block_name="block_name", project_name="project_name", branch="main", refresh=True, git_url="git_url", git_branch="master", username="username", password="password", keep_git=0, required_dirs=[]):
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
			FlowIni.refresh_flow(dict_in, source_dir, branch, git_url=git_url, git_branch=git_branch, username=username, password=password, keep_git=keep_git, required_dirs=required_dirs)
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

	@staticmethod
	def git_info_partial(local_dir, git_branch='main', input_dict=dict(), repo_url="git@github.com:capjiaer/edp.git", required_dirs=[], foundry_name="SAMSUNG", node='S4', project_name='project1', keep_git=1):

		if input_dict:
			foundry_name = input_dict['foundry'].upper()
			node = input_dict['node']
			project_name = input_dict['project_name']
			if "git_url" in input_dict.keys():
				repo_url = input_dict['git_url']

		prj_info_sub = "foundry/{}/{}/{}".format(foundry_name,node,project_name)
		config_dir = local_dir + "/flow/initialize/config/"
		prj_info = config_dir + prj_info_sub
		git_config_dir = "/flow/initialize/config/" + prj_info_sub

		destination_path = local_dir
		if keep_git:
			if os.path.exists(destination_path + "/.git"):
				print("git detected, skip edp initialization in", destination_path)
				return
			else:
				print("git will be remain in the run dir")
				print("in this mode, you may update flow by git if only you want")
		# Refresh destination_path and git
		if os.path.exists(destination_path + "/.git"):
			shutil.rmtree(destination_path + "/.git")

		if os.path.exists(destination_path + "/flow"):
			shutil.rmtree(destination_path + "/flow")
		os.makedirs(destination_path + "/flow")

		# Git init
		git_init_cmd = ["git", 'init']
		subprocess.run(git_init_cmd, cwd= destination_path)

		# Create sparse-checkout file for usage, here take flow as setup
		sparse_checkout_file = destination_path + "/.git/info/sparse-checkout"
		git_sparescheckout = ['git', 'config', 'core.sparsecheckout', 'true']
		with open(sparse_checkout_file, 'w') as stream:
			# Default requirement
			stream.write("flow/initialize/cmds/\n")
			stream.write("flow/initialize/templates/\n")
			stream.write(git_config_dir + "\n")
			# For ele in required_dirs, it will be cloned
			for dir_name in required_dirs:
				stream.write(dir_name + "\n")

		# Turn on sparsecheckout
		subprocess.run(git_sparescheckout, cwd=destination_path)

		# Setup git links from source
		git_add_repo = ['git', 'remote', 'add', 'origin', repo_url]
		subprocess.run(git_add_repo, cwd=destination_path)

		# Git pull target file
		# Modified 1128
		git_pull = ['git', 'pull', repo_url]
		# git_pull = ['git', 'pull', 'origin', repo_url]
		subprocess.run(git_pull, cwd=destination_path)
		print("Git clone succeeded:", git_branch)
		print("Flow Updated and Refreshed")

		# Turn off sparsecheckout
		git_sparescheckout = ['git', 'config', 'core.sparsecheckout', 'false']
		subprocess.run(git_sparescheckout, cwd=destination_path)

		# Move config dir
		FlowIni.copytree(prj_info, config_dir)
		if os.path.exists(config_dir + "/foundry"):
			shutil.rmtree(config_dir + "/foundry")

		# rm git info here 20231110, the user udpate decided by the git owner here, maybe bugs here, if git owner updated git, the user have to update if below logic
		if os.path.exists(destination_path + "/.git"):
			if not keep_git:
				shutil.rmtree(destination_path + "/.git")


if __name__ == '__main__':
	GetFlowInfo().get_ini_info()
