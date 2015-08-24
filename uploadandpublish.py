#!/usr/bin/python

import json
import sys

from optparse import OptionParser
import requests

# URL to your Satellite 6 server
URL = "https://sat6.chrisprocter.co.uk"
# URL for the API to your deployed Satellite 6 server
SAT_API = "%s/katello/api/v2/" % URL
# Katello-specific API
KATELLO_API = "%s/katello/api/" % URL
POST_HEADERS = {'content-type': 'application/json'}
# Default credentials to login to Satellite 6
USERNAME = "admin"
PASSWORD = "password"
# Ignore SSL for now
SSL_VERIFY = False

# Name of the organization to be either created or used
ORG_NAME = "chrisprocter.co.uk"
# Name for lifecycle environments to be either created or used
ENVIRONMENTS = ["Development", "Testing", "Production"]


def get_json(location):
    """
    Performs a GET using the passed URL location
    """
    print "==" + str(location)
    r = requests.get(location, auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
    return r.json()


def post_json(location, json_data):
    """
    Performs a POST and passes the data to the URL location
    """

    result = requests.post(
        location,
        data=json_data,
        auth=(USERNAME, PASSWORD),
        verify=SSL_VERIFY,
        headers=POST_HEADERS)

    return result.json()


#def getresults(url,):



parser = OptionParser()
parser.add_option("-p", "--product", action="append", dest="product", help='product')
parser.add_option("-c", "--cv", default=None, action="store", dest="cv", help='content view')
(opt,args) = parser.parse_args()

org = get_json(SAT_API + "/organizations/?name=%s"%ORG_NAME)
if org.get('error', None):
    print "organization %s not known"%ORG_NAME
    sys.exit(1)

org_id = org['results'][0]['id']
print org_id
#else:
#    # Our organization exists, so let's grab it
#    for i in org['results']:
#        if i['name'] == ORG_NAME:
#            org_id = i['id']


for p in opt.product:
	product = get_json("%s/katello/api/v2/organizations/%s/products?name=%s"%(URL,org_id,p))
	if product.get('error', None):
		print "product %s not known"%p
		sys.exit(1)
	product_id=product['results'][0]['id']
	print product_id

print post_json("%s/katello/api/v2/products/%s/sync"%(URL,product_id),'{}')

#####################
#modules = get_json(SAT_API + "/puppet_modules")
#for m in modules['results']:
#	m['author']+"-"+m['name']
#	for r in m['repositories']:
#		productid=r['product']['id']
#
#################
# Now, let's fetch all available content views for this org...
cvs = get_json(SAT_API + "/organizations/%s/content_views/?name=%s"%(org_id,opt.cv))
if cvs.get('error', None):
    print "content view %s not known"%opt.cv
    sys.exit(1)
cv_id=cvs['results'][0]['id']
puppetmods=cvs['results'][0]['puppet_modules']
print cv_id

print post_json(URL+"/katello/api/v2/content_views/%s/publish"%cv_id,None)

sys.exit(0)
#sys.exit(0)
#GET URL+/katello/api/v2/organizations/:organization_id/products
#POST /katello/api/v2/products/:id/sync
#post_json(URL+"/katello/api/v2/content_views/"+str(cvid)+"/publish",None)

