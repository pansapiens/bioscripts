from sqlobject import *

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
