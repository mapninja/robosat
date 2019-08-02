import sys

import osmium
import geojson
import shapely.geometry

from robosat.osm.core import FeatureStorage, is_polygon


class VillageHandler(osmium.SimpleHandler):
    """Extracts Village features (visible in satellite imagery) from the map.
    """

    # parking=* to discard because these features are not vislible in satellite imagery
    village_filter = set(["yes"])

    def __init__(self, out, batch):
        super().__init__()
        self.storage = FeatureStorage(out, batch)

    def way(self, w):
        if not is_polygon(w):
            return

        if "place" not in w.tags or w.tags["place"] != "village":
            return

        if "abandoned" in w.tags:
            if w.tags["abandoned"] in self.parking_filter:
                return

        geometry = geojson.Polygon([[(n.lon, n.lat) for n in w.nodes]])
        shape = shapely.geometry.shape(geometry)

        if shape.is_valid:
            feature = geojson.Feature(geometry=geometry)
            self.storage.add(feature)
        else:
            print("Warning: invalid feature: https://www.openstreetmap.org/way/{}".format(w.id), file=sys.stderr)

    def flush(self):
        self.storage.flush()
