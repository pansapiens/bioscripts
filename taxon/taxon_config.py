# Taxon client/server config
# Edit the variables below as required
#
DB_NAMES = "/data/databases/taxonomy/names.dmp"
DB_NODES = "/data/databases/taxonomy/nodes.dmp"
USE_MYSQL = True #if False, use SQLite (slow)
USE_ZSI = False

# if False, we use the Uniprot webservice instead
USE_BIOPYTHON_SPROT_PARSER = False # sometimes it breaks

dbname = "taxonomy"
mysql_user = "taxonomy"
mysql_pass = "super_secret_password"

# Do we tag the end of the FASTA header like |||xx ?
# False means tag the start like >tax|xx|gi|nnnnnnn
tag_end = False

# These are not real 'superkingdoms' or 'kingdoms' just the names I am using.
# Essentially we look for a KINGDOMs match first and if there is None we 
# fall back to matching against the SUPERKINGDOMs
SUPERKINGDOMS = {"Bacteria": "ba" }

# this dictionary specifies a tag which will be added for 
# any particular species/genus/order/etc name listed here
KINGDOMS = {"Alphaproteobacteria": "ap", \
            "Betaproteobacteria": "bp", \
            "delta/epsilon subdivisions": "dp", \
            "Gammaproteobacteria": "gp", \
            "Firmicutes": "fi", \
            "Cyanobacteria":"cy", \
            "Metazoa":"me",\
            "Kinetoplastida": "ki",\
            "green plants": "pl",\
            "Archaea": "ar",\
            "Alveolata": "al",\
            "Mycetozoa": "my",\
            "Cercozoa": "ce",\
            "Diplomonadida group": "di",\
            "stramenopiles": "st",\
            "Plasmodiophorida": "pp",\
            "marine metagenome": "mm",\
            "Fungi":"fu"}

