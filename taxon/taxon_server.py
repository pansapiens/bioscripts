#!/usr/bin/env python

from taxon_config import *

__DEBUG__ = False

import sys, os
from sqlobject import *

if USE_ZSI:
    from ZSI import dispatch
else:
    import SOAPpy

if USE_MYSQL:
    connection = connectionForURI("mysql://%s:%s@localhost/%s" % (mysql_user, mysql_pass, dbname))
else:
    db_filename = os.path.abspath("%s.db" % (dbname) )
    connection_string = 'sqlite:' + db_filename
    connection = connectionForURI(connection_string)

sqlhub.processConnection = connection

class Node(SQLObject):
    tax_id = IntCol(alternateID=True)
    parent_tax_id = IntCol()            # a little redundant if we have parent node ForeignKey
    parent_node = ForeignKey("Node")
    rank = StringCol()
    embl_code = StringCol()
    division_id = IntCol()
    inherited_div_flag = BoolCol()
    genetic_code_id = IntCol()
    inherited_GC_flag = BoolCol()
    mitochondrial_genetic_code_id = IntCol()
    inherited_MGC_flag = BoolCol()
    GenBank_hidden_flag = BoolCol()
    hidden_subtree_root_flag = BoolCol()
    comments = StringCol()
    name = MultipleJoin("Name")

class Name(SQLObject):
    tax_id = IntCol()                   # a little redundant if we have the node ForeignKey
    #tax_id = ForeignKey("Node")
    name_txt = StringCol()
    unique_name = StringCol()
    name_class = StringCol()
    node = ForeignKey("Node")

def getLineage(species_name):
    """Takes a speices name and searches the taxonomy database for any
       substring matches. Returns all 'lineages' as a dictionary of lists of lists.
       
       eg. {'Saccharomyces cerevisiae': [['Candida robusta', 'Saccaromyces cerevisiae', 'Saccharomyces capensis', 'Saccharomyces cerevisiae', 'Saccharomyces italicus', 'Saccharomyces oviformis', 'Saccharomyces uvarum var. melibiosus', 'Saccharomyes cerevisiae', 'Sccharomyces cerevisiae', "baker's yeast", "brewer's yeast", 'lager beer yeast', 'yeast'], ['Pachytichospora', 'Saccharomyces'], ['Eremotheciaceae', 'Saccharomycetaceae'], ['Endomycetales', 'Saccharomycetales', 'budding yeasts'], ['Hemiascomycetes', 'Saccharomycetes'], ['Saccharomycotina'], ['Ascomycota', 'ascomycetes', 'ascomycetes', 'sac fungi'], ['Dikarya'], ['Fungi', 'fungi', 'fungi'], ['Fungi/Metazoa group'], ['Eucarya', 'Eucaryotae', 'Eukarya', 'Eukaryota', 'Eukaryotae', 'eucaryotes', 'eukaryotes', 'eukaryotes'], ['biota', 'cellular organisms']]}

    This is because a species name query may give multiple results (the dictionary), 
    and when walking back to the root (the first list) along a each node can have 
    multiple names (the second dimension of the list).
    """
    # find the species name
    records = Name.select(Name.q.name_txt==species_name)
    #print list(records)[0]
    #print
    # for each species with that name, find its place in the tree
    lineages = {}
    for r in list(records):
        tax_id = int(r.tax_id) # tax_id associated with Name record
        node = list(Node.select(Node.q.tax_id==tax_id))[0]  # the Node bearing that (unique) tax_id
        # walk back down the nodes, following the parent_tax_id for each node
        # lookup and print names associated with those tax_id's as we go
        lineage = []
        while node.tax_id != 1:
            #parent = get_parent(node)
            parent = node.parent_node
            names = list(Name.select(Name.q.tax_id==node.tax_id))
            alternate_names = []
            for n in names:
                alternate_names.append(n.name_txt)
            #print "tax_id->parent_tax_id", node.tax_id, parent.tax_id
            #print "Name(s): ", lineage
            #print
            lineage.append(alternate_names)
            node = parent
        lineages[r.name_txt] = lineage
    if __DEBUG__: sys.stderr.write(`lineages` + "\n")
    return lineages

def structType2dict(struct):
    """Converts a SOAPpy structType object to a Python dictionary"""
    return dict((key, getattr(struct, key)) for key in struct._keys())

def getLineageCode(species, kingdoms=KINGDOMS):
    kingdoms = structType2dict(kingdoms)
    lineage = getLineage(species)
    try:
        first_species = lineage.keys()[0]
    except IndexError:
        return None
    for l in lineage[first_species]: # we only do the first species in the lineage results
        for n in l:
            if n in kingdoms:
                return kingdoms[n]
    return None

if USE_ZSI:
    # if using ZSI instead of SOAPpy
    dispatch.AsServer(port=8999)
else:
    server = SOAPpy.SOAPServer(("localhost", 8999))
    server.registerFunction(getLineageCode)
    server.serve_forever()

