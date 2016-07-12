# gl-style-schema

Dump the vector tile schema defined in a [TileJSON spec](https://github.com/mapbox/tilejson-spec)
or as required by [Mapbox GL style JSON](https://github.com/mapbox/mapbox-gl-style-spec).

Use Cases:
- Compare used schema in style vs provided schema (check how much of the schema you actually use)
- Compare two different vector tile sets
- Compare schema required by multiple styles

## Usage

```bash
# Dump schema required by a Mapbox GL style
wget "https://raw.githubusercontent.com/osm2vectortiles/mapbox-gl-styles/master/styles/bright-v9-cdn.json"
./gl-style-schema.py bright-v9-cdn.json

# Dump schema as defined in TileJSON
wget "https://osm2vectortiles.tileserver.com/v2.json"
./gl-style-schema.py v2.json
```

## Output

Layers are denoted with `#layer` and fields with `[field]`.

```css
#admin
  [admin_level]
  [disputed]
  [maritime]
#aeroway
  [type]
#airport_label
  [scalerank]
#country_label
  [scalerank]
#landuse
  [class]
#landuse_overlay
  [class]
#marine_label
  [labelrank]
```

## Compare

Compare the vector tile schema of [OSM2VectorTiles](osm2vectortiles.org) with [Mapbox Streets](https://www.mapbox.com/vector-tiles/mapbox-streets-v7/).

```bash
# TileJSON URLs
MBSTREETS_TILEJSON="http://api.mapbox.com/v4/mapbox.mapbox-streets-v7.json?access_token=pk.eyJ1IjoibW9yZ2Vua2FmZmVlIiwiYSI6IjIzcmN0NlkifQ.0LRTNgCc-envt9d5MzR75w"
OSMVT_TILEJSON="https://osm2vectortiles.tileserver.com/v2.json"

# Dump schemas
curl $MBSTREETS_TILEJSON | ./gl-style-schema.py > mapbox-streets-v7.schema
curl $OSMVT_TILEJSON | ./gl-style-schema.py > osm2vectortiles-v2.schema

# Compare schemas
diff -c mapbox-streets-v7.schema osm2vectortiles-v2.schema
```
