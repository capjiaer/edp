# This script works for the lib generation
# Below generation can be selected:
# cdl/layout/verilog/tech/ndm/lib/lef etc..
import collections
import os, sys
import re
import warnings
import pathlib
from collections import defaultdict
import pandas as pd
from shutil import rmtree
file_dir = os.path.dirname(os.path.realpath(__file__))
package_dir = os.path.dirname(file_dir)
sys.path.append(package_dir)
from dependency.main import *
from translate.translate import TranslateCmd


# For ListToDict
def nested_dict():
    return defaultdict(nested_dict)


# For yaml file transformation
def config_sort(config_dir, yaml_list, merged_tcl_name='full.tcl', info=True, input_dict={}, info_key="setup_tcl"):
    # Get the final merge tcl file
    merged_info = os.path.join(config_dir, merged_tcl_name)
    if os.path.exists(merged_info):
        os.remove(merged_info)
    # Below secquence has been modified
    # [yaml1,yaml2.., yaml_final] -> [yaml1,yaml2.., tcl_info, yaml_final]
    for yaml_ele in yaml_list[:-1]:
        DependencyIni(yaml_ele).yaml2tcl(yaml_ele, merged_info)
    # Tcl file insertion is required 20231108, write tcl_info into merged_info
    if input_dict and info_key in input_dict.keys():
        tcl_file = input_dict[info_key]
        TranslateCmd.get_dict_interp(tcl_file)
        DependencyIni().tcl2tcl(tcl_file, merged_info)
    # yaml_final insertion
    DependencyIni(yaml_list[-1]).yaml2tcl(yaml_list[-1], merged_info)
    if info:
        print("[TCL_INFO] Yaml transformation finished: ", merged_info)


class GetSortedLib:
    # A target path to generate lib is required
    def __init__(self, target_path):
        super().__init__()
        self.target_path = target_path

    @staticmethod
    def link_libs(source_dir, link_dir, sub_dir='libs', show_libs=False):
        """
        :param show_libs: show more info if required
        :param source_dir: a directory contains the libraries
        :param link_dir: a target directory for link setup eventually
        :param sub_dir: default is 'libs', which means the link_dir is always under the link_dir/sub_dir
        :return: None
        """
        # Do backup first
        ini_lib_dir = os.path.join(link_dir, sub_dir)
        backup_dir = os.path.join(link_dir, "backup/libs%s" % time.strftime("%Y%m%d_%H%m", time.gmtime()))
        if os.path.exists(ini_lib_dir) and len(os.listdir(ini_lib_dir)) != 0:
            os.makedirs(backup_dir, exist_ok=True)
            if os.path.exists(backup_dir):
                rmtree(backup_dir)
            os.rename(ini_lib_dir, backup_dir)
            os.makedirs(ini_lib_dir, exist_ok=True)
            print('Backing up... the old libs will be restored -> ', backup_dir)

        # Do link creation
        print("lib link source: ", source_dir, "\n")
        if not os.path.exists(source_dir):
            print("[EDP_ERROR] lib source specification incorrect, please recheck your config")
            exit()

        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_file = os.path.join(root, file)
                sub_path = source_file.split(source_dir)[-1]
                target_link = os.path.join(link_dir, sub_dir + '/' + sub_path)
                target_dir = os.path.split(target_link)[0]
                pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)
                if os.path.exists(target_link) is False:
                    os.symlink(source_file, target_link, target_is_directory=True)
                    if show_libs is True:
                        print(f"Symlink {target_link} created")
                else:
                    if show_libs is True:
                        print(f"File {target_link} links already exists")
        print(f"lib link creation finished")

    @staticmethod
    def gen_merged_lists(source_dir, target_dir, key_word):
        os.makedirs(target_dir, exist_ok=True)
        ini_list = []
        file_list = os.listdir(source_dir)
        target_file = os.path.join(target_dir, key_word)
        # make sure the target file is fresh
        if os.path.exists(target_file):
            os.remove(target_file)
        for file in file_list:
            if re.search(key_word, file):
                ini_list.append(source_dir + "/" + file)
        if len(ini_list) == 0:
            print("No %s files found in source directory" %key_word)
        else:
            # Get all files infor with the key_word
            merged_info = ""
            for file in ini_list:
                with open(file, "r") as stream:
                    merged_info = merged_info + stream.read()
            with open(target_file, 'w') as lib_info_io:
                lib_info_io.write(merged_info)
            print("LIB_GEN_INFO: libs file %s generated" % target_file)


class PvtMapping:
    def __init__(self, excel_path):
        super().__init__()
        self.excel_path = excel_path

    def get_pvt_dict(self, sheet_name='ctip-pvt-mapping'):
        sheet_info = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=0)
        # The column under 'type' is the cell name
        dict_info = sheet_info.to_dict('records')
        pvt_info = dict()
        for sub_dict in dict_info:
            cell_name = sub_dict['type']
            sub_dict.pop('type')
            pvt_info[cell_name] = sub_dict
        return pvt_info


class ExcelToDict:
    def __init__(self, excel_path):
        super().__init__()
        self.excel_path = excel_path

    def read_excel(self, sheet_name='tech-file-list', fillna_mode='ffill', return_info='info_dict'):
        """
        :param sheet_name: claim the name of the sheet
        :param fillna_mode: 'ffill', 'bfill', 'pad'
        :param return_info: 'info_dict' or 'sheet_info'
        :return: directory restore all information
        """
        # Read in the Excel file and refresh the dataframe
        sheet_info = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=0)
        sheet_info.dropna(subset=["files"], inplace=True)
        item_list = sheet_info.columns

        # Fill in the missing values
        for item in item_list:
            sheet_info[item].fillna(method=fillna_mode, inplace=True)
        # It will be automatically get the latest file version if with .T
        info_dict = sheet_info.to_dict('records')
        # info_dict = sheet_info.set_index(column).to_dict('records')
        if return_info == 'info_dict':
            return info_dict
        elif return_info == 'sheet_info':
            return sheet_info

    @staticmethod
    def transform_dict(input_dict):
        for key, value in input_dict.items():
            if isinstance(value, dict):
                input_dict[key] = ExcelToDict.transform_dict(input_dict[key])
        return dict(input_dict)

    @staticmethod
    def get_info(info_dict=None, excel_path=None, sheet_name=None):
        """
        read_excel() function get an initial info_dict
        Base on the previous info_dict
        Resort the info into a better format for further usage
        you can use sheet_name to select different sheets
        :param:
        info_dict: if provided info_dict, the excel_path and sheet_name will be ignored
        excel_path: an Excel file path is required if info_dict is not provided
        sheet_name: a sheet name is required if info_dict is not provided
        :return: a nested dict with switched into a dict
        """
        ini_dict = nested_dict()

        if info_dict is None:
            if not excel_path:
                print("[EDP_ERROR] if info_dict is None, excel_path and sheet_name must be exist")
                exit()
            info_dict = ExcelToDict(excel_path).read_excel(sheet_name=sheet_name)
        else:
            if not excel_path:
                print("[EDP_ERROR] if info_dict exists, excel_path and sheet_name must be None")
                exit()

        for ele in info_dict:
            # ini_dict[ele['flow']][ele['function']][ele['version']] = ele['files'] -> tech info
            # ini_dict[ele['lib_info']][ele['version']] = ele['files'] -> lib info
            ini_dict_str = 'ini_dict'
            valid_list = list(ele.keys())
            value_file = valid_list[-1]
            valid_list.pop()
            for key in valid_list:
                if str(ele[key]) != 'nan':
                    ini_dict_str = ini_dict_str + '[\'' + ele[key] + '\']'
            if len(ele[value_file].split()) > 1:
                # if result is more than one, return a list
                ini_dict_str = ini_dict_str + ' = ' + str(ele[value_file].split())
            else:
                # return a single string
                ini_dict_str = ini_dict_str + ' = ' + '\'' + ele[value_file] + '\''
            exec(ini_dict_str)
        ini_dict = ExcelToDict.transform_dict(ini_dict)
        return ini_dict


if __name__ == "__main__":
    ExcelPath = "/home/chenanping/jedp/source/libs/gen_libs/case/temp.xlsx"
    # ctip_pvt_info = PvtMapping(ExcelPath).get_pvt_dict('ctip-pvt-mapping')
    # print(pvt_info.keys())
    # print(ctip_pvt_info['rgo_tsmc07_18v33_7ff_20c_spt_ivt'])
    # tech_info = ExcelToDict(ExcelPath).read_excel(sheet_name='tech-file-list')
    # tech_info_dict = ExcelToDict.get_info(tech_info)
    # print(tech_info_dict['pv_calibre']['drc']['1.2a'])

    # stdlib_info = ExcelToDict(ExcelPath).read_excel(sheet_name='stdcel-file-list')
    stdlib_info = ExcelToDict(ExcelPath).read_excel(sheet_name='tech-file-list')
    # print(stdlib_info)
    get_lib_info = ExcelToDict.get_info(excel_path=ExcelPath, sheet_name='tech-file-list')
    print(get_lib_info)
    # for ele in get_lib_info.keys():
    #    print(get_lib_info[ele])
    # stdlib_info_dict = ExcelToDict.get_lib_info(stdlib_info)
