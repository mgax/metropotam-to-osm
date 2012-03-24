import simplejson as json
import lxml.etree


def parse_metropotam_xml(xml_file):
    doc = lxml.etree.parse(xml_file)
    for location in doc.iter('location'):
        for coord in location.iter('coord'):
            yield {
                'name': location.attrib['name'],
                'lat': float(coord.attrib['lat']),
                'lon': float(coord.attrib['lng']),
                'type': location.attrib['type'],
            }


def main():
    import sys
    data = list(parse_metropotam_xml(sys.stdin))
    json.dump(data, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
