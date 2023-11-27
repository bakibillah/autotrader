
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from autotrader_app.models import Autotrader
from autotrader_app.serializers import Autotrader_Serializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# class VPNViewSet(viewsets.ModelViewSet):
#     authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     queryset = CompanyDb.objects.all()
#     serializer_class = VpnSerializer


class CarList(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def __init__(self):
        super().__init__()
        self.AtlasVpn = None
        self.vpn_provider = None

    def get(self, request, format=None):
        car_list = Autotrader.objects.all()
        serializer = Autotrader_Serializer(car_list, many=True)
        return Response(serializer.data)
