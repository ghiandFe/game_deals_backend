from django.db import models


# Create your models here.

class Store(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)

    # internal_name field:
    # it's the store name uppercasing and without spaces
    internal_name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.internal_name:
            self.internal_name = self.name.replace(' ', '').upper()
        return super().save(*args, **kwargs)


class Deal(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=200, blank=True, null=True)
    store = models.ForeignKey(Store,
                              on_delete=models.CASCADE,
                              related_name='deals')
    is_on_sale = models.BooleanField(default=True)
    sale_price = models.FloatField(blank=True, null=True)
    normal_price = models.FloatField(blank=True, null=True)
    savings = models.DecimalField(max_digits=6,
                                  decimal_places=2,
                                  blank=True, null=True)
    rating_text = models.CharField(max_length=30, blank=True, null=True)
    rating_percent = models.IntegerField(blank=True, null=True)
    rating_count = models.BigIntegerField(blank=True, null=True)
    release_date = models.BigIntegerField(blank=True, null=True)
    last_change = models.BigIntegerField(blank=True, null=True)
    deal_rating = models.FloatField(blank=True, null=True)
    img_url = models.URLField(max_length=150, blank=True, null=True)
    header_img = models.URLField(max_length=150, blank=True, null=True)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if (thumb := self.img_url):
            if 'capsule_sm_120' in thumb:
                self.header_img = thumb.replace('capsule_sm_120', 'header')
            else:
                self.header_img = thumb
        return super().save(*args, **kwargs)