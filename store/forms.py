from datetime import datetime
from django import forms
from store import models
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
import datetime
from numpy import require
from tabnanny import check


class SaveUser(UserCreationForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    password1 = forms.CharField(max_length=250)
    password2 = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name','password1', 'password2',)


class UpdateProfile(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} username is already exists/taken")


class UpdateUser(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")


class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Old Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Confirm New Password")

    class Meta:
        model = User
        fields = ('old_password','new_password1', 'new_password2')


class SaveCategory(forms.ModelForm):
    name = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Category
        fields = ('name', 'status', )

    def clean_name(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        name = self.cleaned_data['name']
        try:
            if id > 0:
                price = models.Category.objects.exclude(id = id).get(name = name, delete_flag = 0)
            else:
                price = models.Category.objects.get(name = name, delete_flag = 0)
        except:
            return name
        raise forms.ValidationError("Category Type already exists.")


class SaveBrand(forms.ModelForm):
    name = forms.CharField(max_length=250)
    category = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_category'}
    )

    class Meta:
        model = models.Brand
        fields = ('name', 'category')

    def clean_name(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        name = self.cleaned_data['name']
        try:
            if id > 0:
                brand = models.Brand.objects.exclude(id=id).get(name=name, delete_flag=0)
            else:
                brand = models.Brand.objects.get(name=name, delete_flag=0)
        except:
            return name
        raise forms.ValidationError(f"Brand {brand.name} already exist")


class SaveProducts(forms.ModelForm):
    name = forms.CharField(max_length=250)
    category = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_category'}
    )
    description = forms.CharField(max_length=250, required=False)
    buy = forms.CharField(max_length=250)
    price = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Products
        fields = ('name', 'description', 'category', 'buy', 'price', 'status', )

    def clean_name(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        name = self.cleaned_data['name']
        try:
            if id > 0:
                product = models.Products.objects.exclude(id = id).get(name = name, delete_flag = 0)
            else:
                product = models.Products.objects.get(name = name, delete_flag = 0)
        except:
            return name
        raise forms.ValidationError("Product Name already exists.")


class SaveStockIn(forms.ModelForm):
    product = forms.CharField(max_length=250)
    quantity = forms.CharField(max_length=250)

    class Meta:
        model = models.StockIn
        fields = ('product', 'quantity',)

    def clean_product(self):
        pid = self.cleaned_data['product']
        try:
            product = models.Products.objects.get(id = pid, delete_flag = 0)
            return product
        except:
            raise forms.ValidationError("Product is Invalid.")


class SaveSale(forms.ModelForm):
    code = forms.CharField(max_length=250)
    client = forms.CharField(max_length=250, required=False)
    contact = forms.CharField(max_length=250, required=False)
    road = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_road'}
    )
    salesman = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_salesman'}
    )
    deliveryman = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_deliveryman'}
    )
    category = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_category'}
    )
    status = forms.CharField(max_length=2)
    payment = forms.CharField(max_length=2)
    total_amount = forms.CharField(max_length=250)
    tendered = forms.CharField(max_length=250)

    class Meta:
        model = models.Sales
        fields = ('code', 'client', 'contact', 'road', 'salesman', 'deliveryman', 'category', 'status', 'payment', 'total_amount', 'tendered',)

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.Sales.objects.get(code=f"{pref}{code:05d}")
                    code = code + 1
                except:
                    return f"{pref}{code:05d}"
                    break
        else:
            return code

    def clean_payment(self):
        tendered = float(self.data['tendered'])
        if tendered > 0:
            return 1
        else:
            return 0

    def save(self):
        instance = self.instance
        Products = []

        if 'product_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('product_id[]')):
                product = models.Products.objects.get(id=val)
                buy = self.data.getlist('product_buy[]')[k]
                price = self.data.getlist('product_price[]')[k]
                qty = self.data.getlist('product_quantity[]')[k]
                freeqty = self.data.getlist('product_free_quantity[]')[k]
                total = float(price) * float(qty)
                # free = self.cleaned_data['free_quantity']
                try:
                    Products.append(models.SaleProducts(sale=instance, product=product, buy=buy, price=price, quantity=qty, total_amount=total, free_quantity=freeqty))
                    print("SaleProducts..")
                except Exception as err:
                    print(err)
                    return False
        try:
            instance.save()
            models.SaleProducts.objects.filter(sale=instance).delete()
            models.SaleProducts.objects.bulk_create(Products)
            # models.LaundryItems.objects.filter(laundry=instance).delete()
            # models.LaundryItems.objects.bulk_create(Items)
        except Exception as err:
            print(err)
            return False


class SavePurchase(forms.ModelForm):
    code = forms.CharField(max_length=250)
    client = forms.CharField(max_length=250, required=False)
    contact = forms.CharField(max_length=250, required=False)
    status = forms.CharField(max_length=2)
    payment = forms.CharField(max_length=2)
    total_amount = forms.CharField(max_length=250)
    # tendered = forms.CharField(max_length=250)

    class Meta:
        model = models.Purchase
        fields = ('code', 'client', 'contact', 'status', 'payment', 'total_amount', )

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.Purchase.objects.get(code=f"{pref}{code:05d}")
                    code = code + 1
                except:
                    return f"{pref}{code:05d}"
                    break
        else:
            return code

    def save(self):
        instance = self.instance
        Products = []

        if 'product_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('product_id[]')):
                product = models.Products.objects.get(id=val)
                buy = self.data.getlist('product_price[]')[k]
                qty = self.data.getlist('product_quantity[]')[k]
                freeqty = self.data.getlist('product_free_quantity[]')[k]
                total = float(buy) * float(qty)

                try:
                    Products.append(models.PurchaseProducts(purchase=instance, product=product, buy=buy, quantity=qty, total_amount=total, free_quantity=freeqty))
                    print("SaleProducts..")
                except Exception as err:
                    print(err)
                    return False
        try:
            instance.save()
            models.PurchaseProducts.objects.filter(purchase=instance).delete()
            models.PurchaseProducts.objects.bulk_create(Products)

        except Exception as err:
            print(err)
            return False


class SaveEmployee(forms.ModelForm):
    name = forms.CharField(max_length=250)
    phone = forms.CharField(max_length=250)
    nid = forms.CharField(max_length=250)
    type = forms.CharField(max_length=2)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Employee
        fields = ('name', 'phone', 'nid', 'type', 'status',)


class SaveRoad(forms.ModelForm):
    name = forms.CharField(max_length=250)

    class Meta:
        model = models.Road
        fields = ('name',)


class SaveClient(forms.ModelForm):
    name = forms.CharField(max_length=100)
    shop = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=20)
    address = forms.CharField(max_length=100)
    road = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_road'}
    )

    class Meta:
        model = models.Client
        fields = ('name', 'shop', 'mobile', 'address', 'road')
