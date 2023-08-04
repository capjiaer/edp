initialize: This dir will be moved base on the "project_name" 
    -cmds
        # all ini_cmds for each sub-function settled here
        -pv_calibre:
            -fp_drc.tcl: working for drc run
            -fp_ipmerge.tcl: working for ipmerge run
            ...
        -pnr_innovus:
            -pre_place.tcl: working for pre_place
            -pre_routing.tcl: working for pre_routing
            ...
        ...
    -target
        -pv_calibre:
            -config.yaml: working for ini config setup for targets
            -dependency.yaml: working for dependency setup for target functions
        -pnr_innovus:
            -config.yaml: working for ini config setup for targets
            -dependency.yaml: working for dependency setup for target functions
        ...
    -templates
        -pv_calibre
            -fp_drc.temp: working for gen fp drc run rules
            -fp_ipmerge.temp: working for gen fp_ipmerge run rules
            ...
        -pnr_innovus
            -required.temp: working for reuqirement
            ...
        ...
    ->  

############################################################
lets set a example:
if the input yaml file contains below:
project_name: project1
the project name will replace the name of initialization
example:
dir will be settled from:
/home/chenanping/jedp/source/jedp/initialize -> /home/chenanping/jedp/source/jedp/project1_ini


