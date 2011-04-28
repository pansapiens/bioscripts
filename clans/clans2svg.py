#!/usr/bin/env python
# clans2svg.py
# Copyright Andrew Perry, 2011.
#
# Converts export files from CLANS to SVG
# Input files are the CLANS output from 
# "Save blast matrix pP-values" and "Save 2d graph data"

# Node size, edge thickness can be tweaked (see variables at
# the top of the script).
#
# The SVG output contains groups that correspond to the groups
# defined in CLANS. For convenience, nodes also carry a 'name' 
# attribute that matches the name (FASTA header) from CLANS.
# (This can be turned off using the INCLUDE_SEQNAME_IN_SVG
# variable if it somehow causes havoc with the XML due to
# lack of escaping disallowed characters).
#
# Dependencies: 
#    CLANS       : http://bioinfoserver.rsbs.anu.edu.au/programs/clans/
#    SVGFig (2.x): http://code.google.com/p/svgfig/
#
# Usage:
# $ ./clans2svg.py example.blast example.graph >graph.svg
# $ inkscape graph.svg

SCALE=100
NODE_SIZE=0.8
EDGE_THICKNESS=0.1
UNGROUPED_COLOR="rgb(128,128,128)"
# set this to false if your FASTA headers 
# are somehow breaking the SVG output
INCLUDE_SEQNAME_IN_SVG = True


#########################################################################

import sys
try:
  from svgfig.interactive import *
except:
  print "ERROR: clans2svg.py requires SVGFig 2.x ( http://code.google.com/p/svgfig/ )"

USAGE = """clans2svg.py

Converts export files from CLANS to SVG
Input files are the CLANS output from 
"Save blast matrix pP-values" and "Save 2d graph data"

Dependencies: 
   CLANS       : http://bioinfoserver.rsbs.anu.edu.au/programs/clans/
   SVGFig (2.x): http://code.google.com/p/svgfig/

Usage:
$ ./clans2svg.py example.blast example.graph >graph.svg
$ inkscape graph.svg
"""

nodes = [] # id, name, x, y
edges = [] # a, b, weight

def getNodeXY(id):
  """
  Retrieve the x,y tuple for a node by integer id.
  """
  for n in nodes:
    if n[0] == id:
      return (n[2], n[3])

#####################################
# read edge file
# from "Save blast matrix pP-values"
#####################################
seqgroups = {}
curr_seqgroup = None
section = None
try:
  f = open(sys.argv[1], 'r')
except IndexError:
  print USAGE
  sys.exit()

for l in f:
  if l.strip() == "<att>":
    section = "att"
    continue
  if l.strip() == "</att>":
    section = None
    continue
  if l.strip() == "<seqgroups>":
    section = "seqgroups"
    continue
  if l.strip() == "</seqgroups>":
    section = None
    continue

  if section == "att":
    ns, weight = l.split(":")
    a, b = ns.split()
    #e = Edge(int(a), int(b), float(weight))
    #edges.append(e)
    edges.append([int(a), int(b), float(weight)])

  if section == "seqgroups":
    k, v = l.strip().split("=")
    if k == "name":
      curr_seqgroup = v.strip()
      seqgroups[curr_seqgroup] = {}
      continue
    else:
      vs = v.strip().split(";")
      if vs[-1:][0] == "":
        vs = vs[:-1]
      vs_int = map(int, vs)
      seqgroups[curr_seqgroup][k] = vs_int

f.close()

# sort edges by weight so that the darker ones get drawn last
def sortedge(a,b):
  if a[2] > b[2]:
    return 1
  if a[2] < b[2]:
    return -1
  if a[2] == b[2]:
    return 0

edges.sort(cmp=sortedge)

#print edges
#print seqgroups

###########################
# read node position file
# from "Save 2d graph data"
###########################
try:
  f = open(sys.argv[2], 'r')
except IndexError:
  print USAGE
  sys.exit()
f.readline() # skip header line
for l in f:
  id, name, x, y = l.split("\t")
  nodes.append([int(id), name, float(x), float(y)])

f.close()

#print nodes

##################
# setup SVG object
svg = SVG("g", id="CLANS")
nodes_svg = SVG("g", id="nodes", fill_opacity="50%")

#################
# draw the nodes
nodegroups = {}
for n in nodes:
  groupname = ""
  color = UNGROUPED_COLOR 
  # get colors for nodes defined in CLANS groups
  for g in seqgroups:
    if n[0] in seqgroups[g]["numbers"]:
      clr = seqgroups[g]["color"]
      color = "rgb(%i,%i,%i)" % (clr[0], clr[1], clr[2])
      groupname = g

  if INCLUDE_SEQNAME_IN_SVG:
    c = SVG("circle", id="node:"+`n[0]`, name=n[1], cx=n[2]*SCALE, \
             cy=n[3]*SCALE, r=NODE_SIZE, fill=color, stroke=None)
  else:
    c = SVG("circle", id="node:"+`n[0]`, cx=n[2]*SCALE, cy=n[3]*SCALE, \
             r=NODE_SIZE, fill=color, stroke=None)
  #nodes_svg.append(c)
  if groupname not in nodegroups:
    nodegroups[groupname] = SVG("g", id=groupname, fill_opacity="50%")
  nodegroups[groupname].append(c)

for ng in nodegroups.values():
  nodes_svg.append(ng)

##################
# draw the edges
edges_svg = SVG("g", id="edges")
for e in edges:
  x1, y1 = getNodeXY(e[0])
  x2, y2 = getNodeXY(e[1])
  #grey_value = (1.0-e[2])*256
  grey_value = (0.8-e[2])*256
  color = "rgb(%i,%i,%i)" % (grey_value, grey_value, grey_value)
  l = SVG("line", id="edge:%i-%i"%(e[0],e[1]), x1=x1*SCALE, \
           y1=y1*SCALE, x2=x2*SCALE, y2=y2*SCALE,\
           stroke=color, fill=None, \
           style={"stroke-linejoin": "round", "stroke-width": EDGE_THICKNESS})
  edges_svg.append(l)

##################
# output svg
svg.append(edges_svg)
svg.append(nodes_svg)
print svg.xml()
#svg.inkscape()
