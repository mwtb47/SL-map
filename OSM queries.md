# OpenStreetMap - overpass turbo Queries

The JSON files in the OSM_exports folder can be produced using the following 
queries at [overpass turbo](https://overpass-turbo.eu) and then exporting the 
GeoJSON outputs as a JSON files. 

### Tunnelbana
```
[out:json]
[bbox:59.2,17.75,59.45,18.15];
node["station"="subway"];
out body;
```

### Railway Stations
```
[out:json]
[bbox:58.85,17.3,59.92,18.36];
node["public_transport"="station"];
out body;
```

### Spårvagn/Lokalbana
```
[out:json]
[bbox:58.25,17.85,59.7,18.4];
(
  node["network"="Tvärbanan"];
  node["station"="light_rail"];
  node["railway"="tram_stop"];
);
out body;
```