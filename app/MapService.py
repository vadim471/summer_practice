import math

import branca
from folium import folium, Marker, Popup, LatLngPopup
from geopy import Nominatim
import pandas as pd
from jinja2 import Template
from pandas import DataFrame
from sklearn.cluster import KMeans
from folium.plugins import MarkerCluster


class MapService:
    @staticmethod
    def get_map(apartments, clusters_number=4):
        # строим DataFrame
        data = MapService.get_dataframe(apartments)

        # кластеризация
        clusterized_data = MapService.clusterize(data, clusters_number)

        # создание карты
        map_center = [55.1542, 61.4282]
        my_map = folium.Map(location=map_center, zoom_start=12, tiles='cartodbpositron')

        GetLatLngPopup().add_to(my_map)

        for cluster_id in data['cluster'].unique():
            marker_cluster = MarkerCluster().add_to(my_map)
            cluster_data = data[data['cluster'] == cluster_id]
            for i in range(len(cluster_data)):
                popup = MapService.create_popup(cluster_data.apartment.iloc[i])
                iframe = branca.element.IFrame(html=popup, width=350, height=150)
                Marker(
                    location=[cluster_data.latitude.iloc[i], cluster_data.longitude.iloc[i]],
                    popup=Popup(iframe, min_width=350, max_width=350)
                ).add_to(marker_cluster)

        my_map.get_root().render()
        header = my_map.get_root().header.render()
        body = my_map.get_root().html.render()
        script = my_map.get_root().script.render()
        return header, body, script

    @staticmethod
    def clusterize(data: DataFrame, clusters: int) -> DataFrame:
        kmeans = KMeans(n_clusters=clusters, random_state=0)
        kmeans.fit(data[['latitude', 'longitude']])
        data['cluster'] = kmeans.labels_
        return data

    @staticmethod
    def get_dataframe(apartments) -> DataFrame:
        data = pd.DataFrame(columns=['apartment', 'latitude', 'longitude'])
        count: int = 0
        for apartment in apartments:
            # geolocator = Nominatim(user_agent="Tester")
            # location = geolocator.geocode(apartment.address.replace('р-н', 'район'))
            data.loc[count] = [apartment, apartment.latitude, apartment.longitude]
            count += 1
        return data

    @staticmethod
    def get_apartments_in_radius(apartments, lat: float, long: float, radius_km=1):
        new_data = []
        for apartment in apartments:
            if MapService.get_distance(lat, float(apartment.latitude), long, float(apartment.longitude)) <= radius_km:
                new_data.append(apartment)
        return new_data

    @staticmethod
    def get_distance(lat1, lat2, long1, long2):
        long1 = math.radians(float(long1))
        long2 = math.radians(float(long2) )
        lat1 = math.radians(float(lat1))
        lat2 = math.radians(float(lat2))

        D_Lo = long2 - long1
        D_La = lat2 - lat1
        P = math.sin(D_La / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(D_Lo / 2) ** 2

        Q = 2 * math.asin(math.sqrt(P))

        R_km = 6371

        return Q * R_km

    @staticmethod
    def create_popup(apartment):
        return f"""
        <p style="font-family:verdana;">Цена: {apartment.cost} ₽</p>
        <p style="font-family:verdana;">{apartment.rooms_count} комнат, {apartment.floor} этаж, {apartment.square} м^2 </p>
        <p style="font-family:verdana;"><a href="{apartment.url}">View details</a></p>
        <p style="font-family:verdana;"><button id="like_btn" onclick="like_apartment()" apartment-id="{apartment.id}">Like ❤</button></p>
        <script>{MapService.add_like_js()}</script>
        """

    @staticmethod
    def add_like_js():
        return """function like_apartment() {
        const button = event.target;
        const apartmentId = button.getAttribute('apartment-id');
             const message = {
             type: 'customEvent', 
             data: apartmentId // здесь нужно еще возвращать id юзера
         };
         window.parent.postMessage(message, '*'); 
        };
        """


class GetLatLngPopup(LatLngPopup):
    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngClick(e) {
                    fetch('/get_apartments_in_radius', {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ latitude: e.latlng.lat.toFixed(7),
                                                longitude: e.latlng.lng.toFixed(7) })
                         })
                      .then(response => {
                        if (!response.ok) {
                          throw new Error('Ошибка при отправке запроса');
                        }
                      })
                    }
                {{this._parent.get_name()}}.on('click', latLngClick);
            {% endmacro %}
            """)

    def __init__(self):
        super(GetLatLngPopup, self).__init__()
        self._name = 'GetLatLngPopup'