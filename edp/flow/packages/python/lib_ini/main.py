#! /usr/bin/python3.9
############################################################
# File Name: main.py
# Author: anping.chen
# Email: anping.chen@joinsilicon.com
# Created Time: Tue 14 Feb 2023 04:20:46 PM CST
############################################################

import argparse
import glob
import os
import sys

file_dir = os.path.dirname(os.path.realpath(__file__))
package_dir = os.path.dirname(file_dir)
sys.path.append(package_dir)
from lib_ini.gen_libs import *


# Get info and restore it into a dictionary
def get_config_info(config_file):
    """
    :param config_file: a yaml file or json file is required
    :return: a dictionary base on the config file
    """
    if re.match('.*\.json', config_file):
        with open(config_file, 'r') as stream:
            data_ini = json.load(stream)
    elif re.match('.*\.yaml', config_file):
        with open(config_file, 'r') as stream:
            data_ini = yaml.load(stream, Loader=yaml.FullLoader)
    else:
        print("Please input a json or yaml file")
        exit(1)
    return data_ini


def lib_link_creation(config_file, sheet_name='stdcel-file-list', install_tag='libs'):
    """
    :param install_tag: can be 'libs' or 'tech'
    :param sheet_name: can be either 'stdcel-file-list' or 'CTIP-file-list' or 'JEDP-file-list' or 'tech-file-list'
    :param config_file: a yaml file or json file is required
    In the config_file:
        excel_path with tech info is required
        install_dir for the tech installation is required
    :return: None
    """

    data_ini = get_config_info(config_file)
    excel_path = data_ini['excel_path']
    std_sheet_info = ExcelToDict(excel_path).read_excel(sheet_name=sheet_name, return_info='sheet_info')
    column_list = std_sheet_info.columns.tolist()
    type_info = column_list[0]
    file_info = column_list[-1]
    # New column_list contains all the rest column names
    column_list = column_list[1:-1]

    install_dir = data_ini['install_dir']
    if install_dir is None:
        install_dir = os.getcwd() + '/install'
        pathlib.Path(install_dir).mkdir(parents=True, exist_ok=True)
    if install_tag == 'libs':
        install_tag = install_tag + '/' + sheet_name.split('-')[0]
    print('The {0} file related information will be stored in -> {1}/{0}'.format(install_tag, install_dir))
    # Initialize finished

    # Link creation and warning setup
    # Directories setup then link creation
    lib_dir = install_dir + '/' + install_tag + '/'

    info_list = std_sheet_info.to_dict('records')
    for ini_info in info_list:
        ini_str = ini_info[type_info]
        # Libs link dirs initialization
        for column_name in column_list:
            if str(ini_info[column_name]) == 'nan':
                pass
            else:
                ini_str = ini_str + '/' + ini_info[column_name]
        dir_details = lib_dir + ini_str
        pathlib.Path(dir_details).mkdir(parents=True, exist_ok=True)
        # Source file path info, the value can be a list or a string, default separated by " ":
        lib_file_name = ini_info[file_info]
        for lib_file_cluster in lib_file_name.split():
            if not glob.glob(lib_file_cluster):
                print('[EDP_ERROR]     >>> Checking with the lib cluster, {1} {0}'.format(lib_file_cluster, ini_info[type_info]))
            else:
                # Each cell may contain multi file lists, each list is working as a lib_file_cluster
                for target_file in glob.glob(lib_file_cluster):
                    # Eventually, deal with each target_file
                    linked_info = dir_details + '/' + os.path.basename(target_file)
                    # Do soft-link here
                    if os.path.exists(target_file):
                        if os.path.exists(linked_info) is False:
                            os.symlink(target_file, linked_info)
                            print('[EDP_INFO]   The file ' + linked_info + ' link created successfully')
                        else:
                            print('[EDP_WARNING]   The file ' + linked_info + ' exists, skip link creation')
                    else:
                        # Source tech file doesn't exist, the link can not be created, touch an empty file for further usage
                        print('[EDP_ERROR]   >>The file ' + target_file + ' missing, refer to PM for more information')


def args_setup():
    # 0: Read in the config json file
    # 0.1 Setup arguments, an input json file or yaml file is required
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--infile", required=False, type=str,
                         default='/home/chenanping/jedp/source/libs/gen_libs/case/temp.yaml',
                         help="users need to prepare a config file for libs initialization")

    args = options.parse_args()
    if args.infile == '/home/chenanping/jedp/source/flow/gen_libs/case/temp.yaml':
        print("You didn't specify a config file, the default config file will be used")
        print("Please change the default config file for your real case")
        print("")
    return args


if __name__ == '__main__':
    # This script is used to generate tech directories based on the input Excel files
    # Two parts will be generated, tech_ini and lib_ini

    # Step1: setup arguments for the script
    argument = args_setup()

    # Step2: Create the tech_ini directory and links
    lib_link_creation(argument.infile, sheet_name='tech-file-list', install_tag='tech')

    # Step3: Create the lib_ini directory and links stdcel-file-list
    lib_link_creation(argument.infile, sheet_name='stdcel-file-list')

    # Step4: Create the lib_ini directory and links CTIP-file-list
    lib_link_creation(argument.infile, sheet_name='CTIP-file-list')
