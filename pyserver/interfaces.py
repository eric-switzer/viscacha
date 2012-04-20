import sys
from param import *
from logger import *

# global identification utilities
identification_db = {}


# attach a user name to a particular destination
def add_identity(destination, new_name):
    if destination in identification_db.keys():
        if new_name not in identification_db[destination]:
            identification_db[destination].append(new_name)
    else:
        identification_db[destination] = [new_name]


# flush a user name from the id table (appropriate for logoff)
def flush_identity(name):
    for key in identification_db.keys():
        if name in identification_db[key]:
            identification_db[key].remove(name)


# amcp common functions
def amcp_login(session, server):
    commentpush(session, 'SERVER_AUTH',
                SERVER_TOKEN + 'AMCP login successful')

    session.enter(server.amcp_interface)


def amcp_who(server):
    return server.amcp_interface.look_list()


def amcp_write_all(server, line):
    server.amcp_interface.sendcmd_all(line)


def amcp_write_user(server, user, line):
    server.amcp_interface.sendcmd_user(user, line)


# mce common functions
def mce_login(session, server):
    commentpush(session, 'SERVER_AUTH',
                SERVER_TOKEN + 'MCE login successful')

    session.enter(server.mce_interface)


def mce_who(server):
    return server.mce_interface.look_list()


def mce_write_all(server, line):
    server.mce_interface.sendcmd_all(line)


def mce_write_user(server, user, line):
    server.mce_interface.sendcmd_user(user, line)


# generic common functions
def generic_login(session, server):
    commentpush(session, 'SERVER_AUTH',
                SERVER_TOKEN + 'generic login successful')

    session.enter(server.generic_interface)


def generic_who(server):
    return server.generic_interface.look_list()


def generic_write_all(server, line):
    server.generic_interface.sendcmd_all(line)


def generic_write_user(server, user, line):
    server.generic_interface.sendcmd_user(user, line)


# human interface common functions
def client_login(session, server):
    commentpush(session, 'SERVER_AUTH',
                SERVER_TOKEN + 'human login successful')

    session.enter(server.client_interface)


def client_who(server):
    return server.client_interface.look_list()


def client_write_all(server, line):
    server.client_interface.sendcmd_all(line)


def client_write_user(server, user, line):
    server.client_interface.sendcmd_user(user, line)


interface_db = {}
interface_db['amcp'] = {'login': amcp_login, \
                        'who': amcp_who, \
                        'write_user': amcp_write_user, \
                        'write_all': amcp_write_all}

interface_db['mce'] = {'login': mce_login, \
                         'who': mce_who, \
                         'write_user': mce_write_user, \
                         'write_all': mce_write_all}

interface_db['generic'] = {'login': generic_login, \
                         'who': generic_who, \
                         'write_user': generic_write_user, \
                         'write_all': generic_write_all}

interface_db['human'] = {'login': client_login, \
                         'who': client_who, \
                         'write_user': client_write_user, \
                         'write_all': client_write_all}


def write_to_user(server, user, line):
    for interface_key in interface_db.keys():
        rec = interface_db[interface_key]
        if user in rec['who'](server):
            rec['write_user'](server, user, line)
        else:
            silentlogpush('SERVER_MESSAGE',
                          'requested user=' + user + ' not found')


def write_to_all(server, interface_type, line):
    if interface_type in interface_db.keys():
        rec = interface_db[interface_type]
        rec['write_all'](server, line)


def write_to_destination(server, destination, line):
    if destination in identification_db.keys():
        for user in identification_db[destination]:
            write_to_user(server, user, line)


def check_destination(destination):
    if destination in identification_db.keys():
        if len(identification_db[destination]) > 0:
            return 1
        else:
            return 0
    else:
        return 0
