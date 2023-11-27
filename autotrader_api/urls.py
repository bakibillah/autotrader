from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # path('testapp/', include('vpnapp.urls')),
    path('api', include('autotrader_app.urls')),
    path('api/admin/', admin.site.urls),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
