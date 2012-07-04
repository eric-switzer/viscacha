""" Functions for parsing control dictionaries and lists"""
import types
import shelve
try: import simplejson as json
except ImportError: import json
import tempfile
import urllib2


def _decode_list(data):
    r"""convert native json unicode to str"""
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    r"""convert native json unicode to str"""
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
           key = key.encode('utf-8')
        if isinstance(value, unicode):
           value = value.encode('utf-8')
        elif isinstance(value, list):
           value = _decode_list(value)
        elif isinstance(value, dict):
           value = _decode_dict(value)
        rv[key] = value
    return rv


def load_json_over_http(url):
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    fp_url = opener.open(req)
    retjson = json.load(fp_url, object_hook=_decode_dict)

    return retjson


def load_json_over_http_file(url):
    r"""alternate implementation which writes a file"""
    req = urllib2.urlopen(url)
    temp_file = tempfile.NamedTemporaryFile()

    chunksize = 16 * 1024
    while True:
        chunk = req.read(chunksize)
        if not chunk: break
        temp_file.write(chunk)
    temp_file.flush()

    retjson = json.load(open(temp_file.name, "r"), object_hook=_decode_dict)
    temp_file.close()

    return retjson


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
    def __init__(self, configaddr=None, configdb=None, silent=True):
        if configaddr is not None:
            treetitle = "System tree specified in: " + configaddr
            print treetitle + "\n" + "-" * len(treetitle)
            self.configdb = load_json_over_http(configaddr)

        if configdb is not None:
            self.configdb = configdb

        self.build_system_tree()

        if not silent:
            print_treedict(self.system_tree)

    def build_system_tree(self, grpname="system", subgrpname="category"):
        r"""construct the dictionary of systems, subsystems, commands"""
        self.system_tree = {}

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

    def subsystem_list(self, system):
        return self.system_tree[system].keys()

    def command_list(self, system, subsystem):
        return self.system_tree[system][subsystem]

    def command_dict(self, command_key):
        return self.configdb[command_key]

if __name__ == "__main__":
    import doctest

    OPTIONFLAGS = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE)
    doctest.testmod(optionflags=OPTIONFLAGS)
