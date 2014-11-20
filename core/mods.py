#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""<description of the module>"""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil, glob, difflib, sys
from io import open

from . import paths, baselines

def read_mods():
    """Returns a list of mod packs"""
    # should go in tkgui/mods.py later
    return [os.path.basename(o) for o in
            glob.glob(os.path.join(paths.get('mods'), '*'))
            if os.path.isdir(o)]

def simplify_mods():
    """Removes unnecessary files from all mods."""
    for pack in read_mods():
        simplify_pack(pack)

def simplify_pack(pack):
    """Removes unnecessary files from one mod."""
    baselines.simplify_pack(pack, 'mods')
    baselines.remove_vanilla_raws_from_pack(pack, 'mods')
    baselines.remove_empty_dirs(pack, 'mods')

def do_merge_seq(mod_text, vanilla_text, gen_text):
    """Merges sequences of lines.  Returns empty string if a line changed by
    the mod has been changed by a previous mod, or merged lines otherwise.

    Params:
        mod_text
            The lines of the mod file being added to the merge.
        vanilla_text
            The lines of the corresponding vanilla file.
        gen_text
            The lines of the previously merged file.

    Returns:
        tuple(status, lines); status is 0/'ok' or 2/'overlap merged'
    """
    status = 0
    # special cases - where merging is not required because two are equal
    if vanilla_text == gen_text:
        return 0, mod_text
    if vanilla_text == mod_text:
        return 0, gen_text

    # Returns list of 5-tuples describing how to turn vanilla into mod or gen
    # lines.  Each specifies an operation, and start+end lines for each change.
    # We then compose a text from these by concatenation, returning
    # false if the mod changes lines which have already been changed.
    van_mod_match = difflib.SequenceMatcher(None, vanilla_text, mod_text)
    van_gen_match = difflib.SequenceMatcher(None, vanilla_text, gen_text)
    van_mod_ops = van_mod_match.get_opcodes()
    van_gen_ops = van_gen_match.get_opcodes()

    output_file_temp = []
    # holds the line we're up to, effectively truncates blocks which were
    # partially covered in the previous iteration.
    cur_v = 0
    while van_mod_ops and van_gen_ops:
        # get names from the next set of opcodes
        mod_tag, mod_i1, mod_i2, mod_j1, mod_j2 = van_mod_ops[0]
        gen_tag, gen_i1, gen_i2, gen_j1, gen_j2 = van_gen_ops[0]
        # if the mod is vanilla for these lines
        if mod_tag == 'equal':
            # if the gen lines are also vanilla
            if gen_tag == 'equal':
                # append the shorter block to new genned lines
                if mod_i2 < gen_i2:
                    output_file_temp += vanilla_text[cur_v:mod_i2]
                    cur_v = mod_i2
                    van_mod_ops.pop(0)
                else:
                    output_file_temp += vanilla_text[cur_v:gen_i2]
                    cur_v = gen_i2
                    van_gen_ops.pop(0)
                    if mod_i2 == gen_i2:
                        van_mod_ops.pop(0)
            # otherwise append current genned lines
            else:
                output_file_temp += gen_text[gen_j1:gen_j2]
                cur_v = gen_i2
                van_gen_ops.pop(0)
                if mod_i2 == gen_i2:
                    van_mod_ops.pop(0)
        # if mod has changes from vanilla
        else:
            # if no earlier mod changed this section, adopt these changes
            if gen_tag == 'equal':
                output_file_temp += mod_text[mod_j1:mod_j2]
                cur_v = mod_i2
                van_mod_ops.pop(0)
                if mod_i2 == gen_i2:
                    van_gen_ops.pop(0)
            # if the changes would overlap, we can't handle that yet
            else:
                # this is the rare over-write merge.
                # changes status, use caution
                status = 2
                # append the shorter block to new genned lines
                if mod_i2 < gen_i2:
                    output_file_temp += mod_text[cur_v:mod_i2]
                    cur_v = mod_i2
                    van_mod_ops.pop(0)
                else:
                    output_file_temp += mod_text[cur_v:gen_i2]
                    cur_v = gen_i2
                    van_gen_ops.pop(0)
                    if mod_i2 == gen_i2:
                        van_mod_ops.pop(0)
    # clean up trailing opcodes, to avoid dropping the end of the file
    if van_mod_ops:
        mod_tag, mod_i1, mod_i2, mod_j1, mod_j2 = van_mod_ops[0]
        output_file_temp += mod_text[mod_j1:mod_j2]
    if van_gen_ops:
        gen_tag, gen_i1, gen_i2, gen_j1, gen_j2 = van_gen_ops[0]
        output_file_temp += gen_text[gen_j1:gen_j2]
    return status, output_file_temp

def do_merge_files(mod_file_name, van_file_name, gen_file_name):
    """Calls merge sequence on the files, and returns true if they could be
    (and were) merged or false if the merge was conflicting (and thus skipped).
    """
    van_lines = open(van_file_name, mode='r', encoding='cp437',
                     errors='replace').readlines()
    mod_lines = open(mod_file_name, mode='r', encoding='cp437',
                     errors='replace').readlines()
    gen_lines = []
    if os.path.isfile(gen_file_name):
        gen_lines = open(gen_file_name, mode='r', encoding='cp437',
                         errors='replace').readlines()

    status, gen_lines = do_merge_seq(mod_lines, van_lines, gen_lines)
    gen_file = open(gen_file_name, "w")
    for line in gen_lines:
        gen_file.write(line)
    return status

def merge_a_mod(mod):
    """Merges the specified mod, and returns an exit code 0-3.

        0:  Merge was successful, all well
        1:  Potential compatibility issues, no merge problems
        2:  Non-fatal error, overlapping lines or non-existent mod etc
        3:  Fatal error, respond by rebuilding to previous mod
        """
    mod_raw_folder = os.path.join(paths.get('mods'), mod, 'raw')
    if not os.path.isdir(mod_raw_folder):
        return 2
    status = merge_raw_folders(mod_raw_folder, baselines.find_vanilla_raws())
    if status < 3:
        with open(os.path.join(paths.get('baselines'), 'temp', 'raw',
                               'installed_raws.txt'), 'a') as log:
            log.write(mod + '\n')
    return status

def merge_raw_folders(mod_raw_folder, vanilla_raw_folder):
    """Merge the specified folders, output going in LNP/Baselines/temp/raw"""
    mixed_raw_folder = os.path.join(paths.get('baselines'), 'temp', 'raw')
    status = 0
    for file_tuple in os.walk(mod_raw_folder):
        for item in file_tuple[2]:
            f = os.path.join(file_tuple[0], item)
            f = os.path.relpath(f, mod_raw_folder)
            if not f.endswith('.txt'):
                continue
            if (os.path.isfile(os.path.join(vanilla_raw_folder, f)) or
                os.path.isfile(os.path.join(mixed_raw_folder, f))):
                status = max(do_merge_files(os.path.join(mod_raw_folder, f),
                                            os.path.join(vanilla_raw_folder, f),
                                            os.path.join(mixed_raw_folder, f)),
                             status)
            else:
                shutil.copy(os.path.join(mod_raw_folder, f), 
                            os.path.join(mixed_raw_folder, f))
    return status

def clear_temp():
    """Resets the folder in which raws are mixed."""
    if os.path.exists(os.path.join(paths.get('baselines'), 'temp')):
        shutil.rmtree(os.path.join(paths.get('baselines'), 'temp'))
    shutil.copytree(baselines.find_vanilla_raws(),
                    os.path.join(paths.get('baselines'), 'temp', 'raw'))
    with open(os.path.join(paths.get('baselines'), 'temp', 'raw',
                           'installed_raws.txt'), 'w') as log:
        log.write('# List of raws merged by PyLNP:\n' + 
                  os.path.basename(baselines.find_vanilla_raws()) + '\n')

def make_mod_from_installed_raws(name):
    """Capture whatever unavailable mods a user currently has installed
    as a mod called $name.

        * If `installed_raws.txt` is not present, compare to vanilla
        * Otherwise, rebuild as much as possible then compare to installed
        * Harder than I first thought... but not impossible.
    """
    if os.path.isdir(os.path.join(paths.get('mods'), name)):
        return False
    if get_installed_mods_from_log():
        clear_temp()
        for mod in get_installed_mods_from_log():
            merge_a_mod(mod)
        reconstruction = os.path.join(paths.get('baselines'), 'temp2', 'raw')
        shutil.copytree(os.path.join(paths.get('baselines'), 'temp', 'raw'),
                        reconstruction)
    else:
        reconstruction = baselines.find_vanilla_raws()

    clear_temp()
    merge_raw_folders(reconstruction, os.path.join(paths.get('df'), 'raw'))

    baselines.simplify_pack('temp', 'baselines')
    baselines.remove_vanilla_raws_from_pack('temp', 'baselines')
    baselines.remove_empty_dirs('temp', 'baselines')

    if os.path.isdir(os.path.join(paths.get('baselines'), 'temp2')):
        shutil.rmtree(os.path.join(paths.get('baselines'), 'temp2'))

    if os.path.isdir(os.path.join(paths.get('baselines'), 'temp')):
        shutil.copytree(os.path.join(paths.get('baselines'), 'temp'), 
                        os.path.join(paths.get('mods'), name))
        return True
    return False

def get_installed_mods_from_log():
    """Return best mod load order to recreate installed with available."""
    logged = read_installation_log(os.path.join(paths.get('df'),
                                                'raw', 'installed_raws.txt'))
    return [mod for mod in logged if mod in read_mods()]

def read_installation_log(fl):
    """Read an 'installed_raws.txt' and return it's full contents."""
    try:
        with open(fl) as f:
            file_contents = list(f.readlines())
    except IOError:
        return []
    mods_list = []
    for line in file_contents:
        if not line.strip() or line.startswith('#'):
            continue
        mods_list.append(line.strip())
    return mods_list
