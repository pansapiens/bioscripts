#!/usr/bin/python
# Copyright 2008-2010 by Andrew Perry. All rights reserved.
# This code is released under the Biopython License.
# Please see the LICENSE file that should have been included
# as part of this package.
# 
# This script runs MEMSAT3 
# (http://bioinf.cs.ucl.ac.uk/software_downloads/memsat/) 
# over a FASTA format database of sequences.
# It outputs a series of fasta-like files (one for each sequence) into
# a directory 'memsat_out', containing the predicted transmembrane 
# regions and topology. Also outputs a summary of sequence ids and 
# number of transmembranes to stderr (either as CSV or a TMHMM-like 
# output). Can optionally choose to not output proteins predicted 
# to be cytosolic proteins.

# This script was used in the analysis for the publication:
#  "Jedelský PL, Doležal P, Rada P, Pyrih J, Šmíd O, et al. (2011) 
#   The Minimal Proteome in the Reduced Mitochondrion of the Parasitic 
#   Protist Giardia intestinalis. PLoS ONE 6: e17285."
#   ( http://dx.plos.org/10.1371/journal.pone.0017285 )

#
## Dependancies:
#   * MEMSAT3 (http://bioinf.cs.ucl.ac.uk/software_downloads/memsat/)
#     (MEMSAT3 requires PSIBLAST and an installed BLAST database
#      [default is 'swiss'] for decent performance.
#      Tip: read & edit the 'runmemsat' script. It uses tcsh.)
#   * Biopython (http://biopython.org, for Bio.SeqIO.FASTA).
#       Tip: tested with version 1.57
#
## Installation:
#  You should change the memsat_bin variable below to point to
#  the 'runmemsat' script in your MEMSAT3 installation.
#  Also set the outdir, emulate_tmhmm_output and 
#  include_cytosolic variables as desired.
#
## Run like:
#   $ ./memsat3.py test.fasta 2>test_results.tsv

################################################################
# configuration & options                                      #

memsat_bin = "/home/perry/programs/memsat3/runmemsat"
outdir = "memsat_out"

# make output look a bit like TMHMM short output
emulate_tmhmm_output = False

# also output info for proteins predicted to be cytosolic
include_cytosolic = True

################################################################
# end configuration area - probably no need to edit below here #
import sys, os, re
from Bio import SeqIO

def parse_memsat3(f):
    """
    Parses the output of the MEMSAT3 transmembrane region 
    prediction program.
    Accepts an open file object, returns a tuple: 
      (sequence, tm_pred, tm_scores, num_tms).
  
    Where sequence is the input amino acid sequence, tm_pred
    is the transmembrane prediction per residue in the format
    used by MEMSAT3, tm_scores is a list of score for each 
    transmembrane region (N- to C-) and num_tms is the number
    of predicted transmembrane segements in this sequence.

    (Only information from the 'FINAL PREDICTION' is extracted
    not the detailed scoring, which is rarely of interest)
    """
    while 1:
        l = f.readline()
        if l == "FINAL PREDICTION\n":
            num_tms = 0
            f.readline()
            l = f.readline()
            s = l.split(":")
            tm_scores = []
            # read the final prediction scores
            while re.match("\d", l[0]):
                tm_scores.append( s[1].replace("\t", " ").replace("\n", " ") )
                l = f.readline()
                s = l.split(":")
                num_tms += 1
            f.readline() 
            tm_pred = ""
            seq = ""
            while l != "":
                tm_pred = tm_pred + f.readline()[:-1]
                seq = seq + f.readline()[:-1]
                l = f.readline()
                l = f.readline()
            return (seq, tm_pred, tm_scores, num_tms)
        elif l == "0 residues read from file.\n":
            return (None, None, None, None)

if __name__ == "__main__":
    # we need the directory memsat_out .. if it doesn't exist, create it
    try:
        os.stat(outdir)
    except OSError:
        print "!!!! Couldn't find %s directory. Creating it." % (outdir)
        os.mkdir(outdir)

    f = open(sys.argv[1], 'r')
    iter = SeqIO.parse(f, "fasta")
    # iterate over fasta records
    rec = iter.next()
    while rec != None:
        seq = rec.seq.tostring()
        id = rec.id
        
        tmpseqfile = open("tmpseq.fasta", 'w')
        tmpseqfile.write(">"+id+"\n")
        tmpseqfile.write(seq)
        tmpseqfile.close()
       
        # run memsat3, watching for errors 
        print "#### Running memstat3 on: ", id
        i, o, e = os.popen3("nice " + memsat_bin + " tmpseq.fasta")
        for message in o:
            if message.find("FATAL ERROR") != (-1):
                print "### MEMSAT STDOUT: ", message
                print "!!!! MEMSAT Error, skipping: ", id
                rec = iter.next()
                continue
            print "### MEMSAT STDOUT: ", message[:-1]
            #elif message == "":
            #   break
       
        # parse tmpseq.globmem to determine if cytosolic or membrane first
        globmem = open("tmpseq.globmem", 'r')
        for l in globmem:
            if l.find("residues predicted to be in TM segments") != -1:
                num_res_in_tms = int(l.split()[0])
            if l.find("**** Your protein is probably not a transmembrane protein ****") != -1:
                membrane_protein = False
            else:
                membrane_protein = True
        globmem.close()
 
        # parse the memsat3 output 
        memsat_file = open("tmpseq.memsat", 'r')
        memsat_result = parse_memsat3(memsat_file)
        memsat_file.close()
        if memsat_result == (None, None, None):
            print "!!!! MEMSAT PARSING Error, skipping: ", id
            rec = iter.next()
            continue
       
        # write a new 'fasta'-style file with results
        outfile = open(outdir+"/" + id + ".fasta", 'w')
        outfile.write(">"+id+"\n")
        outfile.write(memsat_result[0]+"\n")
        outfile.write(">"+id+" | MEMSAT3 | " + "|".join(memsat_result[2]) + "\n")
        outfile.write(memsat_result[1]+"\n")
        outfile.close()
        
        print "#### done"
        num_tms = memsat_result[3]
        
        # flag proteins predicted to be non-membrane with #
        if not membrane_protein:
            not_memb_flag = "#"
        else:
            not_memb_flag = ""
        # TMHMM short style output
        if emulate_tmhmm_output: 
            sys.stderr.write("%s%s\tlen=%i\tExpAA= \tPredHel=%i\tFirst60= \tTopology= \n" % \
                             (not_memb_flag, \
                              id, \
                              len(seq), \
                              num_tms))
        else:
        # regular CSV output
        # id, num_tms, not a membrane protein ?
            if membrane_protein:
                sys.stderr.write("%s\t%i\t%s\n" % (id, num_tms, not_memb_flag))
            elif include_cytosolic: # and not membrane_protein
                num_tms = 0
                sys.stderr.write("%s\t%i\t%s\n" % (id, num_tms, not_memb_flag))
    
        try:
          rec = iter.next()
        except StopIteration:
          break
        
f.close()
