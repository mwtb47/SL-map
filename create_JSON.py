import json

import pandas as pd


class JSON:
    """Class to create JSON file with SL rail network information.
    
    Data on tunnelbana, pendeltåg and spårvagn/lokalbana stations 
    exported from OpenStreetMap using overpass turbo is cleaned to 
    produce a JSON file containing information on line, their stations 
    and the location of those stations.
    """
    def __init__(self):
        self.read_linjer()

    def read_linjer(self):
        """Read JSON file with stations on each rail/metro line."""
        with open('linjer.json', 'r') as file:
            self.linjer = json.load(file)

    def read_tunnelbana(self):
        """Create dictionary of tunnelbana stations and locations.

        Read overpass turbo export data containing pendeltåg stations
        and their latitudes and longitudes. Create a dictionary with
        this information for all stations on each line.

        Returns
            Dictionary with lines as keys and a dictionary of stations
            and station locations as values.
        """
        with open('OSM_exports/tunnelbana.json', 'r') as file:
            data = json.load(file)
            data = data['features']

        stations = []
        lat = []
        lon = []
        for station in data:
            stations.append(station['properties']['name'])
            lat.append(station['geometry']['coordinates'][1])
            lon.append(station['geometry']['coordinates'][0])

        df = pd.DataFrame({'station': stations, 'lat': lat, 'lon': lon})

        # Remove second Tensta station
        df = df.drop(df[
            (df['lat'] == 59.3938983) & (df['lon'] == 17.9040828)].index)

        stations = {}
        for linje, stationer in self.linjer['tunnelbana'].items():
            stations[linje] = {
                station: {
                    'latitude': df.loc[
                        df['station'] == station, 'lat'].values[0],
                    'longitude': df.loc[
                        df['station'] == station, 'lon'].values[0],
                } for station in stationer
            }
        return stations

    def read_pendeltåg(self):
        """Create dictionary of tunnelbana stations and locations.

        Read overpass turbo export data containing pendeltåg stations
        and their latitudes and longitudes. Create a dictionary with
        this information for all stations on each line.

        Returns
            Dictionary with lines as keys and a dictionary of stations
            and station locations as values.
        """
        with open('OSM_exports/railway_stations.json', 'r') as file:
            data = json.load(file)
            data = data['features']

        # The overpass turbo query to capture all pendeltåg stations
        # also captured other stations which are filtered out.
        stations = []
        lat = []
        lon = []
        for station in data:
            if ('railway' in station['properties']
                and 'station' not in station['properties']):
                stations.append(station['properties']['name'])
                lat.append(station['geometry']['coordinates'][1])
                lon.append(station['geometry']['coordinates'][0])

        df = pd.DataFrame({'station': stations, 'lat': lat, 'lon': lon})

        # Rename stations to match names in linjer.json.
        df = df.replace(
            {
                'Arlanda central': 'Arlanda C',
                'Södertälje centrum': 'Södertälje C'
            }
        )

        # Add Uppsala C station as OSM export did not include it.
        df = df.append(
            {
                'station': 'Uppsala C',
                'lat': 59.85821,
                'lon':  17.64658
            },
            ignore_index=True
        )

        stations = {}
        for linje, stationer in self.linjer['pendeltåg'].items():
            stations[linje] = {
                station: {
                    'latitude': df.loc[
                        df['station'] == station, 'lat'].values[0],
                    'longitude': df.loc[
                        df['station'] == station, 'lon'].values[0],
                } for station in stationer
            }
        return stations

    def read_spårvagn(self):
        """Create dictionary of spårvagn stations and locations.

        Read overpass turbo export data containing spårvagn and
        lokalbana stations and their latitudes and longitudes. Create
        a dictionary with this information for all stations on each
        line.

        While linje 25 and linje 26 are classed as lokalbana, OSM does
        not class the stations this way therefore they must be extracted
        from railway_stations.json.

        Returns
            Dictionary with lines as keys and a dictionary of stations
            and station locations as values.
        """
        with open('OSM_exports/spårvagn_lokalbana.json', 'r') as file:
            data = json.load(file)
            data = data['features']

        stations = []
        lat = []
        lon = []
        for station in data:
            stations.append(station['properties']['name'])
            lat.append(station['geometry']['coordinates'][1])
            lon.append(station['geometry']['coordinates'][0])

        df = pd.DataFrame({'station': stations, 'lat': lat, 'lon': lon})

        # Replace station name to match linjer.json.
        df = df.replace('Torsvik/Millesgården', 'Torsvik')

        # Some stations have stops each direction of travel. The
        # mid-point of these is taken.
        df = df.groupby('station', as_index=False).agg({'lat': 'mean',
                                                        'lon': 'mean'})

        stations = {}
        for linje, stationer in self.linjer['spårvagn_lokalbana'].items():
            if linje not in ['Linje 25', 'Linje 26']:
                stations[linje] = {
                    station: {
                        'latitude': df.loc[
                            df['station'] == station, 'lat'].values[0],
                        'longitude': df.loc[
                            df['station'] == station, 'lon'].values[0],
                    } for station in stationer
                }
        return stations

    def read_saltsjöbanan(self):
        """Create dictionary of Saltsjöbanan stations and locations.

        Read overpass turbo export data containing Saltsjöbanan stations
        and their latitudes and longitudes. Create a dictionary with this
        information for all stations on each line.

        Returns
            Dictionary with lines as keys and a dictionary of stations
            and station locations as values.
        """
        with open('OSM_exports/railway_stations.json', 'r') as file:
            data = json.load(file)
            data = data['features']

        stations = []
        lat = []
        lon = []
        for station in data:
            stations.append(station['properties']['name'])
            lat.append(station['geometry']['coordinates'][1])
            lon.append(station['geometry']['coordinates'][0])

        df = pd.DataFrame({'station': stations, 'lat': lat, 'lon': lon})

        stations = {}
        for linje, stationer in self.linjer['spårvagn_lokalbana'].items():
            if linje in ['Linje 25', 'Linje 26']:
                stations[linje] = {
                    station: {
                        'latitude': df.loc[
                            df['station'] == station, 'lat'].values[0],
                        'longitude': df.loc[
                            df['station'] == station, 'lon'].values[0],
                    } for station in stationer
                }
        return stations

    def write_JSON(self):
        """Write dictionaries to a JSON file.

        Combine the spårvagn and Saltsjöbanan dictionaries and then
        create a new dictionary with each type of network as a key, and
        their respective dictionaries as the values. Save this
        dictionary as a JSON file.
        """
        tunnelbana = self.read_tunnelbana()
        pendeltåg = self.read_pendeltåg()
        spårvagn = self.read_spårvagn()
        saltsjöbanan = self.read_saltsjöbanan()

        # Combine the two dictionaries and sort keys by line name.
        spårvagn.update(saltsjöbanan)
        spårvagn = dict(sorted(spårvagn.items(),
                               key=lambda x: int(x[0].split(' ')[1])))

        linjer_och_stationer = {}
        linjer_och_stationer['tunnelbana'] = tunnelbana
        linjer_och_stationer['pendeltåg'] = pendeltåg
        linjer_och_stationer['spårvagn_lokalbana'] = spårvagn

        with open('linjer_och_stationer.json', 'w') as file:
            json.dump(
                linjer_och_stationer,
                file,
                ensure_ascii=False,
                indent=2
            )


if __name__ == "__main__":
    j = JSON()
    j.write_JSON()
