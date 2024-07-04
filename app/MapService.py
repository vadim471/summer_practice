import branca
from folium import folium, Marker, Popup, Icon
from geopy import Nominatim
import pandas as pd
from pandas import DataFrame
from sklearn.cluster import KMeans
from folium.plugins import MarkerCluster, MousePosition


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

        formatter = "function(num) {return L.Util.formatNum(num, 5);};"
        mouse_position = MousePosition(
            position='topright',
            separator=' Long: ',
            empty_string='NaN',
            lng_first=False,
            num_digits=20,
            prefix='Lat:',
            lat_formatter=formatter,
            lng_formatter=formatter,
        )

        my_map.add_child(mouse_position)

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
    def get_dataframe(apartments) -> DataFrame:  # ИЗМЕНИТЬ КОГДА БУДЕТ ТАБЛИЦА LOCATIONS
        data = pd.DataFrame(columns=['apartment', 'latitude', 'longitude'])
        count: int = 0
        for apartment in apartments:
            geolocator = Nominatim(user_agent="Tester")
            location = geolocator.geocode(apartment.address.replace('р-н', 'район'))
            data.loc[count] = [apartment, location.latitude, location.longitude]
            count += 1
        return data

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
