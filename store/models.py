from django.db import models
from django.utils import timezone
from django.db.models import Sum

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Category"

    def __str__(self):
        return str(f"{self.name}")


class Products(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank= True, null= True)
    buy_price = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Products"

    def __str__(self):
        return str(f"{self.name}")

    def available(self):
        try:
            stockin = StockIn.objects.filter(product__id = self.id).aggregate(Sum('quantity'))
            stockin = stockin['quantity__sum']
        except:
            stockin = 0
        try:
            stockout = SaleProducts.objects.filter(product__id = self.id).aggregate(Sum('quantity'))
            stockout = stockout['quantity__sum']
        except:
            stockout = 0
        stockin = stockin if not stockin is None else 0
        stockout = stockout if not stockout is None else 0
        
        return float(stockin - stockout)


class StockIn(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.FloatField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Stock-In"

    def __str__(self):
        return str(f"{self.product}")


class Sales(models.Model):
    code = models.CharField(max_length=100)
    client = models.CharField(max_length=250)
    contact = models.CharField(max_length=250, blank=True, null = True)
    total_amount = models.FloatField(max_length=15)
    tendered = models.FloatField(max_length=15)
    status = models.CharField(max_length=2, choices=(('0','Pending'), ('1', 'In-progress'), ('2', 'Done'), ('3', 'Picked Up')), default = 0)
    payment = models.CharField(max_length=2, choices=(('0','Unpaid'), ('1', 'Paid')), default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Sales"

    def __str__(self):
        return str(f"{self.code} - {self.client}")

    def change(self):
        change = float(self.tendered) - float(self.total_amount)
        return change

    # def totalItems(self):
    #     try:
    #         Items =  LaundryItems.objects.filter(laundry = self).aggregate(Sum('total_amount'))
    #         Items = Items['total_amount__sum']
    #     except:
    #         Items = 0
    #     return float(Items)
        
    def totalProducts(self):
        try:
            Products =  SaleProducts.objects.filter(laundry = self).aggregate(Sum('total_amount'))
            Products = Products['total_amount__sum']
        except:
            Products = 0
        return float(Products)


class SaleProducts(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE,related_name="laundry_fk2")
    product = models.ForeignKey(Products, on_delete=models.CASCADE,related_name="product_fk")
    buy_price = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    quantity = models.FloatField(max_length=15, default=0)
    free_quantity = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)
  

    class Meta:
        verbose_name_plural = "List of Laundry Products"

    def __str__(self):
        return str(f"{self.laundry.code} - {self.product.name}")