from django.db import models
from django.utils import timezone
from django.db.models import Sum

# Create your models here.
class Employee(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    nid = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=2, choices=(('1','Salesman'), ('2','Deliveryman')), default = 1)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Employee"

    def __str__(self):
        return str(f"{self.name}")


class Road(models.Model):
    name = models.CharField(max_length=100)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Road"

    def __str__(self):
        return str(f"{self.name}")


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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank= True, null= True)
    buy = models.FloatField(max_length=15, default=0)
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
            stockin = PurchaseProducts.objects.filter(product__id = self.id).aggregate(Sum('quantity'))
            stockin = stockin['quantity__sum']
        except:
            stockin = 0
        try:
            stockout = SaleProducts.objects.filter(product__id = self.id).aggregate(Sum('quantity'))
            stockout = stockout['quantity__sum']
        except:
            stockout = 0
        try:
            free = SaleProducts.objects.filter(product__id = self.id).aggregate(Sum('free_quantity'))
            free = free['free_quantity__sum']
        except:
            free = 0
        stockin = stockin if not stockin is None else 0
        stockout = stockout if not stockout is None else 0
        free = free if not free is None else 0
        
        return float(stockin - stockout - free)


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
    client = models.CharField(max_length=250, blank=True, null=True)
    contact = models.CharField(max_length=250, blank=True, null=True)
    road = models.ForeignKey(Road, on_delete=models.CASCADE, null=True, blank=True, related_name='road_fk')
    salesman = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='deliveryman_fk')
    deliveryman = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='salesman_fk')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category_fk")
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
        change = float(self.total_amount) - float(self.tendered)
        return change
        
    def totalProducts(self):
        try:
            Products = SaleProducts.objects.filter(sale = self).aggregate(Sum('total_amount'))
            Products = Products['total_amount__sum']
        except:
            Products = 0
        return float(Products)


class SaleProducts(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE,related_name="sale_fk2")
    product = models.ForeignKey(Products, on_delete=models.CASCADE,related_name="product_fk")
    buy = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    quantity = models.FloatField(max_length=15, default=0)
    free_quantity = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)

    class Meta:
        verbose_name_plural = "List of Sale Products"

    def __str__(self):
        return str(f"{self.sale.code} - {self.product.name}")


class Purchase(models.Model):
    code = models.CharField(max_length=100)
    client = models.CharField(max_length=250, blank=True, null=True)
    contact = models.CharField(max_length=250, blank=True, null=True)
    total_amount = models.FloatField(max_length=15)
    status = models.CharField(max_length=2,
                              choices=(('0', 'Pending'), ('1', 'In-progress'), ('2', 'Done'), ('3', 'Picked Up')),
                              default=0)
    payment = models.CharField(max_length=2, choices=(('0', 'Unpaid'), ('1', 'Paid')), default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Purchase"

    def __str__(self):
        return str(f"{self.code} - {self.client}")

    def totalProducts(self):
        try:
            Products = PurchaseProducts.objects.filter(purchase=self).aggregate(Sum('total_amount'))
            Products = Products['total_amount__sum']
        except:
            Products = 0
        return float(Products)


class PurchaseProducts(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="purchase_fk2")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="purchase_fk")
    buy = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    quantity = models.FloatField(max_length=15, default=0)
    free_quantity = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)

    class Meta:
        verbose_name_plural = "List of Purchase Products"

    def __str__(self):
        return str(f"{self.purchase.code} - {self.product.name}")