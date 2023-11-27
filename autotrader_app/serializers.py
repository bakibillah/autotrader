from rest_framework import serializers
from .models import *


class Autotrader_Serializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Autotrader
        fields = ('listingid', 'title', 'year', 'price', 'kilometers', 'vehicle_type', 'gearbox', 'fuel_type',
                  'seller_type', 'condition', 'suburb', 'state', 'transmission', 'body_type', 'drive_type', 'engine',
                  'fuel_consumption', 'colour_ext', 'colour_int', 'registration', 'vin', 'stock_no', 'dealer', 'address',
                  'make', 'model', 'variant', 'series', 'is_sold', 'sold_date', 'url')




