# onvif/utils/zeep.py

from lxml.etree import QName
from zeep.xsd.elements.any import Any
from zeep.xsd.utils import max_occurs_iter


def patched_parse_xmlelements(self, xmlelements, schema, name=None, context=None):
    """Patched version of parse_xmlelements for <xsd:any> to support child parsing."""
    parsed_result = {}

    for _ in max_occurs_iter(self.max_occurs):
        if not xmlelements:
            break

        xmlelement = xmlelements.popleft()
        tag_name = QName(xmlelement.tag).localname
        children = list(xmlelement)

        if children and schema:
            child_result = {}
            for child in children:
                child_qname = QName(child.tag)
                try:
                    xsd_el = schema.get_element(child_qname)
                    val = xsd_el.parse_xmlelement(
                        child, schema=schema, allow_none=True, context=context
                    )
                    child_result[child_qname.localname] = val
                except Exception:
                    if list(child):  # has nested children
                        nested = {
                            QName(sub.tag).localname: sub.text or sub
                            for sub in child
                        }
                        child_result[child_qname.localname] = nested
                    else:
                        child_result[child_qname.localname] = child.text or child

            parsed_result[tag_name] = child_result
        else:
            parsed_result[tag_name] = xmlelement.text or xmlelement

    return parsed_result


def apply_patch():
    """Inject the custom parse_xmlelements method into zeep.xsd.elements.any.Any."""
    Any.parse_xmlelements = patched_parse_xmlelements