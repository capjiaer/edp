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

# For M1 SADP, M1_PWR should be assigned to MASK 2
if { $vars(TRACK) == "6P25TR" } {
   add_tracks \
   -pitches { M2 vert 0.036 M2 horiz 0.036 \
   	      F4 vert 0.045 F4 horiz 0.045 } \
   -offsets { M2 vert 0.000 M2 horiz 0.000 \
   	      F4 vert 0.000 F4 horiz 0.000 } \
   -width_pitch_pattern { M1 offset 0 width 0.046 pitch 0.044 { width 0.014 pitch 0.028 repeat 4 } width 0.014 pitch 0.044 } \
   -mask_pattern { M1 2 1 2 1 2 1 }

} elseif { $vars(TRACK) == "7P94TR" } {
   add_tracks \
   -pitches { M2 vert 0.040 M2 horiz 0.040 \
   	      F4 vert 0.045 F4 horiz 0.045 } \
   -offsets { M2 vert 0.000 M2 horiz 0.000 \
   	      F4 vert 0.000 F4 horiz 0.000 } \
   -width_pitch_pattern { M1 offset 0 width 0.058 pitch 0.055 { width 0.020 pitch 0.036 repeat 4 } width 0.020 pitch 0.055 } \
   -mask_pattern { M1 2 1 2 1 2 1 }
}
