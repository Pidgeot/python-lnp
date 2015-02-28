#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mod Pack management and merging tools."""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil, glob
from difflib import ndiff, SequenceMatcher
# pylint:disable=redefined-builtin
from io import open

from . import paths, baselines

def read_mods():
    """Returns a list of mod packs"""
    return [os.path.basename(o) for o in
            glob.glob(paths.get('mods', '*'))
            if os.path.isdir(o)]

def simplify_mods():
    """Removes unnecessary files from all mods."""
    mods, files = 0, 0
    for pack in read_mods():
        mods += 1
        files += simplify_pack(pack)
    return mods, files

def simplify_pack(pack):
    """Removes unnecessary files from one mod.

    Params:
        pack
            path segment in './LNP/folder/pack/' as strings

    Returns:
        The sum of files affected by the operations
    """
    # Here we use the heuristic that mods which are bundled with other files
    # contain a complete set of raws, and vanilla files which are missing
    # should not be inserted.  We thus add empty files to fill out the set in
    # cases where several files are removed.
    i = baselines.simplify_pack(pack, 'mods')
    if i > 10:
        i += make_blank_files(pack)
    i += baselines.remove_vanilla_raws_from_pack(pack, 'mods')
    i += baselines.remove_empty_dirs(pack, 'mods')
    return i

def make_blank_files(pack):
    """Create blank files where vanilla files are missing.

    Params:
        pack
            path segment in './LNP/folder/pack/' as strings

    Returns:
        The number of blank files created
    """
    i = 0
    vanilla_raws = baselines.find_vanilla_raws()
    for root, _, files in os.walk(vanilla_raws):
        for k in files:
            f = os.path.relpath(os.path.join(root, k), vanilla_raws)
            if not os.path.isfile(paths.get('mods', pack, f)):
                with open(paths.get('mods', pack, f), 'w') as blank:
                    blank.write('')
                    i += 1
    return i

def install_mods():
    """Deletes installed raw folder, and copies over merged raws."""
    log = paths.get('baselines', 'temp', 'raw', 'installed_raws.txt')
    if get_installed_mods_from_log(log):
        shutil.rmtree(paths.get('df', 'raw'))
        shutil.rmtree(paths.get('df', 'data', 'speech'))
        shutil.copytree(paths.get('baselines', 'temp', 'raw'),
                        paths.get('df', 'raw'))
        shutil.copytree(paths.get('baselines', 'temp', 'data', 'speech'),
                        paths.get('df', 'data', 'speech'))
        return True
    return False

def do_merge_seq(mod_text, vanilla_text, gen_text):
    """Merges sequences of lines.

    Params:
        mod_text
            The lines of the mod file being added to the merge.
        vanilla_text
            The lines of the corresponding vanilla file.
        gen_text
            The lines of the previously merged file or files.

    Returns:
        tuple(status, lines); status is 0/'ok' or 2/'overlap merged'
    """
    if mod_text and vanilla_text == gen_text:
        # This is the first time a vanilla file is modified
        return 0, mod_text
    if gen_text and vanilla_text == mod_text:
        # The mod being merged isn't in reduced raw format
        return 0, gen_text
    if gen_text and gen_text == mod_text:
        # A previous mod made exactly the same changes
        return 0, gen_text
    if mod_text and gen_text and not vanilla_text:
        # No such vanilla file, so we need a two-way merge (additive only)
        return 0, [s[2:] for s in ndiff(gen_text, mod_text)]
    # Finally go to the expensive but complete merge logic
    return three_way_merge(vanilla_text, gen_text, mod_text)

def three_way_merge(vanilla_text, gen_text, mod_text):
    """Implements a three-way merge and returns a tuple of (status, result)"""
    # SequenceMatcher describes how to turn vanilla into mod or gen lines.
    # cur_v holds the line we're up to, truncating overridden blocks
    van_mod_ops = SequenceMatcher(None, vanilla_text, mod_text).get_opcodes()
    van_gen_ops = SequenceMatcher(None, vanilla_text, gen_text).get_opcodes()
    status, output_file_temp, cur_v = 0, [], 0

    while van_mod_ops and van_gen_ops:
        # get names from the next set of opcodes
        mod_tag, _, mod_i2, mod_j1, mod_j2 = van_mod_ops[0]
        gen_tag, _, gen_i2, gen_j1, gen_j2 = van_gen_ops[0]
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
            else:
                # An over-write merge. Change status to warn the user, unless
                # we're overwriting with an identical change, and append the
                # shorter block to new genned lines
                if mod_i2 < gen_i2:
                    if gen_text[cur_v:mod_i2] != mod_text[cur_v:mod_i2]:
                        status = 2
                    output_file_temp += mod_text[cur_v:mod_i2]
                    cur_v = mod_i2
                    van_mod_ops.pop(0)
                else:
                    if gen_text[cur_v:gen_i2] != mod_text[cur_v:gen_i2]:
                        status = 2
                    output_file_temp += mod_text[cur_v:gen_i2]
                    cur_v = gen_i2
                    van_gen_ops.pop(0)
                    if mod_i2 == gen_i2:
                        van_mod_ops.pop(0)
    # clean up trailing opcodes, to avoid dropping the end of the file
    while van_mod_ops:
        mod_tag, _, mod_i2, mod_j1, mod_j2 = van_mod_ops.pop(0)
        output_file_temp += mod_text[mod_j1:mod_j2]
    while van_gen_ops:
        gen_tag, _, gen_i2, gen_j1, gen_j2 = van_gen_ops.pop(0)
        output_file_temp += gen_text[gen_j1:gen_j2]
    return status, output_file_temp

def do_merge_files(mod_file_name, van_file_name, gen_file_name):
    """Merges three files, and returns an exit code 0-3.

        0:  Merge was successful, all well
        1:  Potential compatibility issues, no merge problems
        2:  Non-fatal error, overlapping lines or non-existent mod etc
        3:  Fatal error, respond by rebuilding to previous mod
    """
    #pylint:disable=bare-except
    try:
        van_lines = open(van_file_name, mode='r', encoding='cp437',
                         errors='replace').readlines()
    except:
        van_lines = []
    try:
        mod_lines = open(mod_file_name, mode='r', encoding='cp437',
                         errors='replace').readlines()
    except:
        mod_lines = []
    try:
        gen_lines = open(gen_file_name, mode='r', encoding='cp437',
                         errors='replace').readlines()
    except:
        gen_lines = []
    status, gen_lines = do_merge_seq(mod_lines, van_lines, gen_lines)
    try:
        with open(gen_file_name, "w", encoding='cp437') as gen_file:
            gen_file.writelines(gen_lines)
    except:
        return 3
    return status

def merge_a_mod(mod):
    """Merges the specified mod, and returns an exit code 0-3.

        0:  Merge was successful, all well
        1:  Potential compatibility issues, no merge problems
        2:  Non-fatal error, overlapping lines or non-existent mod etc
        3:  Fatal error, respond by rebuilding to previous mod
        """
    if not baselines.find_vanilla_raws():
        return 3
    mod_raw_folder = paths.get('mods', mod, 'raw')
    if not os.path.isdir(mod_raw_folder):
        return 2
    status = merge_folders(mod_raw_folder, baselines.find_vanilla_raws(),
                           paths.get('baselines', 'temp', 'raw'))
    if os.path.isdir(paths.get('mods', mod, 'data', 'speech')):
        status = max(status, merge_folders(
            paths.get('mods', mod, 'data', 'speech'),
            os.path.join(baselines.find_vanilla(), 'data', 'speech'),
            paths.get('baselines', 'temp', 'data', 'speech')))
    if status < 3:
        with open(paths.get('baselines', 'temp', 'raw', 'installed_raws.txt'),
                  'a') as log:
            log.write('mods/' + mod + '\n')
    return status

def merge_folders(mod_folder, vanilla_folder, mixed_folder):
    """Merge the specified folders, output going in 'LNP/Baselines/temp'
    Text files are merged; other files (sprites etc) are copied over."""
    status = 0
    for root, _, files in os.walk(mod_folder):
        for k in files:
            f = os.path.relpath(os.path.join(root, k), mod_folder)
            mod_f = os.path.join(mod_folder, f)
            van_f = os.path.join(vanilla_folder, f)
            gen_f = os.path.join(mixed_folder, f)
            if any([f.endswith(a) for a in ('.txt', '.init')]):
                # merge raws and DFHack init files
                ret = do_merge_files(mod_f, van_f, gen_f)
                status = max(ret, status)
            elif any([f.endswith(a) for a in ('.lua', '.rb', '.bmp', '.png')]):
                # copy DFHack scripts or sprite sheets
                if not os.path.isdir(os.path.dirname(gen_f)):
                    os.mkdir(os.path.dirname(gen_f))
                if not os.path.isfile(gen_f):
                    shutil.copyfile(mod_f, gen_f)
                    status = max(1, status)
                else:
                    with open(mod_f, 'rb') as m:
                        mb = m.read()
                    with open(gen_f, 'rb') as g:
                        gb = g.read()
                    if not mb == gb:
                        shutil.copyfile(mod_f, gen_f)
                        status = max(2, status)
    return status

def clear_temp():
    """Resets the folder in which raws are mixed."""
    if not baselines.find_vanilla_raws(False):
        # Baselines are not ready; abort silently
        return None
    if os.path.exists(paths.get('baselines', 'temp')):
        shutil.rmtree(paths.get('baselines', 'temp'))
    shutil.copytree(baselines.find_vanilla_raws(),
                    paths.get('baselines', 'temp', 'raw'))
    shutil.rmtree(paths.get('baselines', 'temp', 'raw', 'graphics'))
    shutil.copytree(os.path.join(baselines.find_vanilla(), 'data', 'speech'),
                    paths.get('baselines', 'temp', 'data', 'speech'))
    with open(paths.get('baselines', 'temp', 'raw', 'installed_raws.txt'),
              'w') as log:
        log.write('# List of raws merged by PyLNP:\nbaselines/' +
                  os.path.basename(baselines.find_vanilla()) + '\n')

def make_mod_from_installed_raws(name):
    """Capture whatever unavailable mods a user currently has installed
    as a mod called $name.

        * If `installed_raws.txt` is not present, compare to vanilla
        * Otherwise, rebuild as much as possible then compare to installed
    """
    if os.path.isdir(paths.get('mods', name)):
        return False
    if get_installed_mods_from_log():
        clear_temp()
        for mod in get_installed_mods_from_log():
            merge_a_mod(mod)
        reconstruction = paths.get('baselines', 'temp2')
        shutil.copytree(paths.get('baselines', 'temp'), reconstruction)
    else:
        reconstruction = baselines.find_vanilla()
        if not reconstruction:
            return None

    clear_temp()
    merge_folders(os.path.join(reconstruction, 'raw'),
                  paths.get('df', 'raw'),
                  paths.get('baselines', 'temp', 'raw'))
    merge_folders(os.path.join(reconstruction, 'data', 'speech'),
                  paths.get('df', 'data', 'speech'),
                  paths.get('baselines', 'temp', 'data', 'speech'))

    baselines.simplify_pack('temp', 'baselines')
    baselines.remove_vanilla_raws_from_pack('temp', 'baselines')
    baselines.remove_empty_dirs('temp', 'baselines')

    if os.path.isdir(paths.get('baselines', 'temp2')):
        shutil.rmtree(paths.get('baselines', 'temp2'))

    if os.path.isdir(paths.get('baselines', 'temp')):
        shutil.copytree(paths.get('baselines', 'temp'), paths.get('mods', name))
        return True
    return False

def get_installed_mods_from_log():
    """Return best mod load order to recreate installed with available."""
    logged = read_installation_log(paths.get('df', 'raw', 'installed_raws.txt'))
    return [mod for mod in logged if mod in read_mods()]

def read_installation_log(log):
    """Read an 'installed_raws.txt' and return it's full contents."""
    try:
        with open(log) as f:
            file_contents = list(f.readlines())
    except IOError:
        return []
    mods_list = []
    for line in file_contents:
        if line.startswith('mods/'):
            mods_list.append(line.strip().replace('mods/', ''))
    return mods_list
