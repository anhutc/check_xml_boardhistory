def validate_xml(xml_string):
    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(xml_string)
        return True
    except ET.ParseError:
        return False

def format_string(input_string):
    return input_string.strip().title()