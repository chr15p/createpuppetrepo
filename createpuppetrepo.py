#!/usr/bin/python

import json
from optparse import OptionParser
import os
import sys
#import shutil
import tarfile
import subprocess
import re
import io


def getmodules(repopath,outpath,tag):
	modules=[]

	os.chdir(repopath)
	buildoutput=subprocess.check_output(["git","ls-tree","-rt","--full-tree",tag])
	for line in buildoutput.split("\n"):
		m=re.search("\s+(\S+)/metadata.json",line)
		if m != None and not re.search("\/pkg\/",m.group(1)):
			print m.group(1)
			#modules.append(self.buildmodule(m.group(1),outpath,tag))
			modules.append(m.group(1))

	return modules


def buildmodule(path,outpath,tag):
	builttgz = subprocess.check_output(["git","archive","--format=tar.gz",tag,path])

	io_bytes = io.BytesIO(builttgz)
	tar = tarfile.open(fileobj=io_bytes, mode='r:gz')
	jsonfd = tar.extractfile(path+"/metadata.json")
	metadata = json.loads(jsonfd.read())

	name = metadata['name'].replace("/","-").rsplit("-",1)

	metadata['name'] = name[1]
	metadata['author'] = name[0]

	tar.close()

#/modules/system/releases/a/acp/acp-profile-0.2.5.tar.gz

	outpath=outpath+"/system/releases/"+metadata['author'][0]+"/"+ metadata['author']+"/"+ metadata['author']+"-"+metadata['name']+"-"+metadata['version']+".tar.gz"
	fd = open(outpath,"w")
	fd.write(builttgz)
	fd.close()
	#git archive --format=tar.gz HEAD | (cd /root/tmp && tar xf -)
	# git ls-tree -rt testbranch 

	return metadata


parser = OptionParser()
parser.add_option("-r", "--repo", action="append", dest="repolist", help='repo containing modules')
parser.add_option("-o", "--out", default=None, action="store", dest="outputdir", help='directory to write to')
parser.add_option("-t", "--tag", default="HEAD", action="store", dest="tag", help='tag to build')
#parser.add_option("-p", "--pull", default=None, action="store", dest="pull", help='if given pull to the given directory before building.')

(opt,args) = parser.parse_args()
if opt.outputdir:
	outputpath=opt.outputdir
else:
	outputpath="."

modulesfilepath=outputpath+"/modules.json"

if opt.repolist== None:
	repolist=["."]
else:
	repolist=opt.repolist

tag=opt.tag


#print modulesfilepath 
allmodules=[]

modjsonfd=open(modulesfilepath,"w")

for reponame in repolist:
	if not os.path.isdir(reponame):
		print "%s not a directory"%(reponame)
		sys.exit(1)

	modlist = getmodules(reponame,outputpath,tag)

	for i in modlist:
		allmodules.append(buildmodule(i,outputpath,tag))
		

	#n = r.clone()
	#for i in n.getModules()
	#	n.build()
	#	n.copyBuiltModule(outputpath)
	#	modjsonfd.write(json.dumps(n.module))


modjsonfd=open(modulesfilepath,"w")
modjsonfd.write(json.dumps(allmodules))

