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
    doc = list_to_geojson(json.load(sys.stdin))
    geojson.dump(doc, sys.stdout, indent=2)
