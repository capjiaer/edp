#! /usr/bin/python3.9
############################################################
# File Name: libs_generation.py
# Author: anping.chen
# Email: anping.chen@joinsilicon.com
# Created Time: Tue 28 Feb 2023 02:22:47 PM CST
############################################################
import sys, argparse, os, json, time, datetime, yaml
from yaml.loader import SafeLoader, FullLoader
sys.path.append("/home/chenanping/module/python_module")
from jed_module import jedp

