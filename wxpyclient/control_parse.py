""" Functions for parsing control dictionaries and lists"""
import types
import shelve
import master_config_parse


def find_unique(seq):
    """find the unique elements in a list
    >>> find_unique(['cats', 'cats', 'cat', 'dogs', 'cat'])
    ['cats', 'cat', 'dogs']
    """
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen.add(x)]


def print_treedict(tree, depth = 0):
    if tree == None or len(tree) == 0:
        print "\t" * depth, "-"
    else:
        try:
            for key, val in tree.iteritems():
                print "\t" * depth + "-->", key
                print_treedict(val, depth + 1)
        except AttributeError:
            try:
                for val in tree:
                    print "\t" * depth, val
            except:
                print "\t" * depth, tree

class ControlSpec(object):
    r"""Handle the control specification db"""
    def __init__(self, configaddr):
        self.configaddr = configaddr
        self.configdb = master_config_parse.load_json_over_http(configaddr)
        self.build_system_tree()
        print_treedict(self.system_tree)

    def build_system_tree(self):
        r"""construct the dictionary of systems, subsystems, commands"""
        self.system_tree = {}
        treetitle = "System tree specified in: " + self.configaddr
        print treetitle + "\n" + "-" * len(treetitle)

        for key, conf_entry in self.configdb.iteritems():
            if 'system' in conf_entry:
                try:
                    sysname = conf_entry['system']
                    subsysname = conf_entry['category']
                except KeyError:
                    print "%s had not system/subsys" % key
                    continue

                if sysname not in self.system_tree:
                    self.system_tree[sysname] = {}

                if subsysname not in self.system_tree[sysname]:
                    self.system_tree[sysname][subsysname] = []

                if key not in self.system_tree[sysname][subsysname]:
                    if key not in self.system_tree[sysname][subsysname]:
                        self.system_tree[sysname][subsysname].append(key)
                    else:
                        print "duplicate key: %s" % key

    def system_list(self):
        return self.system_tree.keys()

    def find_groups(self, grpname="system"):
        """
        find list of unique system groups in the command db
        `dbinput` the dictionary or shelve object for the command db
        `grpname` a string for the keyname for the grouping
        return a list object of the group names

        example:
        find_groups(db, 'system')
        will return a list of the systems that can be controlled
        """
        tags = []
        for key in self.configdb:
            if 'system' in self.configdb[key]:
                rec = self.configdb[key]
                if grpname in rec:
                    item = rec[grpname]
                    tags.append(item)

        return find_unique(tags)

    def find_subgroups(dbinput, grpname, grp, subgrpname):
        """
        take the control db and find the unique categories within a given group
        `dbinput`: the dictionary or shelve object for the command db
        `grpname`: a string for the keyname for the grouping
        `grp`: a string that identifies that group
        `subgrpname`: a string for the keyname of the subgroup or category
        return a list object of the category/subgroup names

        example:
        find_subgroups(db,'system','Housekeeping','category')
        will generate a list of the different control categories in the
        housekeeping system. (possible 'category' for controls in the database
        for which system='housekeeping')
        TODO: add else exception for rec.has_key's
        """
        tags = []
        for key in dbinput:
            if 'system' in dbinput[key]:
                rec = dbinput[key]
                if grpname in rec and subgrpname in rec:
                    if rec[grpname] == grp:
                        item = rec[subgrpname]
                        tags = tags + [item]
        return find_unique(tags)


def db_convert(dbinput, entry_type_in, info_in, entry_type_out):
    r"""
    each entry of the control dictionary database is a dictionary
    that contains information about the control variable entry (what type
    of button it is, its description, and so on). This function will
    run through all the control variables until it finds one where the
    entry_type_in matches the request. In some cases, there are many
    control variables that have the same entry type; for example, 'edit_level'.
    in thise case, the function will return the first one that matches--
    you should run db_convert on unique entry types:
    db_convert(db, 'short_name', 'relay3000', 'destination')
    will tell you for the control variable with short_name='relay3000',
    what the destination is.

    `dbinput`: the dictionary or shelve object for the command db
    `entry_type_in`: the type of entry to match
    `info_in`: the desired value for that entry type
    `entry_type_out`: the type of info about the variable to output
    """

    info_out = None
    for key in dbinput:
        if 'system' in dbinput[key]:
            rec = dbinput[key]
            if entry_type_in in rec:
                if rec[entry_type_in] == info_in:
                    info_out = rec[entry_type_out]
            else:
                print "db_convert: failed"

    return info_out


def get_db_convert(shelvefilename, entry_type_in, info_in, entry_type_out):
    """lazy method to call db_convert
    `shelvefilename`: shelve file containing the control database
    `entry_type_in`: the type of entry to match
    `info_in`: the desired value for that entry type
    `entry_type_out`: the type of information about the variable to output
    """
    dbinput = shelve.open(shelvefilename, "r")
    return db_convert(dbinput, entry_type_in, info_in, entry_type_out)


def control_typecast(input_control, output_type):
    """ typecast some input based on its control type
    `input_control`: the input quantity, either float, int, string
    `output_type`: a string, either 'float', 'int', or 'string'
    return input recast as an output_type"""

    output = input_control
    if (type(input_control) is types.IntType or \
       type(input_control) is types.FloatType) \
       and output_type == 'string':
        return repr(input_control)

    if type(input_control) is types.StringType and output_type == 'float':
        return float(input_control)

    if type(input_control) is types.StringType and output_type == 'int':
        return int(float(input_control))

    if type(input_control) is types.FloatType and output_type == 'int':
        return int(input_control)

    if type(input_control) is types.IntType and output_type == 'float':
        return float(input_control)

    return output


def find_controltype(short_name, shelvefilename):
    """what type of variable does ... control
    this assumes that the type_list is one->one"""

    dbinput = shelve.open(shelvefilename, "r")
    output = None
    type_list = dbinput['type_list']
    for key in type_list:
        rec = type_list[key]
        if short_name in rec:
            output = key

    return output


def find_commands(dbinput, grpname, grp, subgrpname, subgrp):
    """ for a given system and control category, list all available commands
    example:
    find_commands(db, 'system', 'housekeeping', 'cateogry', 'master')
    """
    tags = []
    for key in dbinput:
        if 'system' in dbinput[key]:
            rec = dbinput[key]
            if (grpname in rec) and (subgrpname in rec):
                if rec[grpname] == grp and rec[subgrpname] == subgrp:
                    tags = tags + [rec]

    return tags


def pare_pulldown(pulldowndb):
    """for a pulldown menu type, make a new dictionary with index:
    desription"""
    out_dict = {}
    for key in pulldowndb:
        try:
            #desc = key + " : " + pulldowndb[key]['label']
            desc = pulldowndb[key]['label']
            out_dict[key] = desc
        except KeyError:
            pass
    return out_dict


if __name__ == "__main__":
    import doctest

    OPTIONFLAGS = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE)
    doctest.testmod(optionflags=OPTIONFLAGS)
