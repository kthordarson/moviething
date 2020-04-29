
from collections import defaultdict
import os
import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def etree_get_dchildren(children):
    dd = defaultdict(list)
    for dc in map(etree_to_dict, children):
        for k, v in dc.items():
            dd[k].append(v)
    return dd


def etree_to_dict(t):
    # from https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = etree_get_dchildren(children)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update((k, v)  # d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d
