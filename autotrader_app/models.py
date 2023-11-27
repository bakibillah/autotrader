from django.db import models


class Autotrader(models.Model):
    listingid = models.IntegerField(db_column='listingId', unique=True, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(max_length=128, blank=True, null=True)
    year = models.CharField(max_length=45, blank=True, null=True)
    price = models.CharField(max_length=45, blank=True, null=True)
    kilometers = models.CharField(max_length=45, blank=True, null=True)
    vehicle_type = models.CharField(max_length=45, blank=True, null=True)
    gearbox = models.CharField(max_length=45, blank=True, null=True)
    fuel_type = models.CharField(max_length=45, blank=True, null=True)
    seller_type = models.CharField(max_length=45, blank=True, null=True)
    condition = models.CharField(max_length=45, blank=True, null=True)
    suburb = models.CharField(max_length=45, blank=True, null=True)
    state = models.CharField(max_length=45, blank=True, null=True)
    transmission = models.CharField(max_length=45, blank=True, null=True)
    body_type = models.CharField(max_length=45, blank=True, null=True)
    drive_type = models.CharField(max_length=45, blank=True, null=True)
    engine = models.CharField(max_length=45, blank=True, null=True)
    fuel_consumption = models.CharField(max_length=45, blank=True, null=True)
    colour_ext = models.CharField(max_length=45, blank=True, null=True)
    colour_int = models.CharField(max_length=45, blank=True, null=True)
    registration = models.CharField(max_length=45, blank=True, null=True)
    vin = models.CharField(max_length=45, blank=True, null=True)
    stock_no = models.CharField(max_length=45, blank=True, null=True)
    dealer = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    make = models.CharField(max_length=45, blank=True, null=True)
    model = models.CharField(max_length=45, blank=True, null=True)
    variant = models.CharField(max_length=128, blank=True, null=True)
    series = models.CharField(max_length=45, blank=True, null=True)
    is_sold = models.IntegerField(blank=True, null=True)
    sold_date = models.CharField(max_length=45, blank=True, null=True)
    url = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'autotrader'


