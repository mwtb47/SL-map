"""
"""
import json

import plotly.graph_objects as go

import config


class Karta:
    """
    """
    def __init__(self):
        pass
    
    def read_data(self):
        """
        """
        with open('linje_information.json', 'r') as file:
            self.linje_information = json.load(file)
        
        with open('linjer_och_stationer.json', 'r') as file:
            self.stationer = json.load(file)
            
        
    def plot_map(self):
        """
        """
        mapbox_access_token = config.mapbox_access_token
        
        tunnelbana = self.stationer['tunnelbana']
        pendeltåg = self.stationer['pendeltåg']
        spårvagn = self.stationer['spårvagn_lokalbana']
        
        fig = go.Figure()

        # Plot tunnelbana lines
        for linje in tunnelbana:

            colour = self.linje_information[linje]['colour']
            name = self.linje_information[linje]['name']

            fig.add_trace(
                go.Scattermapbox(
                    lat=[station['latitude'] 
                         for station in tunnelbana[linje].values()],
                    lon=[station['longitude'] 
                         for station in tunnelbana[linje].values()],
                    mode='lines+markers',
                    marker=dict(color=colour),
                    name=name,
                    text=list(tunnelbana[linje].keys()),
                    hovertemplate=
                    '<extra>' + name.replace(' - ', '<br>') + '</extra>' +
                    '%{text}'
                )
            )

        # Plot pendeltåg lines
        for linje in pendeltåg:

            colour = self.linje_information[linje]['colour']
            name = self.linje_information[linje]['name']

            fig.add_trace(
                go.Scattermapbox(
                    lat=[station['latitude']
                         for station in pendeltåg[linje].values()],
                    lon=[station['longitude'] 
                         for station in pendeltåg[linje].values()],
                    mode='lines+markers',
                    marker=dict(color=colour),
                    name=name,
                    text=list(pendeltåg[linje].keys()),
                    hovertemplate=
                    '<extra>' + name.replace(' - ', '<br>') + '</extra>' +
                    '%{text}'
                )
            )

        # Plot spärvagn/lokalbana lines
        for linje in spårvagn:

            colour = self.linje_information[linje]['colour']
            name = self.linje_information[linje]['name']

            fig.add_trace(
                go.Scattermapbox(
                    lat=[station['latitude']
                         for station in spårvagn[linje].values()],
                    lon=[station['longitude'] 
                         for station in spårvagn[linje].values()],
                    mode='lines+markers',
                    marker=dict(color=colour),
                    name=name,
                    text=list(spårvagn[linje].keys()),
                    hovertemplate=
                    '<extra>' + name.replace(' - ', '<br>') + '</extra>' 
                    + '%{text}'
                )
            )

        fig.update_layout(
            title=dict(text="SL Spårtrafikkarta"),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=59.33, lon=18),
                zoom=10,
                style='light',
            ),
            margin=dict(t=50, b=20, r=20, l=20),
        )
        
        fig.write_html('SL_karta.html')
        
        
if __name__ == "__main__":
    karta = Karta()
    karta.read_data()
    karta.plot_map()