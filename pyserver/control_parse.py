""" Functions for parsing control dictionaries and lists"""
import types
import sys
import os
import shelve
import string
from param import *


def find_unique(listinput):
    """find the unique elements in a list
    param listinput python list with possible repeated entries
    return a list of unique elements from listinput
    """
    unique = []
    for item in listinput:
        if item not in unique:
            unique = unique + [item]
    return unique


def find_groups(dbinput, grpname):
    """
    find list of unique system groups in the command db
    \param dbinput the dictionary or shelve object for the command db
    \param grpname a string for the keyname for the grouping
    return a list object of the group names

    example:
    find_groups(db, 'system')
    will return a list of the systems that can be controlled
    TODO: add else exception for rec.has_key
    """
    tags = []
    for key in dbinput:
        if 'system' in dbinput[key]:
            rec = dbinput[key]
            if grpname in rec:
                item = rec[grpname]
                tags = tags + [item]
    return find_unique(tags)


def find_subgroups(dbinput, grpname, grp, subgrpname):
    """
    take the control database and find the unique categories
    within a given group
    \param dbinput the dictionary or shelve object for the command db
    \param grpname a string for the keyname for the grouping
    \param grp a string that identifies that group
    \param subgrpname a string for the keyname of the subgroup or category
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


##
# each entry of the control dictionary database is a dictionary
# that contains information about the control variable entry (what type
# of button it is, its description, and so on).    This function will
# run through all the control variables until it finds one where the
# entry_type_in matches the request.    In some cases, there are many
# control variables that have the same entry type; for example, 'edit_level'.
# in thise case, the function will return the first one that matches--
# you should run db_convert on unique entry types:
# db_convert(db, 'short_name', 'relay3000', 'destination')
# will tell you for the control variable with short_name='relay3000',
# what the destination is.
def db_convert(dbinput, entry_type_in, info_in, entry_type_out):
    """\param dbinput the dictionary or shelve object for the command db
    \param entry_type_in the type of entry to match
    \param info_in the desired value for that entry type
    \param entry_type_out the type of information about the variable to output
    """
    info_out = None
    for key in dbinput:
        if 'systems' in dbinput[key]:
            rec = dbinput[key]
            if entry_type_in in rec:
                if rec[entry_type_in] == info_in:
                    info_out = rec[entry_type_out]
            else:
                silentlogpush('SERVER_ERROR',
                              'control file has no short_name' + short_name)

    return info_out


def get_db_convert(shelvefilename, entry_type_in, info_in, entry_type_out):
    """ lazy method to call db_convert
    \param shelvefilename shelve file containing the control database
    \param entry_type_in the type of entry to match
    \param info_in the desired value for that entry type
    \param entry_type_out the type of information about the variable to output
    """
    db = shelve.open(shelvefilename, "r")
    return db_convert(db, entry_type_in, info_in, entry_type_out)


def control_typecast(input, output_type):
    """ typecast some input based on its control type
     \param input the input quantity, either float, int, string
    \param output_type a string, either 'float', 'int', or 'string'
    return input recast as an output_type"""

    output = input
    if (type(input) is types.IntType or
        type(input) is types.FloatType) and output_type == 'string':
        return repr(input)

    if type(input) is types.StringType and output_type == 'float':
        return float(input)

    if type(input) is types.StringType and output_type == 'int':
        return int(float(input))

    if type(input) is types.FloatType and output_type == 'int':
        return int(input)

    if type(input) is types.IntType and output_type == 'float':
        return float(input)

    return output


def find_controltype(short_name, shelvefilename):
    """ what type of variable does ... control
    this assumes that the type_list is one->one"""
    db = shelve.open(shelvefilename, "r")
    output = None
    type_list = db['type_list']
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
            if grpname in rec and subgrpname in rec:
                if rec[grpname] == grp and rec[subgrpname] == subgrp:
                    tags = tags + [rec]

    return tags


def pare_pulldown(pulldowndb):
    """for a pulldown menu type, make a new dictionary with index:
    desription"""
    out_dict = {}
    for key in pulldowndb:
        try:
            keyval = key
            #desc = key + " : " + pulldowndb[key]['label']
            desc = pulldowndb[key]['label']
            out_dict[key] = desc
        except:
            None
    return out_dict


def value_to_key(dict_in, value):
    """find key for a given value"""
    tags = []
    for key in dict_in:
        if dict_in[key].find(value) != -1:
            tags = tags + [key]

    return tags


def flatten_string(string_in):
    """ Flatten a string by replacing newlines with ^ and
    spaces with &
    """
    output = string.replace(string_in, "\n", "^")
    output = string.replace(output, " ", "&")
    return output


def unflatten_string(string_in):
    """ unflatten a string by replacing ^ with newline and
    & with space"""
    output = string.replace(string_in, "^", "\n")
    output = string.replace(output, "&", " ")
    return output