"""
"""
import json

import pandas as pd


class JSON:
    """
    """
    def __init__(self):
        self.read_linjer()
    
    def read_linjer(self):
        """
        """
        with open('linjer.json', 'r') as file:
            self.linjer = json.load(file)
    
    def read_tunnelbana(self):
        """
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
        """
        """
        with open('OSM_exports/railway_stations.json', 'r') as file:
            data = json.load(file)
            data = data['features']

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
        
        # Add Uppsala C station as OSM export did not inlcude it.
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
        """
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

        # Replace station
        df = df.replace('Torsvik/Millesgården', 'Torsvik')

        # Some stations have stops for both directions. The mid-point of 
        # these is taken.
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
        """
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
                indent=4
            )
            

if __name__ == "__main__":
    j = JSON()
    j.write_JSON()