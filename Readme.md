You may see below dirs in the work directory:

==================================================
FILES:

1: ./Readme.md	->
	Help doc for user usage

2: ./user_config.yaml	->
	A user cfg template for flow initialization

3: ./requirement.txt
	pip3.9 install -r requirement.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

4: ./env_setup.csh
	Env setup for user initialization
	steps:
	4.0:
		Then you can use edp_ini to initial your run
		source ./env_setup.csh
	4.1: 
		mkdir testcase
		cp ./user_config.yaml testcase/
	4.2:
		cd testcase
		edp_ini

==================================================

DIRS:

1: config	->
	The config file from flow_ini.yaml/project.yaml/user_config.yaml.
	They have been tranformed into final tcl files, all vars in yaml have been flatten here.

2: data		->
	The outputs for each target link here, which will be convinent for the user to get generated database.

3: hooks	->
	It is possible to add the third party target for the flow if required, such as:
		"pre_steps -> pv_calibre_dummy -> pv_calibre_drc -> post_steps".
	A hook target can be exist named as pv_calibre_hook_gds, then the steps works as: 
		"pre_steps -> pv_calibre_dummy -> pv_calibre_hook_gds -> pv_calibre_drc -> post_steps"

4: jedp		->
	All flow template will be settle here, for each run target, all variables will NOT be updated incase users modified user_config.yaml unconciously
	How to update params: 
	> jedp -u
	Then 2 files rewrite: merged_info.yaml merged_info.tcl.
	jedp/libs: lib setup yaml and related settle here
	jedp/main: main flow here
	jedp/others: others
	jedp/targets: all included targets
	jedp/template: all template required by targets or main

5: logs		->
	logs will be seperated into 2 parts: lsf_logs and work_logs.

6: rpts		->
	rpts will be seperated here.

7: tune		->
	The enhance scripts will be settled here if required, this one is different from templates in jedp dirs:
	- The template in jedp is std flow for each target 
	- Tune file is a enhance script for each target

All in all:
	jedp	-> works for all main flow
	hooks	-> works for add addtional target incase the main flow does not support
	tune	-> works for main flow enhance
	
