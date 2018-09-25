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


def analyze_duplicates(displaycount=None):
    """Prints a list of duplicates."""
    with open('duplicate.json', 'r') as f:
        files = pickle.load(f)
        
    sortedfiles = sorted(files, key=lambda x: (len(x), os.path.getsize(x[0])), reverse=True)
    for pos, paths in enumerate(sortedfiles[:displaycount], start=1):
        prefix = os.path.dirname(os.path.commonprefix(paths))
        print "\n(%d) Found %d duplicate files (size: %d Bytes) in %s/:" % \
            (pos, len(paths), os.path.getsize(paths[0]), prefix)
        if 'copied_to_NAS' in prefix:
            continue # skip internal duplicate for now
        for i, path in enumerate(sorted(paths), start=1):
            print "%2d: %s" % (i, path[len(prefix) + 1:])
            
    return files

def analyze_dup_dir(displaycount=None):
    """Prints a list of duplicates."""
    with open('duplicate.json', 'r') as f:
        files = pickle.load(f)
        
    sortedfiles = sorted(files, key=lambda x: (len(x), os.path.getsize(x[0])), reverse=True)

    duplicates = {}
    for pos, paths in enumerate(sortedfiles[:displaycount], start=1):
        dirs = sorted([os.path.dirname(p) for p in paths])
        key = tuple(dirs)
        duplicates.setdefault(key, []).append(set(paths))

    counts = {k:len(duplicates[k]) for k in duplicates}
    for paths, c in sorted(counts.items(), key= lambda (k, v) : v):
        #print paths
        prefix = os.path.dirname(os.path.commonprefix(paths))
        if '_copied_to_NAS' in prefix:
            continue
        print "\n(%d) Found %d duplicate files (size: %d Bytes) in %s/:" % \
            (c, len(paths), os.path.getsize(paths[0]), prefix)
        #if 'copied_to_NAS' in prefix:
        #    continue # skip internal duplicate for now
        for i, path in enumerate(sorted(paths), start=1):
            print "%2d: %s" % (i, path[len(prefix):])

if __name__ == "__main__":
    analyze_dup_dir()
    exit(0)
    DUPLICATES = analyze_duplicates()
    print "\nFound %d duplicates (%d duplicate files total)" % \
        (len(DUPLICATES), reduce(lambda sumValue, files: sumValue + len(files), DUPLICATES, 0))
