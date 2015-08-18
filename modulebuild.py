#!/usr/bin/python

import json
from optparse import OptionParser
import os
import sys
import shutil
import subprocess
import re

parser = OptionParser()
parser.add_option("-d", "--dir", action="append", dest="dirlist", help='directories containing modules')
parser.add_option("-o", "--out", default=None, action="store", dest="outputdir", help='directory to write to')

(opt,args) = parser.parse_args()
if opt.outputdir:
	outputpath=opt.outputdir
else:
	outputpath="."

modulesfilepath=outputpath+"/modules.json"

if opt.dirlist==[]:
	dirlist=["."]
else:
	dirlist=opt.dirlist


#print modulesfilepath 
modules=[]

for dirname in opt.dirlist:
	if not os.path.isdir(dirname):
		print "%s not a directory"%(dirname)
		sys.exit(1)

	for obj in os.listdir(dirname):
		if obj[0]=="." or not os.path.isdir(dirname+"/"+obj):
			continue
		
		modulepath=dirname+"/"+obj
		metadatapath=modulepath+"/metadata.json"
		if not os.path.isfile(metadatapath):
			print "no manifest.json file found in %s"%modulepath	
			continue
		jsondata = open(metadatapath,"r").read()
		#print jsondata
		j=json.loads(jsondata)
		name=j['name'].replace("/","-").rsplit("-",1)
		modules.append(j)
		modules[-1]['name']=name[1]
		modules[-1]['author']=name[0]
	
		buildoutput=subprocess.check_output(["puppet","module","build",modulepath])
		m=re.search("Module built: *(.*)$",buildoutput)
		if m == None:
			print "Something went wrong! Build output: %s"%buildoutput
			next
		
		shutil.copy2(m.group(1),outputpath)

modjsonfd=open(modulesfilepath,"w")
modjsonfd.write(json.dumps(modules))
