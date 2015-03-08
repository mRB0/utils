#!/usr/bin/env python
# -*- coding: utf-8; -*-

r"""
Read a uTorrent '.dat' file and convert it to json so it's easier to inspect and work with.

Example usage: python utorrent_dat_to_json.py C:\Users\me\AppData\Roaming\uTorrent\resume.dat
"""


class Reader(object):

    def __init__(self, source):
        self.source = source

    def readint(self):
        s = ''
        c = self.source.next()
        while c != 'e':
            s += c
            c = self.source.next()

        return int(s)


    def read_list(self):
        c = []
        
        nv = self.read_next()
        while nv is not None:
            c.append(nv)
            nv = self.read_next()

        return c

    def read_dict(self):
        c = {}

        nk = self.read_next()
        while nk is not None:
            nv = self.read_next()
            c[nk] = nv

            nk = self.read_next()

        return c

    def read_next(self):
        nb = self.source.next()

        if nb == 'i':
            value = self.readint()
            return value
        elif nb == 'l':
            return self.read_list()
        elif nb == 'd':
            return self.read_dict()
        elif nb == 'e':
            return None
        elif nb.isdigit():
            lengthstr = nb
            nb = self.source.next()
            while nb != ':':
                lengthstr = lengthstr + nb
                nb = self.source.next()
            length = int(lengthstr)
            str_value = ''.join([self.source.next() for _ in xrange(length)])

            return str_value


#
# Output: Printing and escaping
#

def escape_as_hex(str_value):
    return ('0x' + ''.join([hex(ord(c))[2:].zfill(2) for c in str_value])).decode('iso-8859-1')

def escape_as_base64(str_value):
    import base64
    return base64.encodestring(str_value).decode('iso-8859-1')

def escape_as_unicode(str_value):
    return str_value.decode('iso-8859-1')

escape_fn_names = {escape_as_hex: u"hex",
                   escape_as_base64: u"base64"}

def escape_unprintable_string(str_value, escape_fn):
    if ['' for c in str_value if ord(c) < ord(' ')]:
        # escape if there are fancy characters
        final = escape_fn(str_value)
    else:
        try:
            # escape if we can't treat the string as utf-8
            final = str_value.decode('utf-8')
        except:
            final = escape_fn(str_value)
    return final

def print_names_and_paths(root):
    for name, props in sorted(root.iteritems(), key=lambda kv: kv[0]):
        try:
            print '{}\n    {}'.format(name, props['path'])
        except:
            pass

def escape_unprintable_strings(element, escape_fn):
    if isinstance(element, dict):
        
        new_dict = {}
        for k, v in element.iteritems():
            new_key = escape_unprintable_strings(k, escape_fn)
            new_value = escape_unprintable_strings(v, escape_fn)
            if isinstance(new_value, unicode) and new_value.encode('utf-8') != v:
                name = escape_fn_names.get(escape_fn, None)
                if name:
                    new_key = u"{}${}".format(new_key, name)

            new_dict[new_key] = new_value
        return new_dict

    elif isinstance(element, list):

        new_list = []
        for v in element:
            new_value = escape_unprintable_strings(v, escape_fn)
            new_list.append(new_value)
        return new_list

    elif isinstance(element, str):

        return escape_unprintable_string(element, escape_fn)

    else:

        return element

#
# Main
#

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=u"Convert a uTorrent .dat file to JSON for readability.")

    escape_fns = {u'hex': escape_as_hex,
                  u'base64': escape_as_base64,
                  u'raw': escape_as_unicode}

    parser.add_argument('-o', metavar="PATH", type=unicode, nargs=1, help=u"Save output to file instead of stdout")
    parser.add_argument('-e', metavar="ESCAPE", choices=escape_fns.keys(), default=[u'base64'], nargs=1, help=u"How to escape binary strings in JSON output [base64 (default), hex, raw]")
    parser.add_argument('datfile', nargs=1, type=unicode, help=u".dat file to convert")

    args = parser.parse_args()

    with open(args.datfile[0], 'rb') as f:
        contents = f.read()

    source = (c for c in contents)

    try:
        root = Reader(source).read_next()
    except StopIteration as e:
        pass


    escape_fn = escape_fns[args.e[0]]
    escaped_root = escape_unprintable_strings(root, escape_fn)


    def write_result_to_file(fileobj):
        import json
        fileobj.write(json.dumps(escaped_root, sort_keys=True, indent=4, separators=(',', ': ')))

    if args.o:
        with open(args.o[0], 'wb') as f:
            write_result_to_file(f)
    else:
        import sys
        write_result_to_file(sys.stdout)





