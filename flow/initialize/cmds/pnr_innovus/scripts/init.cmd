#0>> Import packages for the furture usage
# import util tcl_env.tcl

#1 >> modified samsung n4 flow as ref flow
#Init basic information
set step "init"

setMultiCpuUsage -reset
if {[info exist pnr_innovus(default,cpu_num)]} {
	setMultiCpuUsage -localCpu $pnr_innovus(default,cpu_num)
} else {
	setMultiCpuUsage -localCpu 8
}

set fpgOddEvenSitesRowConstraint 1

set init_pwr_net "$pnr_innovus(r_power) $pnr_innovus(v_power)"
set init_gnd_net "$pnr_innovus(ground)"
set init_lef "$pnr_innovus(tech_lef) $pnr_innovus(cell_lefs)"
set init_mmmc_file [file normalize $pnr_innovus(mmmc_file)]
set init_verilog "$pnr_innovus(netlist)"

setDesignMode -process 4 -node S4
setNanoRouteMode -dbProcessNode S4
setExtractRCMode -lefTechFileMap $pnr_innovus(qrctech_map_file)

#1 >> Do initialization
init_design

# Via pillar auto generation (example)
if { [info exist pnr_innovus(via_pillar_flow)] && $pnr_innovus(via_pillar_flow) == 1 } {
  gen_vp -process_node N5 -vp_bottom_layer M1 -vp_top_layers F4 -allow_finger_outside_cell 1 \
  -output_rule_lef_file vp_rule.lef -output_association_file vp_assoc.tcl -match_pattern {(.*)(_D)([0-9]*)(\S*)}

  #loadLefFile ./vp_rule.lef
  loadLefFile $pnr_innovus(vp_rule_lef_file)
}

############################################################
# Floorplan
############################################################


# Power connect
if {$pnr_innovus(v_power) == "" } { 
	set pnr_innovus(v_power) $pnr_innovus(r_power)
}

# Upf flow
if { [file exist $pnr_innovus(upf_file)] || $pnr_innovus(lowpower_design) == 1 } {
  puts "Read UPF flow"
  read_power_intent -1801 $pnr_innovus(upf_file)
  commit_power_intent
}

# Override power connection (Need check UPF or Innovus)
source $pnr_innovus(global_net_connect_file)

# Create placement halo around marco
addHaloToBlock {1 1 1 1} -allBlock

if { $pnr_innovus(floorplan) == 1 && [file exist $pnr_innovus(def)] } {
  defIn $pnr_innovus(def)
  deleteRow -all
  initCoreRow

  # Routing track adjusting to limit drc
  source $pnr_innovus(4nm_addTrack_file)
  
  # Override power connection (Need check UPF or Innovus)
  source $pnr_innovus(global_net_connect_file)

  # Upf flow
  if { [file exist $pnr_innovus(upf)] || $pnr_innovus(lowpower_design) == 1 } {
  	puts "Read UPF flow"
	read_power_intent -1801 $pnr_innovus(upf)
	commit_power_intent
  }

  saveDesign dbs/powerplan.enc
} else {
  floorPlan -r 1 $pnr_innovus(util) 0.54 0.54 0.54 0.54
  source ./innovus_scripts/etc/4nm_addTrack.tcl
}

# Create placement halo around marco
addHaloToBlock {2 2 2 2} -allBlock
addRoutingHalo -allBlocks -space 0.3 -bottom M1 -top M3

## Insert Physical cell
#================================================================================================
saveDesign dbs/b4_phyCells.enc

# Insert Physical cell
if { $pnr_innovus(lowpower_design) != 1 } {
  set powerDomainName "" ; set is_OnOff 0
  source $env(SCRIPTS)/floorplan/01_place_finishing_cell.tcl
} elseif { $pnr_innovus(lowpower_design) == 1 } {
   foreach pdinfo $pnr_innovus(pd_list) {
      scan $pdinfo "%s %s" powerDomainName is_OnOff
      source $env(SCRIPTS)/floorplan/01_place_finishing_cell.tcl
  }
}

# Swap Top/Bottom cell for RXFIN.C.4 rule (7p94TR only)
if { $pnr_innovus(track) == "7P94TR" } {
  source $env(SCRIPTS)/floorplan/02_swap_topbottom_cell.tcl
}

saveDesign dbs/floorplan.enc


#================================================================================================
## Power Plan
#================================================================================================

# Define power spec in below script
source $env(SCRIPTS)/floorplan/03_powerplan.tcl

saveDesign dbs/powerplan.enc

#================================================================================================
## Verify Floor Plan
#================================================================================================
verify_drc -check_only special -limit 100000
checkPlace

set vars($step,stop_time) [clock seconds]
set run_time [expr $vars($step,stop_time) - $vars($step,start_time)]

exec touch $env(PASS_DIR)/$step


exit
