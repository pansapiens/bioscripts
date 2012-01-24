Taxon - label protein sequences based on taxonomy
=================================================

Taxon was built for one specific purpose - given a set of
protein sequences in FASTA format with headers containing the binomial name
as '[genus species]', add a small tag to the header to indicate some higher
level of classification (eg order or kingdom).

It's a little over-engineered (warning: contains a SOAP server !), and sorely 
needs some cleanup .. but I've used it and it works.

For dependencies and installation instructions, see INSTALL.

Example
-------

    $ ./taxon_client.py sequences.fasta >sequences_tagged.fasta

For example, given the sequences (sequences.fasta):

    >some_protein [Caulobacter crescentus] bla
    SDFGWSGEWE
    >some_other_protein [Saccharomyces cerevisiae] blabla
    SDGSDGSDGDSGSDGSD

Taxon can output (sequence_tagged.fasta):

    >tax|ap|some_protein [Caulobacter crescentus] bla
    SDFGWSGEWE
    >tax|fu|some_other_protein [Saccharomyces cerevisiae] blabla
    SDGSDGSDGDSGSDGSD

where the tax|xx label is added to indicate, in this case, the order or kingdom
('ap' for Alphaproteobacteria and 'fu' for Fungi)

This can be useful in various contexts. Mostly I've used it to colour groups of
sequences based on broad taxonomic groups in CLANS.

The superkingdoms/kingdoms/orders/genus detected, associated tags, should be 
configured in taxon_config.py for the users particular needs.
