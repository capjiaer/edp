set package_dir [file dirname [file normalize [info script]]]

package ifneeded file_edit_func 1.0 [list source [file join $package_dir module_setup.tcl]]
package ifneeded rule_temp 1.0 [list source [file join $package_dir module_setup.tcl]]
package ifneeded gen_deck_header 1.0 [list source [file join $package_dir gen_deck.tcl]]
package ifneeded data_func 1.0 [list source [file join $package_dir data_func.tcl]]
package ifneeded old_files 1.0 [list source [file join $package_dir module_setup.tcl]]
package ifneeded debug_proc 1.0 [list source [file join $package_dir debug_setup.tcl]]












