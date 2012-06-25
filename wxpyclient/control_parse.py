""" Functions for parsing control dictionaries and lists"""
import types
import shelve
import master_config_parse


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

    def build_system_tree(self, grpname="system", subgrpname="category"):
        r"""construct the dictionary of systems, subsystems, commands"""
        self.system_tree = {}
        treetitle = "System tree specified in: " + self.configaddr
        print treetitle + "\n" + "-" * len(treetitle)

        for key, conf_entry in self.configdb.iteritems():
            if 'system' in conf_entry:
                try:
                    sysname = conf_entry[grpname]
                    subsysname = conf_entry[subgrpname]
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

    def subsystem_list(system):
        return self.system_tree[system].keys()

    def command_list(system, subsystem):
        return self.system_tree[system][subsystem]


if __name__ == "__main__":
    import doctest

    OPTIONFLAGS = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE)
    doctest.testmod(optionflags=OPTIONFLAGS)
