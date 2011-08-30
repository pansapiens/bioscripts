#!/usr/bin/env python
# clans2json.py
# Copyright Andrew Perry, 2011.
#
# Converts export files from CLANS to JSON,
# suitable for use with d3.js force directed
# graph plotting (http://mbostock.github.com/d3/ex/force.html).
# Input files are the CLANS output from 
# "Save blast matrix pP-values" and "Save 2d graph data"
#

import sys, json
from clans2svg import parse_clans_edgefile, parse_clans_nodefile

if __name__ == "__main__":

  USAGE = """clans2json.py

  Converts export files from CLANS to JSON,
  suitable for use with d3.js force directed
  graph plotting (http://mbostock.github.com/d3/ex/force.html).

  Input files are the CLANS output from 
  "Save blast matrix pP-values" and "Save 2d graph data"

  Dependencies: 
     CLANS       : http://bioinfoserver.rsbs.anu.edu.au/programs/clans/
     SVGFig (2.x): http://code.google.com/p/svgfig/

  Usage:
  $ ./clans2json.py example.blast example.graph >graph.json
  """

  with open(sys.argv[1], 'r') as f:
    edges, groups = parse_clans_edgefile(f)

  with open(sys.argv[2], 'r') as f:
    nodes = parse_clans_nodefile(f)

  #print edges
  #print groups

  # node id to group id
  nid2gid = {}
  gid2group = {}
  gid = 0
  for gname in groups:
    g = groups[gname]
    gid2group[gid] = gname
    for n in nodes:
      if n[0] in g["numbers"]:
        nid2gid[n[0]] = gid
    gid += 1

  #print nid2gid

  jdict = {"nodes":[]}
  for n in nodes:
    jdict["nodes"].append({"name":n[1],"group":nid2gid[n[0]]})

  jdict["links"] = []
  for e in edges:
    jdict["links"].append({"source":e[0],"target":e[1],"value":e[2]})

  print json.dumps(jdict)