#! python3
##########################################################
# HOW TO INVOKE:
# eg: python3 mv_backup.py -s <OLD/PATH/TO/RM> -t <NEW> -d <DEPTH_INFO> -d <DEPTH> -i <INFO_TIME>
##########################################################

import sys, argparse, os, shutil, subprocess, asyncio
from pathlib import Path

global_file_list = []
global_dir_list = []
global_all_list = []


def gen_args():
    opts = argparse.ArgumentParser(add_help=True, description="A tool for backup a directory to the new directory")
    opts.add_argument("-s", "--source", required=True, help="Source directory for backup")
    opts.add_argument("-t", "--target", required=True, help="Target directory for backup")
    opts.add_argument("-d", "--depth", required=False, help="Depth of rsync operations", default=2)
    opts.add_argument("-i", "--info_time", required=False, help="information output time", default=30)
    opts.add_argument("-k", "--keep_old", required=False, help="if still remain old data after backup", default=1)
    args = opts.parse_args()
    if args.target == args.source:
        print("Fatal: the target directory is source directory, Error out")
        exit()
    return args


def list_files_and_folders(path, max_depth, current_depth=0):
    global global_file_list
    global global_dir_list
    # Check files
    items = os.listdir(path)
    files_list = [os.path.join(path, item) for item in items if os.path.isfile(os.path.join(path, item))]
    folders_list = [os.path.join(path, item) for item in items if os.path.isdir(os.path.join(path, item))]

    global_file_list = global_file_list + files_list
    if current_depth < int(max_depth):
        for path in folders_list:
            # Keep empty dir if exist
            if not os.listdir(path):
                global_dir_list.append(path)
            list_files_and_folders(path, max_depth, current_depth + 1)
    else:
        for path in folders_list:
            global_dir_list.append(path)


def rsync(source_path, target_path, pre_path_info="", log_pre_fix=1, log_dir="rsync_logs"):
    log_dir = os.getcwd() + "/" + log_dir
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # The directory shall be the source dirname here
    # Rsync is different from copy here
    if os.path.isdir(source_path):
        final_target_path = target_path + "_tmp"
        os.makedirs(final_target_path, exist_ok=True)
    else:
        final_target_path = target_path
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

    if log_pre_fix:
        base_info = target_path.replace(pre_path_info, "").strip("/").replace("/", "_")
        output_info = "-o" + log_dir + "/" + base_info + ".log"
        rsync_cmd = ["bsub", "-K", "-J", base_info, output_info, "rsync", "-avPh", source_path, final_target_path, "&"]
    else:
        rsync_cmd = ["bsub", "-K", "-J", os.path.basename(target_path), "rsync", "-avPh", source_path,
                     final_target_path, "&"]
    rsync_cmd = " ".join(rsync_cmd)
    return rsync_cmd


def delete_file_if_exist(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def main(source_dir, target_dir, depth, script_name="bsub_rsync.csh"):
    global global_dir_list
    global global_file_list
    global global_all_list

    match_info = dict()

    pre_length = len(source_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    list_files_and_folders(source_dir, depth)
    file_list = global_file_list
    dir_list = global_dir_list
    final_list = file_list + dir_list
    global_all_list = final_list

    # For all files
    delete_file_if_exist(os.getcwd() + script_name)
    with open(os.getcwd() + script_name, "a") as cmd_file:
        for ele in final_list:
            path_info1 = args.target
            path_info2 = ele[pre_length:].lstrip("/") if ele[pre_length:].startswith("/") else ele[pre_length:]
            target_path = os.path.join(path_info1, path_info2)
            cmd = rsync(ele, target_path, target_dir)
            match_info[ele] = target_path
            cmd_file.write(cmd + "\n")
    return match_info


def rm_file_and_link(rm_path, link_path, keep_old=0):
    if not int(keep_old):
        if os.path.isfile(rm_path):
            os.remove(rm_path)
        elif os.path.isdir(rm_path):
            shutil.rmtree(rm_path)
        print("remove old file done", rm_path)
        print("Create link:", rm_path, "from", link_path)
        os.symlink(link_path, rm_path)


def get_success_flag(file_name, keyword="Successfully completed"):
    with open(file_name, "r") as stream:
        for line_number, line in enumerate(stream, start=1):
            if keyword in line:
                return 1
    return 0


# Deal with concurrency problems
def move_contents_to_parent_folder(folder_path):
    parent_folder = os.path.dirname(folder_path)
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        destination_path = os.path.join(parent_folder, item)
        shutil.move(item_path, destination_path)
    os.rmdir(folder_path)


async def check_file(input_list, target_dir, info_time=30, keep_old=1):
    with open("error_info.log", "a") as stream:
        while not Path(input_list[2]).exists():
            print("Checking file " + input_list[2], "does not exist, waiting for", info_time, "seconds")
            await asyncio.sleep(int(info_time))
        # Check rsync success or not
        if get_success_flag(input_list[2]):
            if os.path.isdir(input_list[0]):
                move_contents_to_parent_folder(input_list[1] + "_tmp")
            rm_file_and_link(input_list[0], input_list[1], keep_old)
        else:
            info = "[ERROR] Move failed:" + input_list[1] + "! Check " + input_list[2] + " for more information"
            print(info)
            stream.write("#" + info + "\n")
            stream.write(rsync(input_list[0], input_list[1], target_dir) + "\n")


async def main_check(all_info_list, target_dir, info_time=30, keep_old=1):
    tasks = [check_file(input_list, target_dir, info_time, keep_old) for input_list in all_info_list]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    args = gen_args()
    script_path = os.getcwd() + "/bsub_rsync.csh"
    os.remove(script_path)

    info_dict = main(args.source, args.target, args.depth)

    os.chmod(script_path, 0o755)

    # Run scripts as required
    subprocess.run(script_path, shell=True, check=True)
    print("All bsub processes started")

    # Try remove and link
    log_info = []
    for key, value in info_dict.items():
        base_info = value.replace(args.target, "").strip("/").replace("/", "_")
        log_file = os.getcwd() + "/rsync_logs/" + base_info + ".log"
        log_list = [key, value, log_file]
        log_info.append(log_list)

    asyncio.run(main_check(log_info, args.target, args.info_time, args.keep_old))
    
