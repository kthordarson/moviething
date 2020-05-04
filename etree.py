from collections import defaultdict

from lxml import etree

TYPE_MAP = dict(
    int=int,
    bytes=bytes,
    NoneType=lambda x: None,
    list=list,
    bool=bool,
    str=str,
)

NoneType = type(None)


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


def element(k, v):
    """ key, val --> etree.Element(key)
    """

    node = etree.Element(k)

    if isinstance(v, dict):
        for ck, cv in v.items():
            node.append(element(ck, cv))
    elif isinstance(v, str):
        # node.set('type', type(v).__name__)
        node.text = v  # .encode('utf8')
    elif isinstance(v, (int, float, bool, str, NoneType)):  # scalar
        # node.set('type', type(v).__name__)
        node.text = str(v)
    elif isinstance(v, list):
        # node.set('type', type(v).__name__)  # list xx this could be done across the board.
        for cv in v:
            node.append(element('item',
                                cv))  # node.append(element("item", cv))  # node.append(element("_list_element_%d" % i, cv))
    else:
        assert False

    return node


def value(e):
    """ etree.Element --> value
    """

    children = e.getchildren()

    typ = e.get('type')
    if children:
        if not typ:  # xx defaults dict
            return dict((c.tag, value(c)) for c in children)
        elif typ == 'list':
            return [value(c) for c in children]
        else:
            raise TypeError('unexpected type', typ)

    # convert it back to the right python type
    ctor = TYPE_MAP[typ]
    return ctor(e.text)


def xpath(val, xp):
    for node in element('root', val).xpath(xp):
        yield value(node)
