#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for traversing a directory structure, finding duplicate FILES and displaying them, but does NOT delete them."""

import os
import argparse
import hashlib
import zlib
import UpdatePrinter
import exceptions
import json
import pickle

__author__ = "Michael Krisper"
__copyright__ = "Copyright 2012, Michael Krisper"
__credits__ = ["Michael Krisper"]
__license__ = "GPL"
__version__ = "1.3.1"
__maintainer__ = "Michael Krisper"
__email__ = "michael.krisper@gmail.com"
__status__ = "Production"
__python_version__ = "2.7.3"

def parse_arguments():
    """ Parses the Arguments """

    epilog = """EXAMPLES:
    (1) %(prog)s ~/Downloads
        Description: Searches the Downloads directory for duplicate files and displays the top 3 duplicates (with the most files).

    (2) %(prog)s ~/Downloads -top 3
        Description: Searches duplicates, but only displays the top 3 most duplicates

    (3) %(prog)s ~/Downloads -top 3 --fast 
        Description: Searches for the top 3 duplicates. May eventually get less than 3 results, even if they would exist.

    (4) %(prog)s ~/Downloads -a
        Description: Searches duplicates and displays ALL results

    (5) %(prog)s ~/Downloads --hidden --empty
        Description: Searches duplicates and also include hidden or empty files
    """

    parser = argparse.ArgumentParser(description=__doc__, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(dest="directory", nargs='*', help="the directory which should be checked for duplicate files")
    parser.add_argument("-fast", dest="fast", action="store_true", 
                        help="Searches very fast for only for the top X duplicates. The fast check may return less than the \
                        top X, even if they would exist. Remarks: the fast option is useless when -a is given.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", dest="show_all", action="store_true", help="display all duplicate files. equal to -top 0")
    group.add_argument("-top", dest="top", action="store", metavar="X", default=3, type=int,  
                       help="set the amount of displayed duplicates. If 0 is given, all results will be displayed. default=10")
    parser.add_argument("--hidden", dest="include_hidden", action="store_true", help="check hidden files and hidden directories too")
    parser.add_argument("--empty", dest="include_empty", action="store_true", help="check empty files too")
    parser.add_argument("--nameonly", dest="nameonly", action="store_true", help="Only check name and size and simple hash, no full hash")
    args = parser.parse_args()
    if args.show_all or args.top == 0:
        args.top = None

    return args

def print_duplicates(files, displaycount=None):
    """Prints a list of duplicates."""
    with open('duplicate.json', 'w') as f:
        pickle.dump(files, f)
    sortedfiles = sorted(files, key=lambda x: (len(x), os.path.getsize(x[0])), reverse=True)
    f = open('duplicate_files.txt', 'w')
    for pos, paths in enumerate(sortedfiles[:displaycount], start=1):
        prefix = os.path.dirname(os.path.commonprefix(paths))
        print >>f, "\n(%d) Found %d duplicate files (size: %d Bytes) in %s/:" % \
            (pos, len(paths), os.path.getsize(paths[0]), prefix)
        for i, path in enumerate(sorted(paths), start=1):
            print >>f, "%2d: %s" % (i, path[len(prefix) + 1:])

def get_hash_key(filename):
    """Calculates the hash value for a file."""
    hash_object = hashlib.sha256()
    with open(filename, 'rb') as inputfile:
        for chunk in iter(lambda:inputfile.read(1024 * 8), ""):
            hash_object.update(chunk)
    return hash_object.digest()

def get_crc_key(filename):
    """Calculates the crc value for a file."""
    with open(filename, 'rb') as inputfile:
        chunk = inputfile.read(1024)
    return zlib.adler32(chunk)

def filter_duplicate_files(files, top=None, nameonly=False):
    """Finds all duplicate files in the directory."""
    duplicates = {}
    update = UpdatePrinter.UpdatePrinter().update
    iterations = ((os.path.getsize, "By Size", top**2 if top else None),  # top * top <-- this could be performance optimized further by top*3 or top*4
                  (get_crc_key, "By CRC ", top*2 if top else None),       # top * 2
                  (get_hash_key, "By Hash", None))
    if nameonly:
        iterations = iterations[:2]
    
    for keyfunction, name, topcount in iterations:
        duplicates.clear()
        count = 0
        duplicate_count = 0
        i = 0
        for i, filepath in enumerate(files, start=1):
            try:
                key = keyfunction(filepath)
            except Exception as e:
                print(e)
                continue
                
            duplicates.setdefault(key, []).append(filepath)
            if len(duplicates[key]) > 1:
                count += 1
                if len(duplicates[key]) == 2:
                    count += 1
                    duplicate_count += 1

            update("\r(%s) %d Files checked, %d duplicates found (%d files)" % (name, i, duplicate_count, count))
        else:
            update("\r(%s) %d Files checked, %d duplicates found (%d files)" % (name, i, duplicate_count, count), force=True)
        
        print ""
        sortedfiles = sorted(duplicates.itervalues(), key=len, reverse=True)
        files = [filepath for filepaths in sortedfiles[:topcount] if len(filepaths) > 1 for filepath in filepaths]

    if nameonly:
        pre = duplicates
        duplicates = {}
        for k in pre:
            for filepath in pre[k]:
                key = (os.path.basename(filepath), k)
                duplicates.setdefault(key, []).append(filepath)

    return [filelist for filelist in duplicates.itervalues() if len(filelist) > 1]

def get_files(directory, include_hidden, include_empty):
    """Returns all FILES in the directory which apply to the filter rules."""
    ignore = ('Thumbs.db')
    return (os.path.join(dirpath, filename)
            for dirpath, _, filenames in os.walk(directory)
            for filename in filenames
                if not os.path.islink(os.path.join(dirpath, filename)) and not os.path.basename(filename) in ignore and not 'RECYCLE.BIN' in dirpath
                and (include_hidden or
                     reduce(lambda r, d: r and not d.startswith("."), os.path.abspath(os.path.join(dirpath, filename)).split(os.sep), True))
                and (include_empty or os.path.getsize(os.path.join(dirpath, filename)) > 0))

if __name__ == "__main__":
    ARGS = parse_arguments()
    FILES = []
    print ARGS
    for directory in ARGS.directory:
        print ARGS.directory
        exit(1)
        FILES.extend(get_files(directory, ARGS.include_hidden, ARGS.include_empty))
    DUPLICATES = filter_duplicate_files(FILES, ARGS.top if ARGS.fast else None, ARGS.nameonly)
    print_duplicates(DUPLICATES, ARGS.top)
    
    if ARGS.fast:
        print "\nFound %d duplicates at least (%d duplicate files total) -- More duplicates may exist." % \
            (len(DUPLICATES), reduce(lambda sumValue, files: sumValue + len(files), DUPLICATES, 0))
    else:
        print "\nFound %d duplicates (%d duplicate files total)" % \
            (len(DUPLICATES), reduce(lambda sumValue, files: sumValue + len(files), DUPLICATES, 0))
