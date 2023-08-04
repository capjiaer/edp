#################################################################################################
##                                                                                             ##
## SAMSUNG FOUNDRY RESERVES THE RIGHT TO CHANGE PRODUCTS, INFORMATION AND SPECIFICATIONS       ##
## WITHOUT NOTICE.                                                                             ##
##                                                                                             ##
## No part of this publication may be reproduced, stored in a retrieval system, or transmitted ##
## in any form or by any means, electric or mechanical, by photocopying, recording,            ##
## or otherwise, without the prior written consent of Samsung. This publication is intended    ##
## for use by designated recipients only. This publication contains confidential information   ##
## (including trade secrets) of Samsung protected by Competition Law, Trade Secrets Protection ##
## Act and other related laws, and therefore may not be, in part or in whole, directly or      ##
## indirectly publicized, distributed, photocopied or used (including in a posting on the      ##
## Internet where unspecified access is possible) by any unauthorized third party. Samsung     ##
## reserves its right to take any and all measures both in equity and law available to it and  ##
## claim full damages against any party that misappropriates Samsung's trade secrets and/or    ##
## confidential information                                                                    ##
##                                                                                             ##
## All brand names, trademarks and registered trademarks belong to their respective owners.    ##
##                                                                                             ##
## 2023 Samsung Foundry                                                                        ##
##                                                                                             ##
#################################################################################################
##                                                                                             ##
## Title                : Samsung_Foundry_LN04LPP_SFDK_PnR_Methodology_Innovus_REV1.01         ##
## Process              : LN04LPP                                                              ##
## Author               : JongHwan Park                                                        ##
## Initial Release Date : January. 31, 2023                                                    ##
## Last Update Date     : January. 31, 2023                                                    ##
## Script Version       : REV1.01                                                              ##
## Usage                : make route_opt                                                       ##
## Tool Version         : Innovus 21.15_s110_1_G or later      	  	                       ##
##                                                                                             ##
#################################################################################################

# This file should be applied before clock net route during cts.

# Redundant via
if {  $step == "route_opt" } { setNanoRouteMode -drouteUseMultiCutViaEffort low
} else { setNanoRouteMode -drouteUseMultiCutViaEffort high }

setNanoRouteMode -drouteHonorAlternativeTrackColor "M1"
setNanoRouteMode -routeBottomRoutingLayer $vars(min_route_layer)
setNanoRouteMode -routeTopRoutingLayer $vars(max_route_layer)
setNanoRouteMode -drouteExpRelaxSamenetConnection true
setNanoRouteMode -routeTieNetToShape stripe
setNanoRouteMode -droutePostRouteSpreadWire false
setNanoRouteMode -routeWithSiDriven true
# No OBS patching
#setNanoRouteMode -drouteExpNoMetalPatchOnCellObs true
setNanoRouteMode -drouteExpMaxPatchLengthOnBlockage 0.0

# For antenna drc
setNanoRouteMode -drouteFixAntenna true -routeAntennaCellName [dbGet head.libCells.name ANTENNA_DX_*$vars(INITIAL)$vars(physicalcell_vth)] -routeInsertAntennaDiode true 
