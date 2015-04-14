#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Linter for raw files. Ported from Lethosor's Lua script:
https://github.com/lethosor/dfhack-scripts/blob/master/raw-lint.lua"""
from __future__ import print_function, unicode_literals, absolute_import

import os

from .dfraw import DFRaw
from . import log

# TODO: Handle older versions correctly
# For example, 40d and earlier use object names MATGLOSS and DESCRIPTOR
valid_objnames = [
    'BODY_DETAIL_PLAN',
    'BODY',
    'BUILDING',
    'CREATURE_VARIATION',
    'CREATURE',
    'DESCRIPTOR_COLOR',
    'DESCRIPTOR_PATTERN',
    'DESCRIPTOR_SHAPE',
    'ENTITY',
    'INORGANIC',
    'INTERACTION',
    'ITEM',
    'LANGUAGE',
    'MATERIAL_TEMPLATE',
    'PLANT',
    'REACTION',
    'TISSUE_TEMPLATE',
]

objname_overrides = {
    'b_detail_plan': 'BODY_DETAIL_PLAN',
    'c_variation': 'CREATURE_VARIATION',
}

def check_file(path):
    """Validates the raw file located at <path>. Error details are printed to
    the log with level WARNING. Returns True/False."""
    file_ok = True
    if not path.endswith('.txt'):
        log.w('Unrecognized filename')
        return False
    contents = DFRaw.read(path)
    filename = os.path.basename(path)[:-4]
    try:
        realname = contents.splitlines()[0]
    except IndexError:
        realname = ''
    try:
        rawname = realname.split()[0]
    except IndexError:
        rawname = realname
    # Everything before first whitespace must match filename
    if not (realname == realname.lstrip() and rawname == filename):
        log.w('Name mismatch: expected %s, found %s' % (filename, rawname))
        file_ok = False
    objname = filename
    check_objnames = []
    for k, v in objname_overrides.items():
        if filename.startswith(k) and v in valid_objnames:
            check_objnames.append(v)
    for o in valid_objnames:
        if filename.upper().startswith(o):
            check_objnames.append(o)
    if check_objnames:
        found = False
        for i, objname in enumerate(check_objnames):
            objname = '[OBJECT:' + objname.upper() + ']'
            if objname in contents:
                found = True
            check_objnames[i] = objname
        if not found:
            log.w('None of %s found' % ', '.join(check_objnames))
            file_ok = False
    else:
        log.w('No valid object names')
        file_ok = False
    return file_ok

def check_folder(path):
    """Validates all raw files in <path> and its subfolders. Problems with
    individual files are printed to the log with level WARNING. General problems
    are printed to the log with level ERROR.

    Returns:
        (passed, failed)
            two lists of paths of files that passed or failed, respectively"""
    log.push_prefix('RawLint')
    files = []
    for d in os.walk(path):
        files += [os.path.join(d[0], f) for f in d[2]]
    passed = []
    failed = []
    if not files:
        log.e('Could not find any files in '+path)
    for f in files:
        f_parts = f.split(os.sep)
        if (f.endswith('.txt') and 'notes' not in f_parts and
                'text' not in f_parts):
            log.push_prefix(f)
            has_passed = check_file(f)
            log.pop_prefix()
            if has_passed:
                passed.append(f)
            else:
                failed.append(f)
    log.pop_prefix()
    return (passed, failed)

def check_df(path):
    """Validates the raw/objects folder in the Dwarf Fortress folder located at
    <path>. Problem with individual files are printed to the log with level
    WARNING. General problems are printed to the log with level ERROR.

    Returns:
        (passed, failed)
            two lists of paths of files that passed or failed, respectively"""
    return check_folder(os.path.join(path, 'raw', 'objects'))

def check_folder_bool(path):
    """Returns True if all raw files in <path> pass validation. Problems with
    individual files are printed to the log with level WARNING. General
    problems are printed to the log with level ERROR."""
    p, f = check_folder(path)
    return len(f) == 0 and len(p) != 0

def check_df_bool(path):
    """Validates the raw/objects folder in the Dwarf Fortress folder located at
    <path> and returns True if all files pass validation. Problems with
    individual files are printed to the log with level WARNING. General
    problems are printed to the log with level ERROR."""
    p, f = check_df(path)
    return len(f) == 0 and len(p) != 0
