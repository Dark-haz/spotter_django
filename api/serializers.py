from rest_framework import serializers



class CoordinatesSerializer(serializers.Serializer):
    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)

class RouteRequestSerializer(serializers.Serializer):
    start_coordinates = CoordinatesSerializer(required=True)
    end_coordinates = CoordinatesSerializer(required=True)


# class CreateWorkLogSerializer(serializers.Serializer):
#     start_coordinates = serializers.IntegerField(required=True)
#     end_coordinates = serializers.FloatField(required=True)

#     def validate_hours_logged(self, value):
#         if value <= 0:
#             raise serializers.ValidationError("Hours logged must be greater than 0.")
#         return value

#     def validate(self, data):
#         if data['hours_logged'] > 24:
#             raise serializers.ValidationError("Hours logged cannot exceed 24 in a day.")
#         return data
