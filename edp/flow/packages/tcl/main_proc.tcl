proc get_proc_info {tag} {
	# This proc works for deliver required procs for each sub flow.
	set script_path [file normalize [info script]]
	regexp -nocase {(.*flow)/(.*)} $script_path matched_info flow_path rest_info 
	set proc_path [file join $flow_path "initialize/cmds" $tag "proc"]
	puts "Get proc info from $proc_path"
	set file_list [glob -nocomplain -type f [file join $proc_path *]]
	return file_list
	foreach ele $file_list {
		source $ele
	}
}

