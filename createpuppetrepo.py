#!/usr/bin/python

import json
from optparse import OptionParser
import os
import sys
import shutil
import tarfile
import subprocess
import re
import io


def getmodules(repopath,outpath,tag):
	modules=[]

	buildoutput=subprocess.check_output(["git","ls-tree","-rt","--full-tree",tag])
	for line in buildoutput.split("\n"):
		#print line
		m=re.search("\s+(\S*)/?metadata.json",line)
		#if m != None:
		if m != None and not re.search("pkg/",m.group(1)):
			if m.group(1)!="" and  m.group(1)[-1]=="/":
				modules.append(m.group(1)[0:-1])
			elif m.group(1)!="":
				modules.append(m.group(1))
			else:
				modules.append(".")
			
	return modules


def buildmodule(path,outpath,tag,isbare=False):

	jsonblob = subprocess.check_output(["git","cat-file","blob","%s:%s/metadata.json"%(tag,path)])
	metadata = json.loads(jsonblob)
	name = metadata['name'].replace("/","-").rsplit("-",1)

	metadata['name'] = name[1]
	metadata['author'] = name[0]

	#/modules/system/releases/a/acp/acp-profile-0.2.5.tar.gz
	outpath=outpath + "/system/releases/" + metadata['author'][0] + "/" + metadata['author']
	outfile= outpath+"/"+ metadata['author']+"-"+metadata['name']+"-"+metadata['version']+".tar.gz"

	if os.path.exists(outfile):
		print "%s already exists not rebuilding"%(outfile)
		return metadata

	print "building %s"%(outfile)
	if not os.path.isdir(outpath):
		try:
			os.makedirs(outpath)
		except Exception,e:	
			print "unable to create %s"%outpath
			sys.exit(1)
	print "created %s"%outpath

	builttgz=""
	if isbare:
		c=os.getcwd()
		os.chdir(path)
		#print ["git","archive","--format=tar.gz","--prefix=%s/"%(metadata['author']+"-"+metadata['name']),tag,"."]
		builttgz = subprocess.check_output(["git","archive","--format=tar.gz","--prefix=%s/"%(metadata['author']+"-"+metadata['name']),tag,"."])
		os.chdir(c)
	else:
		buildoutput=subprocess.check_output(["puppet","module","build",path])
		m=re.search("Module built: *(.*)$",buildoutput)
		if m == None:
			print "Something went wrong! Build output: %s"%buildoutput
			sys.exit(1)
		builttgz = open(m.group(1),"r").read()	
	
	fd = open(outfile,"w")
	fd.write(builttgz)
	fd.close()

	return metadata


parser = OptionParser()
parser.add_option("-r", "--repo", action="append", dest="repolist", help='repo containing modules (can be used multiple times)')
parser.add_option("-o", "--out", default=None, action="store", dest="outputdir", help='directory to write to')
parser.add_option("-t", "--tag", default="HEAD", action="store", dest="tag", help='tag to build (default: HEAD)')
parser.add_option("-b", "--bare", default=False, action="store_true", dest="isbare", help='no working copy in the repo')
parser.add_option("-c", "--clean", default=False, action="store_true", dest="clean", help='clean out the output directory before commencing build (requires --out)')

cwd=os.getcwd()

(opt,args) = parser.parse_args()
if opt.outputdir:
	outputpath=opt.outputdir
	if  outputpath[0]!="/":
		 outputpath=cwd+"/"+ outputpath
	if opt.clean and os.path.isdir(outputpath+"/system"):
		try:
			shutil.rmtree(outputpath+"/system")
		except Exception, e:
			print "failed to remove directory %s/system : %s"%(outputpath,e)
			sys.exit(1)
else:
	outputpath=cwd

isbare = opt.isbare

modulesfilepath = outputpath+"/modules.json"

if opt.repolist == None:
	repolist=["."]
else:
	repolist=opt.repolist

tag=opt.tag


#print modulesfilepath 
allmodules=[]

modjsonfd=open(modulesfilepath,"w")
for reponame in repolist:
	print "processing "+reponame
	if not os.path.isdir(reponame):
		print "%s not a directory"%(reponame)
		sys.exit(1)

	os.chdir(reponame)
	modlist = getmodules(reponame,outputpath,tag)

	for i in modlist:
		allmodules.append(buildmodule(i,outputpath,tag,isbare))
		
	os.chdir(cwd)

modjsonfd=open(modulesfilepath,"w")
modjsonfd.write(json.dumps(allmodules))

