#!/usr/bin/env python
# Look up the kingdom / superphylum of sequences in a FASTA file and re-output the FASTA database
# appending |||kk to the sequence description (where kk is the kingdom code defined in the KINGDOMS dictionary). Species searched is taken from whatever is between the first set of [] brackets in the sequence description (ie BLAST hit format, like [Homo sapiens])

# Requires the taxonomy database to be populated using "create_taxonomy_db.py", and the
# taxon_server.py SOAP server running to interegate the taxonomy database.

from taxon_config import *

import sys
from Bio import SeqIO
if USE_ZSI:
    from ZSI.client import Binding
else:
    import SOAPpy

fh = open(sys.argv[1], 'rU')
seqs = SeqIO.parse(fh, "fasta")

if USE_ZSI:
    server = Binding(url='', host='localhost', port=8999)
else:
    server = SOAPpy.SOAPProxy("http://localhost:8999/")

#def get_lineage_code(species, kingdoms=KINGDOMS):
#    lineage = server.getLineage(species)
#    for l in lineage:
#        for n in l:
#            #print "----------------"
#            for x in n:
#                if x in kingdoms:
#                    return kingdoms[x]
#    return None

for s in seqs:
    try:
        species = s.description.split("[")[1].split("]")[0].strip()
    except IndexError: # no [genus species] in the description for this sequence
        continue
    #print "Species: ", species
    lineage_code = server.getLineageCode(species, kingdoms=KINGDOMS)
    if lineage_code == None:
        lineage_code = server.getLineageCode(species, kingdoms=SUPERKINGDOMS)
    if tag_end:
      print ">%s |||%s" % (s.description, lineage_code)
    else:
      print ">tax|%s|%s" % (lineage_code, s.description)
    print s.seq.tostring()

fh.close()

