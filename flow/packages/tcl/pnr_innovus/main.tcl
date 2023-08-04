proc upf_flow {} {
	global pnr_innovus
	puts "Read UPF"
	read_power_intent -1801 $pnr_innovus(upf)
	commit_power_intent
}

proc readin_fp {} {
	global pnr_innovus
	if {[file exist $pnr_innovus(fp_def)]} {
		defIn $pnr_innovus(fp_def)
	} elseif {[file exist $pnr_innovus(def)]} {
		defIn $pnr_innovus(def)
	}
	deleteRow -all
	initCoreRow
}
