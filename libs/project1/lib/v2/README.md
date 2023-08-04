# Generary setup will be links in the libs dir
# Std cells/ip/3rd_part ip's information will be sorted here

-cdl: PV
    The source netlist link will be settle here
    
-layout: PV
    All gds/oasis files settle here

-lef: PnR for routing
    all lef file for physical information here

-lib: PnR for routing
    all timing infor for PVT session

-ndm: PnR (FC/icc2)
    ndm = lef + lib

-verilog: PnR Routing/ stream out PV database
    the connection information, help to generate cdl base on connection infor

-tech: PnR timing analys
    PVT session
    timing influence will be settle here for different PVT


