import os, shutil, filecmp, glob, tempfile
import difflib, sys, time

from . import paths
from . import raws

paths.register('mods', 'LNP', 'mods')

def simplify_mod_and_df_folders_to_defined_format():
    raws.simplify_mods()

def do_merge_seq (mod_text, vanilla_text, gen_text):
    """Merges sequences of lines.  Returns empty string if a line changed by the mod
    has been changed by a previous mod, or merged lines otherwise.

    Params:
        mod_text
            The lines of the mod file being added to the merge.
        vanilla_text
            The lines of the corresponding vanilla file.
        gen_text
            The lines of the previously merged file.

    Returns:
        Merged lines if no changes in mod and gen files overlap.
        Empty string otherwise.
    """
    # special cases - where merging is not required because two are equal
    if vanilla_text == gen_text:
        return mod_text
    if vanilla_text == mod_text:
        return gen_text

    # returns list of 5-tuples describing how to turn vanilla into mod or gen lines
    # each specifies an operation, and start+end line nums for each change
    # we then compose a text from these by concatenation,
    # returning false if the mod changes lines which have already been changed.
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
            if gen_tag == 'equal' :
                # append the shorter block to new genned lines
                if mod_i2 < gen_i2:
                    output_file_temp += vanilla_text[cur_v:mod_i2]
                    cur_v = mod_i2
                    van_mod_ops.pop(0)
                else:
                    output_file_temp += vanilla_text[cur_v:gen_i2]
                    cur_v = gen_i2
                    van_gen_ops.pop(0)
                    if mod_i2 == gen_i2 :
                        van_mod_ops.pop(0)
            # otherwise append current genned lines
            else:
                output_file_temp += gen_text[gen_j1:gen_j2]
                cur_v = gen_i2
                van_gen_ops.pop(0)
                if mod_i2 == gen_i2 :
                    van_mod_ops.pop(0)
        # if mod has changes from vanilla
        else:
            # if no earlier mod changed this section, adopt these changes
            if gen_tag == 'equal':
                output_file_temp += mod_text[mod_j1:mod_j2]
                cur_v = mod_i2
                van_mod_ops.pop(0)
                if mod_i2 == gen_i2 :
                    van_gen_ops.pop(0)
            # if the changes would overlap, we can't handle that yet
            else:
                # we'll revisit this later, to allow overlapping merges
                # (important for graphics pack inclusion)
                # probably have to return (status, lines) tuple.
                return ''
    # clean up trailing opcodes, to avoid dropping the end of the file
    if van_mod_ops:
        mod_tag, mod_i1, mod_i2, mod_j1, mod_j2 = van_mod_ops[0]
        output_file_temp += mod_text[mod_j1:mod_j2]
    if van_gen_ops:
        gen_tag, gen_i1, gen_i2, gen_j1, gen_j2 = van_gen_ops[0]
        output_file_temp += gen_text[gen_j1:gen_j2]
    return output_file_temp

def get_lines_from_file(filename):
    """Get lines from a file, managing encoding.
        Trying to merge files with diferent encoding causes errors;
        a strict encoding often merges but at worst produces known issues.
        Unicode handling changed a lot between versions...
        TODO:  test and improve this function!
    """
    if sys.version_info[0] == 3: # Python 3.4 works for me
        return open(filename, encoding='utf-8', errors='ignore').readlines()
    else: # Forget handling encoding and hope for the best
        return open(filename).readlines()

def do_merge_files(mod_file_name, van_file_name, gen_file_name):
    ''' calls merge sequence on the files, and returns true if they could be (and were) merged
        or false if the merge was conflicting (and thus skipped).
    '''
    van_lines = get_lines_from_file(van_file_name)
    mod_lines = get_lines_from_file(mod_file_name)
    gen_lines = []
    if os.path.isfile(gen_file_name):
        gen_lines = get_lines_from_file(gen_file_name)        

    gen_lines = do_merge_seq(mod_lines, van_lines, gen_lines)
    if gen_lines:
        gen_file = open(gen_file_name,"w")
        for line in gen_lines:
            gen_file.write(line)
        return True
    else:
        return False

def merge_a_mod(mod):
    '''Merges the specified mod, and returns status (0|1|2|3) like an exit code.

        0:  Merge was successful, all well
        1:  Potential compatibility issues, no merge problems
        2:  Non-fatal error, overlapping lines or non-existent mod etc
        3:  Fatal error, respond by rebuilding to previous mod'''
    mod_raw_folder = os.path.join(mods_folder, mod, 'raw')
    if not os.path.isdir(mod_raw_folder):
        return 2
    status = merge_raw_folders(mod_raw_folder, vanilla_raw_folder)
    if status < 2:
        with open(os.path.join(mods_folder, 'temp', 'raw', 'installed_mods.txt'), 'a') as log:
            log.write(mod + '\n')
    return status

def merge_raw_folders(mod_raw_folder, vanilla_raw_folder):
    '''Behind the wrapper, to allow tricks by overriding the global variables'''
    status = 0
    for file_tuple in os.walk(mod_raw_folder):
        for item in file_tuple[2]:
            file = os.path.join(file_tuple[0], item)
            file = os.path.relpath(file, mod_raw_folder)
            if os.path.isfile(os.path.join(vanilla_raw_folder, file)):
                if not do_merge_files(os.path.join(mod_raw_folder, file), 
                                      os.path.join(vanilla_raw_folder, file), 
                                      os.path.join(mixed_raw_folder, file)):
                    return 3
            elif os.path.isfile(os.path.join(mixed_raw_folder, file)):
                return 3
            else:
                shutil.copy(os.path.join(mod_raw_folder, file), 
                            os.path.join(mixed_raw_folder, file))
                status = 1
    return status

def clear_temp():
    global mixed_raw_folder, vanilla_raw_folder
    mixed_raw_folder = os.path.join(mods_folder, 'temp', 'raw')
    if os.path.exists(os.path.join(mods_folder, 'temp')):
        shutil.rmtree(os.path.join(mods_folder, 'temp'))
    shutil.copytree(vanilla_raw_folder, mixed_raw_folder)
    with open(os.path.join(mods_folder, 'temp', 'raw', 'installed_mods.txt'),
              'w') as log:
        log.write('# List of mods merged by PyLNP mod loader\n' + 
                  os.path.dirname(vanilla_raw_folder)[:-4] + '\n')

def read_mods():
    """Returns a list of mod packs"""
    # should go in tkgui/mods.py later
    return [os.path.basename(o) for o in
            glob.glob(os.path.join(paths.get('mods'), '*'))
            if os.path.isdir(o) and not os.path.basename(o)=='temp']

def init_paths(lnpdir):
    global mods_folder, mods_folders_list, vanilla_folder, vanilla_raw_folder, installed_raw_folder
    raws.simplify_mods()
    installed_raw_folder = os.path.join(paths.get('df'), 'raw')
    mods_folder = os.path.join(lnpdir, 'Mods')
    vanilla_raw_folder = raws.find_vanilla_raws(version=None)
    mod_folders_list = read_mods()
    clear_temp()

def make_mod_from_installed_raws(name):
    '''Capture whatever unavailable mods a user currently has installed as a mod called $name.

        * If `installed_mods.txt` is not present, compare to vanilla
        * Otherwise, rebuild as much as possible then compare installed and rebuilt
        * Harder than I first thought... but not impossible'''
    mod_load_order = get_installed_mods_from_log()
    if mod_load_order:
        clear_temp()
        for mod in mod_load_order:
            merge_a_mod(mod)
        best_effort_reconstruction = os.path.join(mods_folder, 'temp2', 'raw')
        shutil.copytree(os.path.join(mods_folder, 'temp', 'raw'),
                        os.path.join(mods_folder, 'temp2', 'raw'))
    else:
        best_effort_reconstruction = vanilla_raw_folder

    clear_temp()
    merge_raw_folders(best_effort_reconstruction, installed_raw_folder)
    simplify_mod_folder('temp')
    if os.path.isdir(os.path.join(mods_folder, 'temp2')):
        shutil.rmtree(os.path.join(mods_folder, 'temp2'))

    if os.path.isdir(os.path.join(mods_folder, 'temp')):
        if not name or os.path.isdir(os.path.join(mods_folder, name)):
            name = 'Extracted Mod at '+str(int(time.time()))
        shutil.copytree(os.path.join(mods_folder, 'temp'), os.path.join(mods_folder, name))
        return_val = 'User unique mods extracted as "'+str(name)+'"'
        return return_val
    else:
        return 'No unique user mods found.'

def get_installed_mods_from_log():
    '''Return best possible mod load order to recreate installed with available'''
    logged = read_installation_log(os.path.join(installed_raw_folder, 'installed_mods.txt'))
    # return list overlap - like set intersection, but ordered
    return [mod for mod in logged if mod in mods_folders_list]

def read_installation_log(file):
    '''Read an 'installed_mods.txt' and return it's full contents.'''
    try:
        with open(file) as f:
            file_contents = list(f.readlines())
    except IOError:
        return []
    mods_list = []
    for line in file_contents:
        if not line.strip() or line.startswith('#'):
            continue
        mods_list.append(line.strip())
    return mods_list

mods_folder = os.path.join('LNP', 'Mods')
vanilla_folder = ''
vanilla_raw_folder = ''
mixed_raw_folder = ''
mod_folders_list = read_mods()
