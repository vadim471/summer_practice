import math
import branca
from branca.element import CssLink
from folium import folium, Marker, Popup, LatLngPopup
import pandas as pd
from jinja2 import Template
from pandas import DataFrame
from sklearn.cluster import KMeans, SpectralClustering, AgglomerativeClustering
from folium.plugins import MarkerCluster


class MapService:
    @staticmethod
    def get_map(apartments, clusters_number=5):
        if len(apartments) < clusters_number:
            map_center = [55.1542, 61.4282]
            my_map = folium.Map(location=map_center, zoom_start=12, tiles='cartodbpositron')
            for apartment in apartments:
                popup = MapService.create_popup(apartment)
                iframe = branca.element.IFrame(html=popup, width=350, height=250)
                Marker(
                    location=[apartment.latitude, apartment.longitude],
                    popup=Popup(iframe, min_width=350, max_width=350)
                ).add_to(my_map)
            my_map.get_root().render()
            header = my_map.get_root().header.render()
            body = my_map.get_root().html.render()
            script = my_map.get_root().script.render()
            return header, body, script

        # строим DataFrame
        data = MapService.get_dataframe(apartments)

        # кластеризация
        clusterized_data = MapService.clusterize(data, clusters_number)

        # создание карты
        map_center = [55.1542, 61.4282]
        my_map = folium.Map(location=map_center, zoom_start=12, tiles='cartodbpositron')
        GetLatLngPopup().add_to(my_map)

        for cluster_id in data['cluster'].unique():
            cluster_data = data[data['cluster'] == cluster_id]
            marker_cluster = MarkerCluster(
                icon_create_function=MapService.add_icon_create()
            ).add_to(my_map)
            for i in range(len(cluster_data)):
                popup = MapService.create_popup(cluster_data.apartment.iloc[i])
                iframe = branca.element.IFrame(html=popup, width=350, height=250)
                Marker(
                    location=[cluster_data.latitude.iloc[i], cluster_data.longitude.iloc[i]],
                    popup=Popup(iframe, min_width=350, max_width=350),
                    props={'cost': cluster_data.apartment.iloc[i].cost}
                ).add_to(marker_cluster)

        my_map.get_root().header.add_child(CssLink('/static/map.css'))
        my_map.get_root().render()
        header = my_map.get_root().header.render()
        body = my_map.get_root().html.render()
        script = my_map.get_root().script.render()
        return header, body, script

    @staticmethod
    def clusterize(data: DataFrame, clusters: int) -> DataFrame:
        # clusterizer = SpectralClustering(n_clusters=clusters, random_state=0)
        # clusterizer = KMeans(n_clusters=clusters, random_state=0)
        clusterizer = AgglomerativeClustering(n_clusters=clusters, linkage='ward')
        clusterizer.fit(data[['latitude', 'longitude']])
        data['cluster'] = clusterizer.labels_
        return data

    @staticmethod
    def get_dataframe(apartments) -> DataFrame:
        data = pd.DataFrame(columns=['apartment', 'latitude', 'longitude'])
        count: int = 0
        for apartment in apartments:
            data.loc[count] = [apartment, apartment.latitude, apartment.longitude]
            count += 1
        return data

    @staticmethod
    def get_apartments_in_radius(apartments, lat: float, long: float, radius_km=1):
        new_data = []
        for apartment in apartments:
            if MapService.get_distance(lat, apartment.latitude, long, apartment.longitude) <= radius_km:
                new_data.append(apartment)
        return new_data

    @staticmethod
    def get_distance(lat1, lat2, long1, long2):
        long1 = math.radians(float(long1))
        long2 = math.radians(float(long2))
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
        deal_type = "СНЯТЬ" if apartment.type_of_deal == "RENT" else "КУПИТЬ"
        cost = f'{apartment.cost} ₽/месяц' if apartment.type_of_deal == "RENT" else f'{apartment.cost} ₽'
        rooms = MapService.format_rooms(apartment.rooms_count)
        return f"""
        <h3 style="font-family:verdana;">{deal_type}</h3>
        <p style="font-family:verdana;">Цена: {cost}</p>
        <p style="font-family:verdana;color:#999999";>{apartment.address}</p>
        <p style="font-family:verdana;">{rooms}, {apartment.floor} этаж, {apartment.square} м^2 </p>
        <p style="font-family:verdana;"><a href="{apartment.url}">Объявление</a></p>
        <p style="font-family:verdana;"><button id="like_btn" onclick="like_apartment()" apartment-id="{apartment.id}">В избранное ❤</button></p>
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

    @staticmethod
    def format_rooms(rooms_count: int) -> str:
        if rooms_count == 0:
            return 'Студия'
        if rooms_count == 1:
            return '1 комната'
        if 1 < rooms_count < 5:
            return f'{rooms_count} комнаты'
        else:
            return f'{rooms_count} комнат'

    @staticmethod
    def add_icon_create():
        return f'''
            function(cluster) {{
                var markers = cluster.getAllChildMarkers();
                var sum = 0;
                for (var i = 0; i < markers.length; i++) {{
                    sum += markers[i].options.props.cost;
                }}
                var avg = Math.ceil(sum/cluster.getChildCount());
                return L.divIcon({{
                     html: '<div class="centered">' + avg + '₽' + '</div>',
                     className: 'marker-cluster marker-cluster-small',
                     iconSize: new L.Point(60, 40)
                }});
            }}
        '''

    @staticmethod
    def add_cluster_animation():
        return '''const markerCluster = document.querySelector('.leaflet-marker-icon.leaflet-marker-cluster');
              function toggleClusterMarkers(show) {
                const markers = markerCluster.querySelectorAll('.leaflet-marker-pane > *');
                markers.forEach(marker => {
                  marker.style.display = show ? 'block' : 'none';
                });
              }
            
              // Обработчик события zoomend для карты
              const map = document.querySelector('.leaflet-container');
              map.addEventListener('zoomend', function(event) {
                if (event.target.getZoom() >= 10) { // Приближение
                  toggleClusterMarkers(true); // Показывать маркеры
                } else { // Удаление
                  toggleClusterMarkers(false); // Скрывать маркеры
                }
              });
          '''


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
