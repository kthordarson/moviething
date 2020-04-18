# xml parsing
import os
import re
import time
import hashlib
import requests
import platform
import sys
import codecs
import unidecode
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


class MovieClass(object):
    def __init__(self, filename):
        self.filename = filename


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''

    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


def read_xml(file):
    # read xml, return structured movie info or None if failed
    data = None
    xml_file = open(file, encoding='utf-8', errors='ignore')
    xml_data = xml_file.readlines()
    xml_file.close()
    root = ET.parse(file).getroot()
    children = list(root)
    for subchild in children:
        print(subchild.tag, subchild.text)
        if len(list(subchild)) > 1:
            for k in list(subchild):
                print(f'\t{k.tag}: {k.text}')

    return data


def get_xml_dict(file):
    tree = ET.parse(source=file)
    root = tree.getroot()
    xmldict = XmlDictConfig(root)
    # print(xmldict)
    return xmldict

def get_xml_config(file):
    xml_file = open(file, encoding='utf-8', errors='ignore')
    xml_data = xml_file.read()
    xml_file.close()
    root = ET.fromstring(xml_data)
    xml_config = XmlListConfig(root)
    print(xml_config)
