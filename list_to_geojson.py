import simplejson as json
import geojson


def list_to_geojson(record_list):
    features = []
    for n, record in enumerate(record_list):
        prop = dict(record)
        id = prop.pop('id')
        geom = geojson.Point([prop.pop('lon'), prop.pop('lat')])
        features.append(geojson.Feature(id=id, geometry=geom, properties=prop))
    return geojson.FeatureCollection(features)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            exclude_list = f.read().split()
    records = [r for r in json.load(sys.stdin) if r['id'] not in exclude_list]
    doc = list_to_geojson(records)
    geojson.dump(doc, sys.stdout, indent=2)
