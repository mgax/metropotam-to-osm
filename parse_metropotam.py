import lxml.etree


def parse_metropotam_xml(xml_file):
    doc = lxml.etree.parse(xml_file)
    for location in doc.iter('location'):
        out = {'name': location.attrib['name'], 'coord': []}
        for coord in location.iter('coord'):
            out['coord'].append({
                'lat': float(coord.attrib['lat']),
                'lng': float(coord.attrib['lng']),
            })
        yield out


def main():
    import sys
    from pprint import pprint
    for location in parse_metropotam_xml(sys.stdin):
        pprint(location)


if __name__ == '__main__':
    main()
