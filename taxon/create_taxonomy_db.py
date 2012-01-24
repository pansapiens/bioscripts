#!/usr/bin/env python
# Import nodes.dmp and names.dmp files from NCBI taxonomy 
# into a database using SQLObject (MySQL or SQLite)
# Andrew Perry, 2007

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

# work with SQLite DB in memory
#sqlhub.processConnection = connectionForURI('sqlite:/:memory:')

try:
    Node.createTable()
except: #dberrors.OperationalError:
    raise

try:
    Name.createTable()
except: #dberrors.OperationalError:
    raise

###
# import nodes.dmp
###

dbnodes_file = open(DB_NODES, 'r')

#db_nodes = {}
for l in dbnodes_file:
    tax_id, parent_tax_id, rank, embl_code, \
    division_id, inherited_div_flag, genetic_code_id, \
    inherited_GC_flag, mitochondrial_genetic_code_id, \
    inherited_MGC_flag, GenBank_hidden_flag, \
    hidden_subtree_root_flag, comments = l.split("\t|\t")
    comments = comments[:-3]
    #db_nodes[tax_id] = (parent_tax_id, rank, embl_code, \
    #                    division_id, inherited_div_flag, genetic_code_id, \
    #                    inherited_GC_flag, mitochondrial_genetic_code_id, \
    #                    inherited_MGC_flag, GenBank_hidden_flag, \
    #                    hidden_subtree_root_flag, comments)
    Node(tax_id=int(tax_id), \
         parent_tax_id=int(parent_tax_id), \
         parent_node=None,\
         rank=rank, \
         embl_code=embl_code, \
         division_id=int(division_id), \
         inherited_div_flag=int(inherited_div_flag), \
         genetic_code_id=int(genetic_code_id), \
         inherited_GC_flag=int(inherited_GC_flag), \
         mitochondrial_genetic_code_id=int(mitochondrial_genetic_code_id), \
         inherited_MGC_flag=int(inherited_MGC_flag), \
         GenBank_hidden_flag=int(GenBank_hidden_flag), \
         hidden_subtree_root_flag=int(hidden_subtree_root_flag), \
         comments=comments)

dbnodes_file.close()

###
# import names.dmp
###
dbnames_file = open(DB_NAMES, 'r')

#db_names = {}
for l in dbnames_file:
    tax_id, name_txt, unique_name, name_class = l.split("\t|\t")
    tax_id = int(tax_id)
    name_class = name_class[:-3] # removes "\t|\n"
    #print "%s | %s | %s | %s" % (tax_id, name_txt, unique_name, name_class)
    #db_names[name_txt] = (tax_id, unique_name, name_class)
    # find the Node record (by unique tax_id) to associate with this Name record
    node = list(Node.select(Node.q.tax_id==tax_id))[0]
    Name(tax_id=tax_id, name_txt=name_txt, unique_name=unique_name, name_class=name_class, node=node)
    #print "Added:", tax_id, name_txt, unique_name, name_class

dbnames_file.close()

# Now go back and update all the parent_node links in the Node records ?
# in theory (based on SQLObject docs) the  Node.select() iterator
# should be fetching records one-by-one .. memory utilisation and lag time
# clearly indicates it isn't.
for n in Node.select():
    parent_id = n.parent_tax_id
    parent = list(Node.select(Node.q.tax_id==parent_id))[0]
    n.parent_node = parent

#print db_names["Caulobacter crescentus"]
#print Name.select(Name.q.name_txt=="Caulobacter crescentus")
