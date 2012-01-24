#!/usr/bin/env python
# This script queries the local NCBI taxonomy tree database
# for a particular species and outputs info about the hierachry
# It's mostly for testing.

LOOKUP_SPECIES = "Caulobacter crescentus"

from taxon_config import *

import sys, os
from sqlobject import *
from model import *

if USE_MYSQL:
    connection = connectionForURI("mysql://%s:%s@localhost/%s" % (mysql_user, mysql_pass, dbname))
else:
    db_filename = os.path.abspath("%s.db" % (dbname) )
    connection_string = 'sqlite:' + db_filename
    connection = connectionForURI(connection_string)

sqlhub.processConnection = connection

#species = sys.argv[1]

# Not required now that database schema has 
# ForeignKey pointers directly to parent_node's from Nodes.
#def get_parent(node):
#    """Given a Node, return the parent Node"""
#    parent_id = node.parent_tax_id
#    return list(Node.select(Node.q.tax_id==parent_id))[0]

# find the species name
records = Name.select(Name.q.name_txt==LOOKUP_SPECIES)
#print list(records)[0]
#print
# for each species with that name, find its place in the tree
for r in list(records):
    tax_id = int(r.tax_id) # tax_id associated with Name record
    node = list(Node.select(Node.q.tax_id==tax_id))[0]  # the Node bearing that (unique) tax_id
    # walk back down the nodes, following the parent_tax_id for each node
    # lookup and print names associated with those tax_id's as we go
    while node.tax_id != 1:
        #parent = get_parent(node)
        parent = node.parent_node
        names = list(Name.select(Name.q.tax_id==node.tax_id))
        allnames = ""
        for n in names:
            allnames += " | " + n.name_txt
        print "tax_id->parent_tax_id", node.tax_id, parent.tax_id
        print "Name(s): ", allnames
        print
        node = parent
