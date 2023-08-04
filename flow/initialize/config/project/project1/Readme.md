All required target settle here

For each target, 2 files required:

Take pv_calibre as example:
	> flow.yaml
		Contains all flow secquence request
		This one works for makefile creation

	> config.yaml
		All basic pv_calibre settings here and these will be merged into the full_var.yaml
        This yaml contains the initialization for the tools
