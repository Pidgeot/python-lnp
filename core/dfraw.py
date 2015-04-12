#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Modification of Dwarf Fortress raw files."""
from __future__ import print_function, unicode_literals, absolute_import
import io
import re
import sys
import os
from fnmatch import fnmatch

if sys.version_info[0] == 3:
    #pylint: disable=redefined-builtin
    basestring = str

NODE_COMMENT = 1 << 1
NODE_TAG = 1 << 2
NODE_ROOT = 1 << 3

# These are glob patterns - * represents an arbitrary string
object_parents = {
    'BODY': ['BODY'],
    'BUILDING': ['BUILDING_*'],
    'BODY_DETAIL_PLAN': ['BODY_DETAIL_PLAN'],
    'CREATURE': ['CREATURE'],
    'CREATURE_VARIATION': ['CREATURE_VARIATION'],
    'DESCRIPTOR': ['COLOR', 'SHAPE'], #40d and earlier
    'DESCRIPTOR_COLOR': ['COLOR'],
    'DESCRIPTOR_PATTERN': ['PATTERN'],
    'DESCRIPTOR_SHAPE': ['SHAPE'],
    'ENTITY': ['ENTITY'],
    'GRAPHICS': ['TILE_PAGE', 'CREATURE_GRAPHICS'],
    'INORGANIC': ['INORGANIC'],
    'INTERACTION': ['INTERACTION'],
    'ITEM': ['ITEM_*'],
    'LANGUAGE': ['TRANSLATION', 'SYMBOL', 'WORD'], # TODO: Maybe add NOUN, etc?
    'MATERIAL_TEMPLATE': ['MATERIAL_TEMPLATE'],
    'MATGLOSS': ['MATGLOSS_*'], #40d and earlier
    'PLANT': ['PLANT'],
    'REACTION': ['REACTION'],
    'TISSUE_TEMPLATE': ['TISSUE_TEMPLATE'],
}

init_filename_parents = {
    'embark_profiles.txt': ['PROFILE'],
    'interface.txt': ['BIND'], #Legacy doesn't use BIND, will be flat
    'world_gen.txt': ['WORLD_GEN'],
}

# Do not allow parent tags to go under these tags
final_level_tags = ['TILE_PAGE']

def tokenize_raw(text):
    """Generator which returns nodes from a raw file.

    Params:
        text
            Text of the raw file to parse.
    Returns:
        (kind, token)
            kind
                "Tag" or "Comment"
            token
                Token text (including any delimiters)"""
    while text:
        curr_string = ''
        if text[0] == '[':
            if ']' not in text:
                raise Exception('Found non-terminated tag: '+text[0:100])
            curr_string = text[:text.find(']')+1]
            node_type = 'Tag'
        if text[0] == '!':
            match = re.match('!\\w+!', text)
            if match:
                curr_string = match.group()
                node_type = 'Tag'
        if not curr_string:
            if '[' in text:
                curr_string = text[:text.find('[')]
            else:
                curr_string = text
            #check for
            match = re.search('!\\w+!', text)
            if match:
                curr_string = curr_string[:match.start()]
            node_type = 'Comment'
        text = text[len(curr_string):]
        yield node_type, curr_string


def parse_raw(parent, text):
    """Parses the raw text contained in <text> and places resulting nodes in a
    tree under <parent>."""
    path, fname = os.path.split(os.path.abspath(parent.filename))
    path = path.split(os.sep)
    parent_tags = []
    parent_stack = [parent]
    # Parent tags for raw/{graphics, objects} are handled later
    if path[-1] == 'init':
        parent_tags = init_filename_parents.get(fname, [])
    for kind, token in tokenize_raw(text):
        if kind == 'Tag':
            contents = token[1:-1]
            if ':' in contents:
                name, value = contents.split(':', 1)
            else:
                name, value = contents, token[0] == '['
            is_parent = False
            for g in parent_tags:
                if fnmatch(name, g):
                    is_parent = True
                    while (parent_stack[-1].name in final_level_tags or
                           any([fnmatch(p.name, g) for p in parent_stack])):
                        parent_stack.pop()
            node = DFRawTag(parent_stack[-1], name, value)
            if is_parent:
                parent_stack.append(node)
            if path[-2] == 'raw' and name == 'OBJECT':
                parent_tags = object_parents[value]
        elif kind == 'Comment':
            DFRawComment(parent_stack[-1], token)
        else:
            raise Exception('Unknown raw token kind: '+kind)

class DFRawNode(object):
    """Class representing a node in a raw file."""
    def __init__(self, parent, node_id, value, node_type, **kwargs):
        """Constructor for DFRawNode.

        Parameters:
            parent
                Parent node.
            node_id
                Identifier for the node (e.g. field name)
            value
                The complete string value for this node (no splitting).
            node_type
                Indicates the node type for queries (e.g. NODE_TAG)

        Keyword arguments:
            after
                If None, the node is inserted as the first child. Otherwise, it
                is inserted after the child node provided in this argument.
                If omitted, or if the provided child node does not exist, the
                child is added as the last child."""
        self.name = node_id
        self.__parent = None
        self.__type = node_type
        if self.is_tag:
            if value:
                self.__value = value
            else:
                self.__value = None
        else:
            self.__value = value
        self.children = []
        if parent:
            parent.add_child(self, **kwargs)

    def add_child(self, child, **kwargs):
        """Adds <child> to the list of child nodes and sets its parent to this
        node. If <child> already has another parent, it is first removed from
        that parent. Has no effect if <child> is a root node.

        Params:
            child
                The child node to add.

        Keyword arguments:
            after
                If None, the node is inserted as the first child. Otherwise, it
                is inserted after the child node provided in this argument.
                If omitted, or if the provided child node does not exist, the
                child is added as the last child."""
        if child.is_root:
            return
        if 'after' in kwargs:
            if kwargs['after'] is not None:
                try:
                    self.children.insert(
                        self.children.index(kwargs['after']), child)
                    return
                except ValueError:
                    self.children.append(child)
            else:
                self.children.insert(0, child)
        self.children.append(child)
        if child.parent is not self and child.parent is not None:
            child.parent.remove_child(child)
        # pylint: disable=protected-access
        child.__parent = self

    def remove_child(self, child):
        """Removes <child> as a child node and sets its parent to None."""
        if self.is_root:
            return
        self.children.remove(child)
        # pylint: disable=protected-access
        child.__parent = None

    @property
    def is_root(self):
        """Returns True if this is the root node for a raw file."""
        return (self.__type & NODE_ROOT) == NODE_ROOT

    @property
    def is_comment(self):
        """Returns True if this is a comment node."""
        return (self.__type & NODE_COMMENT) == NODE_COMMENT

    @property
    def is_tag(self):
        """Returns True if this node represents a tag."""
        return (self.__type & NODE_TAG) == NODE_TAG and not self.is_root

    @property
    def is_flag(self):
        """Returns True if this node represents a flag (has no values)."""
        return (self.__type & NODE_TAG) and isinstance(self.__value, bool)

    @property
    def is_container(self):
        """Returns True if this node represents a container (has children)."""
        return (self.__type & NODE_TAG) and self.children

    @property
    def parent(self):
        """Returns the parent for this node, or itself if this is the root."""
        return self if self.is_root else self.__parent

    @property
    def root(self):
        """Returns the root node."""
        return self if self.is_root else self.__parent.root

    @property
    def filename(self):
        """Returns the filename for this raw file."""
        # pylint: disable=protected-access
        return self.root.__value

    @property
    def value(self):
        """Returns the unparsed value for this node."""
        return self.__value

    @value.setter
    def value(self, value):
        """Sets the value of this node. Multiple values may be passed for tag
        nodes, in the form of a list or tuple."""
        if isinstance(value, (list, tuple)):
            if self.is_tag:
                value = ':'.join(value)
            else:
                raise Exception('Multiple values passed to non-tag node')
        if value == self.__value:
            return
        self.__value = value
        #pylint: disable=protected-access
        self.root._modified = True

    @property
    def values(self):
        """Returns a list of values associated with this node."""
        if self.is_tag and not self.is_flag:
            return self.value.split(':')
        return [self.value,]

    @property
    def text(self):
        """Returns the text for this node."""
        if self.is_root:
            return ''
        elif self.is_comment:
            return self.__value
        elif self.is_flag:
            if self.__value:
                return '[{0}]'.format(self.name)
            else:
                return '!{0}!'.format(self.name)
        else:
            return '[{0}:{1}]'.format(self.name, self.value)

    @property
    def fulltext(self):
        """Returns the text for this node and all its children."""
        child_contents = ''
        for c in self.children:
            child_contents += c.fulltext
        return self.text + child_contents

    @property
    def elements(self):
        """Generator producing a flat view of this node and its subnodes.
        Yields raw nodes."""
        for c in self.children:
            yield c
            for c2 in c.elements:
                yield c2

    def __str__(self):
        return self.text

    def find_first(self, field):
        """Returns the first child node with the tag name field, or None if no
        such node exists."""
        for c in self.children:
            if c.name == field:
                return c
            child_result = c.find_first(field)
            if child_result is not None:
                return child_result
        return None

    def find_all(self, field):
        """Returns a list of all child nodes with the tag name field."""
        result = []
        for c in self.children:
            if c.name == field:
                result.append(c)
            result += c.find_all(field)
        return result

class DFRaw(DFRawNode):
    """Represents a Dwarf Fortress raw file."""
    def __init__(self, path):
        """Constructor for DFRaw.

        Params:
            path
                Path to the raw file that should be parsed."""
        super(DFRaw, self).__init__(None, '*ROOT*', path, NODE_ROOT)
        self._modified = False
        self.__parse()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and self._modified:
            self.save()

    @staticmethod
    def open(path, mode):
        """
        Opens a raw file at <path> with mode <mode> and returns a stream.

        Params:
            path
                Path to raw file
            mode
                File mode (see io.open), typically 'rt' or 'wt'
        """
        return io.open(path, mode, encoding='cp437', errors='replace')

    @classmethod
    def read(cls, path):
        """Returns the contents of the raw file at <path>."""
        with cls.open(path, 'rt') as fd:
            return fd.read()

    @classmethod
    def write(cls, path, text):
        """Writes <text> to a raw file located at <path>."""
        with cls.open(path, 'wt') as fd:
            return fd.write(text)

    def save(self):
        """Re-writes the current raw file, saving all changes."""
        with self.open(self.filename, 'wt') as fd:
            for node in self.elements:
                fd.write(node.text)

    def __parse(self):
        """Parses a raw file into tokens and builds an appropriate hierarchy
        based on the file path."""
        # raw/objects: detect name, type, use major tag for type as parent node
        # raw/graphics: as object raw, but add TILE_PAGE
        # init: usually flat file, except
        #   embark_profiles.txt: [PROFILE] is parent
        #   interface.txt: [BIND] is parent (legacy will be flat)
        #   world_gen.txt: [WORLD_GEN] is parent
        # Non-raw files (unsupported): init/arena.txt, subdirs of raw/objects
        parse_raw(self, self.read(self.filename))

    def set_all(self, field, value):
        """Sets all tags named <field> to <value>."""
        fields = self.find_all(field)
        for f in fields:
            f.value = value

    def set_value(self, field, value):
        """Sets the first tag named <field> to <value>."""
        field = self.find_first(field)
        if field is not None:
            field.value = value

    def get_value(self, field):
        """Gets the value of the first tag named <field>. Returns None if no
        such field exists."""
        field = self.find_first(field)
        if field is not None:
            return field.value
        return None

    def get_values(self, *fields):
        """Returns the values of <fields> in a list. The nesting and order of
        the resulting list will match the nesting and order of <fields>.
        Equivalent to calling get_value for each field."""
        result = []
        for field in fields:
            if isinstance(field, (str, basestring)):
                result.append(self.get_value(field))
            elif isinstance(field, (tuple, list)):
                result.append(self.get_values(*field))
            else:
                result.append(None)
        return result

class DFRawTag(DFRawNode):
    """Represents a tag in a raw file."""
    def __init__(self, parent, tag, value):
        """Constructor for DFRawTag.

        Params:
            parent
                Parent node.
            tag
                Name of the tag.
            value
                Value for this tag (True/False for flags)"""
        super(DFRawTag, self).__init__(parent, tag, value, NODE_TAG)

class DFRawComment(DFRawNode):
    """Represents a comment (non-tag) in a raw file."""
    def __init__(self, parent, text):
        """Constructor for DFRawComment.

        Params:
            parent
                Parent node.
            text
                Text for this comment."""
        super(DFRawComment, self).__init__(
            parent, '**COMMENT**', text, NODE_COMMENT)
