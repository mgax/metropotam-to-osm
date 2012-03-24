import lxml.etree


def parse_metropotam_xml(xml_file):
    doc = lxml.etree.parse(xml_file)
    for location in doc.iter('location'):
        print location.attrib['name']
        for coord in location.iter('coord'):
            print '  ', coord.attrib['lat'], coord.attrib['lng']


def main():
    import sys
    parse_metropotam_xml(sys.stdin)


if __name__ == '__main__':
    main()
