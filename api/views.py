import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView 
from django.shortcuts import render
from django.views.generic import TemplateView
from .services.geo_service import *
from .services.folium_service import *
import pandas as pd
from functools import reduce
from django.conf import settings
from .serializers import RouteRequestSerializer

class GasStationMapInfoView(APIView):
    def get(self, request):
        location = [37.7749, -122.4194]  # San Francisco coordinates

        m = folium.Map(location=location, zoom_start=12)
        folium.Marker(location, popup="San Francisco").add_to(m)
        return HttpResponse(m._repr_html_())


    def post(self, request):
        try:          
            serializer = RouteRequestSerializer(data=request.data)
            if(not serializer.is_valid()):
                    return HttpResponse(
                        json.dumps({"errors": serializer.errors}),
                        content_type="application/json",
                        status=400
                    )
            
            validated_data =  serializer.validated_data

            # {latitude : 1 , longitude: -1}
            start = validated_data.get("start_coordinates")
            start_coords = (start["latitude"], start["longitude"])

            end = validated_data.get("end_coordinates")
            end_coords = (end["latitude"], end["longitude"])


            route = call_openroute_service_by_car(start_coords, end_coords)
            route_geometry = route["features"][0]["geometry"]
            
            waypoints = [(lat, lon) for lon, lat in route_geometry["coordinates"]] 
            total_distance = meters_to_miles(route["features"][0]["properties"]["summary"]["distance"])

            map = create_route_map(route , start_coords, end_coords)

            gas_station_stops = calculate_stops_on_route(waypoints , 500, total_distance)

            csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'cleaned_fuel_prices_file.csv')
            gas_stations =  pd.read_csv(csv_file_path)

            station_stops = find_cheapest_gas_station(gas_station_stops , gas_stations , 200)

            for item in station_stops:
                stop,station = item["Stop"] , item["Station"]
                folium.Marker((stop[0], stop[1]), popup="stop", icon=folium.Icon(color="blue")).add_to(map)

                folium.Marker((station["Latitude"], station["Longitude"]), popup="Station", icon=folium.Icon(color="purple")).add_to(map)
                folium.Marker((station["Latitude"]-0.0001, station["Longitude"]), icon =folium.DivIcon(html=f'<div style="font-size: 12px; color: white; font-weight: bold;">{station["Name"]} | ${station["Price"]}</div>')).add_to(map)

            total_fuel_price = reduce(
                lambda acc, entry: acc + entry['Station']['Price'] * 50,
                station_stops,
                0
            )

            response = json.dumps({
                "total_fuel_price": total_fuel_price,
                "map": map._repr_html_() 
            })

            return HttpResponse(response, status=200)
            # return HttpResponse(m._repr_html_())

        except Exception as e:
            return HttpResponse({"error": f"Internal server error"}, status=500)
            
       

class GasStationMapView(APIView):
    def get(self, request):
    
        try:          
            serializer = RouteRequestSerializer(data=request.data)
            if(not serializer.is_valid()):
                    return HttpResponse(
                        json.dumps({"errors": serializer.errors}),
                        content_type="application/json",
                        status=400
                    )
            
            validated_data =  serializer.validated_data

            # {latitude : 1 , longitude: -1}
            start = validated_data.get("start_coordinates")
            start_coords = (start["latitude"], start["longitude"])

            end = validated_data.get("end_coordinates")
            end_coords = (end["latitude"], end["longitude"])


            route = call_openroute_service_by_car(start_coords, end_coords)
            route_geometry = route["features"][0]["geometry"]
            
            waypoints = [(lat, lon) for lon, lat in route_geometry["coordinates"]] 
            total_distance = meters_to_miles(route["features"][0]["properties"]["summary"]["distance"])

            map = create_route_map(route , start_coords, end_coords)

            gas_station_stops = calculate_stops_on_route(waypoints , 500, total_distance)

            csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'cleaned_fuel_prices_file.csv')
            gas_stations =  pd.read_csv(csv_file_path)

            station_stops = find_cheapest_gas_station(gas_station_stops , gas_stations , 200)

            for item in station_stops:
                stop,station = item["Stop"] , item["Station"]
                folium.Marker((stop[0], stop[1]), popup="stop", icon=folium.Icon(color="blue")).add_to(map)

                folium.Marker((station["Latitude"], station["Longitude"]), popup="Station", icon=folium.Icon(color="purple")).add_to(map)
                folium.Marker((station["Latitude"]-0.0001, station["Longitude"]), popup="gay", icon =folium.DivIcon(html=f'<div style="font-size: 12px; color: white; font-weight: bold;">{station["Name"]} | ${station["Price"]}</div>')).add_to(map)

            total_fuel_price = reduce(
                lambda acc, entry: acc + entry['Station']['Price'] * 50,
                station_stops,
                0
            )


            return render(request, 'api/map_template.html', {
            'map': map._repr_html_(),
            'total_fuel_price': total_fuel_price,
        })

        except Exception as e:
            return HttpResponse({"error": f"Internal server error"}, status=500)


