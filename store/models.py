from django.db import models
from django.utils import timezone
from django.db.models import Sum
from datetime import date


# Create your models here.
class Employee(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    nid = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=2, choices=(('1','Salesman'), ('2','Deliveryman'), ('3','Manager'), ('4','AIC'), ('5','Other')), default = 1)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Employee"

    def __str__(self):
        return str(f"{self.name}")

    def due(self):
        try:
            balance = Loan.objects.filter(employee__id=self.id).aggregate(Sum('due_amount'))
            balance = balance['due_amount__sum']
        except:
            balance = 0

        balance = balance if not balance is None else 0

        return float(balance)


class Road(models.Model):
    name = models.CharField(max_length=100)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Road"

    def __str__(self):
        return str(f"{self.name}")


class Client(models.Model):
    name = models.CharField(max_length=100)
    shop = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    address = models.CharField(max_length=100, null=True, blank=True)
    road = models.ForeignKey(Road, on_delete=models.CASCADE)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Client"

    def __str__(self):
        return str(f"{self.name}")

    def totalDue(self):
        try:
            due = SaleDue.objects.filter(client__id=self.id).aggregate(Sum('balance'))
            due = due['balance__sum']
        except:
            due = 0
        return float(due)


class Brand(models.Model):
    name = models.CharField(max_length=250)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Brand"

    def __str__(self):
        return str(f"{self.name}")

    # commission due
    def due(self):
        try:
            given = DiscountGiven.objects.filter(brand__id=self.id).aggregate(Sum('price'))
            given = given['price__sum']
        except:
            given = 0
        try:
            received = DiscountReceived.objects.filter(brand__id=self.id).aggregate(Sum('price'))
            received = received['price__sum']
        except:
            received = 0

        given = given if not given is None else 0
        received = received if not received is None else 0

        return float(given - received)

    # advance due
    def advance(self):
        try:
            debit = OnlineAdvance.objects.filter(brand__id=self.id).aggregate(Sum('advance'))
            debit = debit['advance__sum']
        except:
            debit = 0
        try:
            credit = OnlineCredit.objects.filter(brand__id=self.id).aggregate(Sum('amount'))
            credit = credit['amount__sum']
        except:
            credit = 0

        debit = debit if not debit is None else 0
        credit = credit if not credit is None else 0

        return float(debit - credit)


class Products(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250, default=0)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank= True, null= True)
    buy = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    mrp = models.FloatField(max_length=15, default=0)
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
        try:
            good = SaleProducts.objects.filter(product__id = self.id).aggregate(Sum('good_quantity'))
            good = good['good_quantity__sum']
        except:
            good = 0

        stockin = stockin if not stockin is None else 0
        stockout = stockout if not stockout is None else 0
        free = free if not free is None else 0
        good = good if not good is None else 0

        return float(stockin + good - stockout - free)

    def damage(self):
        try:
            damage = SaleProducts.objects.filter(product__id = self.id).aggregate(Sum('damage_quantity'))
            damage = damage['damage_quantity__sum']
        except:
            damage = 0
        try:
            restore = SaleReturn.objects.filter(product__id = self.id).aggregate(Sum('quantity'))
            restore = restore['quantity__sum']
        except:
            restore = 0
        try:
            out = DamageProduct.objects.filter(product__id = self.id).aggregate(Sum('quantity'))
            out = out['quantity__sum']
        except:
            out = 0

        damage = damage if not damage is None else 0
        restore = restore if not restore is None else 0
        out = out if not out is None else 0

        return float(damage + restore - out)

    def value(self):
        try:
            restore = SaleReturn.objects.filter(product__id = self.id).aggregate(Sum('total_amount'))
            restore = restore['total_amount__sum']
        except:
            restore = 0
        try:
            out = DamageProduct.objects.filter(product__id = self.id).aggregate(Sum('total_amount'))
            out = out['total_amount__sum']
        except:
            out = 0

        restore = restore if not restore is None else 0
        out = out if not out is None else 0

        return float(restore - out)

    def fresh_value(self):
        stock = self.available() * self.buy
        return stock


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
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="brand_fk")
    total_amount = models.FloatField(max_length=15)
    tendered = models.FloatField(max_length=15)
    cost = models.FloatField(max_length=15, default=0)
    extra = models.FloatField(max_length=15, default=0)
    status = models.CharField(max_length=2, choices=(('0','Pending'), ('1', 'In-progress'), ('2', 'Done'), ('3', 'Picked Up')), default = 0)
    payment = models.CharField(max_length=2, choices=(('0','Unpaid'), ('1', 'Paid')), default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Sales"

    def __str__(self):
        return str(f"{self.code} - {self.client}")

    def change(self):
        change = float(self.total_amount) - float(self.tendered)
        return change

    def short(self):
        short = float(self.total_amount) + float(self.extra) - float(self.cost)
        return short
        
    def totalProducts(self):
        try:
            Products = SaleProducts.objects.filter(sale = self).aggregate(Sum('total_amount'))
            Products = Products['total_amount__sum']
        except:
            Products = 0
        return float(Products)

    def totalItems(self):
        try:
            Items = SaleDue.objects.filter(sale = self).aggregate(Sum('balance'))
            Items = Items['balance__sum']
        except:
            Items = 0
        return float(Items)

    def totalReturns(self):
        try:
            Returns = SaleReturn.objects.filter(sale = self).aggregate(Sum('total_amount'))
            Returns = Returns['total_amount__sum']
        except:
            Returns = 0
        return float(Returns)

    def totalCommissions(self):
        try:
            Commissions = SaleCommission.objects.filter(sale = self).aggregate(Sum('total_amount'))
            Commissions = Commissions['total_amount__sum']
        except:
            Commissions = 0
        return float(Commissions)


class SaleProducts(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE,related_name="sale_fk2")
    product = models.ForeignKey(Products, on_delete=models.DO_NOTHING,related_name="product_fk")
    brand = models.CharField(max_length=100, null=True)
    buy = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    quantity = models.FloatField(max_length=15, default=0)
    free_quantity = models.FloatField(max_length=15, default=0)
    good_quantity = models.FloatField(max_length=15, default=0)
    damage_quantity = models.FloatField(max_length=15, default=0)
    sign = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Sale Products"

    def __str__(self):
        return str(f"{self.sale.code} - {self.product.name}")


class SaleReturn(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE,related_name="sale_fk3")
    product = models.ForeignKey(Products, on_delete=models.CASCADE,related_name="product_fk2")
    brand = models.CharField(max_length=100, null=True)
    buy = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    quantity = models.FloatField(max_length=15, default=0)
    free_quantity = models.FloatField(max_length=15, default=0)
    good_quantity = models.FloatField(max_length=15, default=0)
    damage_quantity = models.FloatField(max_length=15, default=0)
    sign = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)

    class Meta:
        verbose_name_plural = "List of Sale Returns"

    def __str__(self):
        return str(f"{self.sale.code} - {self.product.name}")


class SaleDue(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name="sale_fk4")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_fk")
    brand = models.CharField(max_length=250, blank=True, null=True)
    note = models.CharField(max_length=250, blank=True, null=True)
    due = models.FloatField(max_length=15, default=0)
    new = models.FloatField(max_length=15, default=0)
    previous = models.FloatField(max_length=15, default=0)
    paid = models.FloatField(max_length=15, default=0)
    balance = models.FloatField(max_length=15, default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Sale Due"

    def __str__(self):
        return str(f"{self.sale.code} - {self.client.name}")


class SaleCommission(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name="sale_fk5")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="brand_fk2")
    commission = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15, default=0)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Sale Commission"

    def __str__(self):
        return str(f"{self.sale.code} - {self.brand.name}")


class Purchase(models.Model):
    code = models.CharField(max_length=100)
    note = models.CharField(max_length=250, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="brand_fk5")
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


class CommissionBill(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    month = models.CharField(max_length=12, choices=(('1','January'), ('2','February'), ('3','March'),
                                                     ('4','April'), ('5','May'), ('6','June'), ('7','July'),
                                                     ('8','August'), ('9','September'), ('10','October'),
                                                     ('11','November'), ('12','December')), default = 1)
    bill = models.FloatField(max_length=15, default=0)
    collect = models.FloatField(max_length=15, default=0)
    status = models.CharField(max_length=2, choices=(('1','Unpaid'), ('2','Paid')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Commission Bills"

    def __str__(self):
        return str(f"{self.month} - {self.brand.name}")

    def due(self):
        due = float(self.bill) - float(self.collect)
        return due


class Online(models.Model):
    code = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="brand_fk6")
    note = models.CharField(max_length=250, blank=True, null=True)
    due_amount = models.FloatField(max_length=15, null=True)
    status = models.CharField(max_length=2,
                              choices=(('0', 'Pending'), ('1', 'In-progress'), ('2', 'Done')),
                              default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Advance"

    def __str__(self):
        return str(f"{self.code}")

    def totalDue(self):
        try:
            brands = OnlineAdvance.objects.filter(online=self).aggregate(Sum('total_amount'))
            brands = brands['total_amount__sum']
        except:
            brands = 0
        return float(brands)

    def totalCredit(self):
        try:
            brands = OnlineCredit.objects.filter(online=self).aggregate(Sum('total_amount'))
            brands = brands['total_amount__sum']
        except:
            brands = 0
        return float(brands)


class OnlineAdvance(models.Model):
    online = models.ForeignKey(Online, on_delete=models.CASCADE, related_name="online_fk")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="brand_fk3")
    previous = models.FloatField(max_length=15, default=0)
    advance = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)
    day = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = "List of Advance Brand"

    def __str__(self):
        return str(f"{self.online.code} - {self.brand.name}")


class OnlineCredit(models.Model):
    online = models.ForeignKey(Online, on_delete=models.CASCADE, related_name="online_fk2")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="brand_fk4")
    amount = models.CharField(max_length=100)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)
    day = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = "List of Advance Credited"

    def __str__(self):
        return str(f"{self.online.code} - {self.brand.name}")


class DamageSale(models.Model):
    code = models.CharField(max_length=100)
    total_amount = models.FloatField(max_length=15)
    payable_amount = models.FloatField(max_length=15, null=True)
    paid_amount = models.FloatField(max_length=15)
    short = models.FloatField(max_length=15)
    status = models.CharField(max_length=2,
                              choices=(('0', 'Pending'), ('1', 'In-progress'), ('2', 'Done')),
                              default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Damage Sale"

    def __str__(self):
        return str(f"{self.code}")

    def totalProducts(self):
        try:
            products = DamageProduct.objects.filter(online=self).aggregate(Sum('total_amount'))
            products = products['total_amount__sum']
        except:
            products = 0
        return float(products)


class DamageProduct(models.Model):
    damage = models.ForeignKey(DamageSale, on_delete=models.CASCADE, related_name="damage_fk")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="product_fk3")
    brand = models.CharField(max_length=100)
    price = models.FloatField(max_length=15, default=0)
    quantity = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Damage Sale Product"

    def __str__(self):
        return str(f"{self.damage.code} - {self.product.name}")


class Expense(models.Model):
    name = models.CharField(max_length=100)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Expense"

    def __str__(self):
        return str(f"{self.name}")


class Surplus(models.Model):
    code = models.CharField(max_length=100)
    month = models.CharField(max_length=12, choices=(('1', 'January'), ('2', 'February'), ('3', 'March'),
                                                     ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'),
                                                     ('8', 'August'), ('9', 'September'), ('10', 'October'),
                                                     ('11', 'November'), ('12', 'December')), default=1)
    total_sale = models.FloatField(max_length=15)
    total_cost = models.FloatField(max_length=15)
    total_extra = models.FloatField(max_length=15, null=True)
    total_damage = models.FloatField(max_length=15, null=True)
    total_expense = models.FloatField(max_length=15)
    margin = models.FloatField(max_length=15, default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Surplus"

    def __str__(self):
        return str(f"{self.code}")

    def totalExpense(self):
        try:
            expense = Charge.objects.filter(online=self).aggregate(Sum('total_amount'))
            expense = expense['total_amount__sum']
        except:
            expense = 0
        return float(expense)


class Charge(models.Model):
    surplus = models.ForeignKey(Surplus, on_delete=models.CASCADE, related_name="surplus_fk")
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="expense_fk")
    note = models.CharField(max_length=250, blank=True, null=True)
    amount = models.CharField(max_length=100)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Surplus Charges"

    def __str__(self):
        return str(f"{self.surplus.code} - {self.expense.name}")


class Debit(models.Model):
    name = models.CharField(max_length=100)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Debit"

    def __str__(self):
        return str(f"{self.name}")


class Credit(models.Model):
    name = models.CharField(max_length=100)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Credit"

    def __str__(self):
        return str(f"{self.name}")


class Loan(models.Model):
    code = models.CharField(max_length=100)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_fk')
    note = models.CharField(max_length=250, blank=True, null=True)
    due_amount = models.FloatField(max_length=15)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Loans"

    def __str__(self):
        return str(f"{self.code} - {self.employee.name}")

    def totalCredit(self):
        try:
            credit = LoanCredit.objects.filter(loan=self).aggregate(Sum('total_amount'))
            credit = credit['total_amount__sum']
        except:
            credit = 0
        return float(credit)

    def totalDebit(self):
        try:
            debit = LoanDebit.objects.filter(loan=self).aggregate(Sum('total_amount'))
            debit = debit['total_amount__sum']
        except:
            debit = 0
        return float(debit)


class LoanCredit(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="loan_fk")
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="credit_fk")
    amount = models.CharField(max_length=100)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)
    day = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = "List of Loans Credited"

    def __str__(self):
        return str(f"{self.loan.code} - {self.credit.name}")


class LoanDebit(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="loan_fk2")
    debit = models.ForeignKey(Debit, on_delete=models.CASCADE, related_name="debit_fk")
    amount = models.CharField(max_length=100)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)
    day = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = "List of Loans Debited"

    def __str__(self):
        return str(f"{self.loan.code} - {self.debit.name}")


class Expenditure(models.Model):
    code = models.CharField(max_length=100)
    total_amount = models.FloatField(max_length=15)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Expenditure"

    def __str__(self):
        return str(f"{self.code}")

    def totalExpense(self):
        try:
            expense = ExpenditureCharge.objects.filter(online=self).aggregate(Sum('total_amount'))
            expense = expense['total_amount__sum']
        except:
            expense = 0
        return float(expense)


class ExpenditureCharge(models.Model):
    expenditure = models.ForeignKey(Expenditure, on_delete=models.CASCADE, related_name="expenditure_fk")
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="expense_fk2")
    note = models.CharField(max_length=250, blank=True, null=True)
    amount = models.CharField(max_length=100)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Expenditure Charges"

    def __str__(self):
        return str(f"{self.expenditure.code} - {self.expense.name}")


class Investment(models.Model):
    invest = models.FloatField(max_length=250)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Investment"

    def __str__(self):
        return str(f"{self.invest}")


class OnlineTransaction(models.Model):
    amount = models.FloatField(max_length=250)
    note = models.CharField(max_length=250)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Expose"

    def __str__(self):
        return str(f"{self.amount}")


class Bank(models.Model):
    amount = models.FloatField(max_length=100)
    note = models.CharField(max_length=250, blank=True, null=True)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Banks"

    def __str__(self):
        return str(f"{self.amount}")

    def totalBalance(self):
        try:
            existing = Bank.objects.filter(delete_flag=0).aggregate(Sum('amount'))
            existing = existing['amount__sum']
        except:
            existing = 0
        try:
            deposit = BankTransaction.objects.filter(type=1, delete_flag=0).aggregate(Sum('amount'))
            deposit = deposit['amount__sum']
        except:
            deposit = 0
        try:
            withdraw = BankTransaction.objects.filter(type=2, delete_flag=0).aggregate(Sum('amount'))
            withdraw = withdraw['amount__sum']
        except:
            withdraw = 0

        existing = existing if not existing is None else 0
        deposit = deposit if not deposit is None else 0
        withdraw = withdraw if not withdraw is None else 0
        return float(existing + deposit - withdraw)

    def todayCash(self):
        try:
            existing = Bank.objects.filter(delete_flag=0).aggregate(Sum('amount'))
            existing = existing['amount__sum']
        except:
            existing = 0
        try:
            deposit = BankTransaction.objects.filter(type=1, delete_flag=0).aggregate(Sum('amount'))
            deposit = deposit['amount__sum']
        except:
            deposit = 0
        try:
            withdraw = BankTransaction.objects.filter(type=2, delete_flag=0).aggregate(Sum('amount'))
            withdraw = withdraw['amount__sum']
        except:
            withdraw = 0
        try:
            sale = SaleProducts.objects.aggregate(Sum('total_amount'))
            sale = sale['total_amount__sum']
        except:
            sale = 0
        try:
            damage = SaleReturn.objects.aggregate(Sum('total_amount'))
            damage = damage['total_amount__sum']
        except:
            damage = 0
        try:
            due = SaleDue.objects.aggregate(Sum('balance'))
            due = due['balance__sum']
        except:
            due = 0
        try:
            commission = SaleCommission.objects.aggregate(Sum('total_amount'))
            commission = commission['total_amount__sum']
        except:
            commission = 0
        try:
            debit = LoanDebit.objects.aggregate(Sum('total_amount'))
            debit = debit['total_amount__sum']
        except:
            debit = 0
        try:
            credit = LoanCredit.objects.aggregate(Sum('total_amount'))
            credit = credit['total_amount__sum']
        except:
            credit = 0
        try:
            online = OnlineTransaction.objects.aggregate(Sum('amount'))
            online = online['amount__sum']
        except:
            online = 0
        try:
            expense = ExpenditureCharge.objects.aggregate(Sum('total_amount'))
            expense = expense['total_amount__sum']
        except:
            expense = 0

        existing = existing if not existing is None else 0
        deposit = deposit if not deposit is None else 0
        withdraw = withdraw if not withdraw is None else 0
        sale = sale if not sale is None else 0
        damage = damage if not damage is None else 0
        due = due if not due is None else 0
        commission = commission if not commission is None else 0
        debit = debit if not debit is None else 0
        credit = credit if not credit is None else 0
        online = online if not online is None else 0
        expense = expense if not expense is None else 0
        return float(existing - deposit + withdraw + sale - damage - due - commission - debit + credit - online - expense)


class BankTransaction(models.Model):
    amount = models.FloatField(max_length=100)
    type = models.CharField(max_length=2, choices=(('1', 'Deposit'), ('2', 'Withdraw')), default=1)
    delete_flag = models.IntegerField(default=0)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Bank Transaction"

    def __str__(self):
        return str(f"{self.amount} - {self.type}")


class Discount(models.Model):
    code = models.CharField(max_length=100)
    note = models.CharField(max_length=250, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="brand_fk7")
    month = models.CharField(max_length=12, choices=(('1', 'January'), ('2', 'February'), ('3', 'March'),
                                                     ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'),
                                                     ('8', 'August'), ('9', 'September'), ('10', 'October'),
                                                     ('11', 'November'), ('12', 'December')), default=1)
    total_amount = models.FloatField(max_length=15)
    extra = models.FloatField(max_length=15,  default=0)
    status = models.CharField(max_length=2,
                              choices=(('0', 'Pending'), ('1', 'Due'), ('2', 'Done')),
                              default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Discount"

    def __str__(self):
        return str(f"{self.code} - {self.brand}")

    def totalGiven(self):
        try:
            given = DiscountGiven.objects.filter(discount=self).aggregate(Sum('total_amount'))
            given = given['total_amount__sum']
        except:
            given = 0
        return float(given)

    def totalReceived(self):
        try:
            received = DiscountReceived.objects.filter(discount=self).aggregate(Sum('total_amount'))
            received = received['total_amount__sum']
        except:
            received = 0
        return float(received)

    def totalItems(self):
        try:
            due = DiscountDue.objects.filter(sale=self).aggregate(Sum('total_amount'))
            due = due['total_amount__sum']
        except:
            due = 0
        return float(due)


class DiscountGiven(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name="discount_fk")
    brand = models.ForeignKey(Brand, on_delete=models.DO_NOTHING, related_name="brand_fk8")
    previous = models.FloatField(max_length=15, default=0)
    price = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Discount Given"

    def __str__(self):
        return str(f"{self.discount.code} - {self.brand.name}")


class DiscountReceived(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name="discount_fk2")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="brand_fk9")
    price = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Discount Received"

    def __str__(self):
        return str(f"{self.discount.code} - {self.brand.name}")


class DiscountDue(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name="discount_fk3")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="brand_fk10")
    due = models.FloatField(max_length=15, default=0)
    total_amount = models.FloatField(max_length=15)
    date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "List of Discount Due"

    def __str__(self):
        return str(f"{self.discount.code} - {self.brand.name}")
