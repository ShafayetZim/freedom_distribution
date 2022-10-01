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
        fields = ('email', 'username','first_name', 'last_name',)

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


class SaveBrand(forms.ModelForm):
    name = forms.CharField(max_length=250)

    class Meta:
        model = models.Brand
        fields = ('name',)

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
    code = forms.CharField(max_length=250)
    brand = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_brand'}
    )
    description = forms.CharField(max_length=250, required=False)
    buy = forms.CharField(max_length=250)
    price = forms.CharField(max_length=250)
    mrp = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Products
        fields = ('name', 'code', 'description', 'brand', 'buy', 'price', 'mrp', 'status', )

    def clean_code(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        code = self.cleaned_data['code']
        try:
            if id > 0:
                product = models.Products.objects.exclude(id = id).get(code = code, delete_flag = 0)
            else:
                product = models.Products.objects.get(code = code, delete_flag = 0)
        except:
            return code
        raise forms.ValidationError("Product code already exists.")


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
    cost = forms.CharField(max_length=250)
    extra = forms.CharField(max_length=250)

    class Meta:
        model = models.Sales
        fields = ('code', 'client', 'contact', 'road', 'salesman', 'deliveryman', 'brand', 'status', 'payment', 'total_amount', 'tendered', 'cost', 'extra',)

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.Sales.objects.get(code=f"{pref}{code:02d}")
                    code = code + 1
                except:
                    return f"{pref}{code:02d}"
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
        Returns = []
        Clients = []
        Brands = []

        if 'product_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('product_id[]')):
                product = models.Products.objects.get(id=val)
                brand = self.data.getlist('product_brand[]')[k]
                buy = self.data.getlist('product_buy[]')[k]
                price = self.data.getlist('product_price[]')[k]
                qty = self.data.getlist('product_quantity[]')[k]
                freeqty = self.data.getlist('product_free_quantity[]')[k]
                goodqty = self.data.getlist('product_good_quantity[]')[k]
                damageqty = self.data.getlist('product_damage_quantity[]')[k]
                sign = self.data.getlist('product_sign[]')[k]
                total = float(price) * (float(qty) - float(goodqty) - float(damageqty))
                # free = self.cleaned_data['free_quantity']
                try:
                    Products.append(models.SaleProducts(sale=instance, product=product, brand=brand, buy=buy, price=price, quantity=qty, total_amount=total, free_quantity=freeqty, good_quantity=goodqty, damage_quantity=damageqty, sign=sign))
                    print("SaleProducts..")
                except Exception as err:
                    print(err)
                    return False

        if 'return_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('return_id[]')):
                product = models.Products.objects.get(id=val)
                brand = self.data.getlist('return_brand[]')[k]
                buy = self.data.getlist('return_buy[]')[k]
                price = self.data.getlist('return_price[]')[k]
                qty = self.data.getlist('return_quantity[]')[k]
                freeqty = self.data.getlist('return_free_quantity[]')[k]
                goodqty = self.data.getlist('return_good_quantity[]')[k]
                damageqty = self.data.getlist('return_damage_quantity[]')[k]
                sign = self.data.getlist('return_sign[]')[k]
                total = float(price)
                # free = self.cleaned_data['free_quantity']
                try:
                    Returns.append(models.SaleReturn(sale=instance, product=product, brand=brand, buy=buy, price=price, quantity=qty, total_amount=total, free_quantity=freeqty, good_quantity=goodqty, damage_quantity=damageqty, sign=sign))
                    print("SaleReturns..")
                except Exception as err:
                    print(err)
                    return False

        if 'client_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('client_id[]')):
                prices = models.Client.objects.get(id= val)
                brand = self.data.getlist('due_brand[]')[k]
                note = self.data.getlist('due_note[]')[k]
                due = self.data.getlist('due_price[]')[k]
                new = self.data.getlist('due_new[]')[k]
                previous = self.data.getlist('due_previous[]')[k]
                date = self.data.getlist('due_date[]')[k]
                paid = float(new) + float(previous)
                total = float(due) - float(paid)
                try:
                    Clients.append(models.SaleDue(sale=instance, client=prices, brand=brand, note=note, due=due, new=new, previous=previous, date=date, paid=paid, balance=total))
                    print("ClientDues..")
                except Exception as err:
                    print(err)
                    return False

        if 'brand_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('brand_id[]')):
                brand = models.Brand.objects.get(id= val)
                commission = self.data.getlist('brand_price[]')[k]
                total = float(commission)
                try:
                    Brands.append(models.SaleCommission(sale=instance, brand=brand, commission=commission, total_amount=total))
                    print("BrandCommissions..")
                except Exception as err:
                    print(err)
                    return False
        try:
            instance.save()
            models.SaleProducts.objects.filter(sale=instance).delete()
            models.SaleProducts.objects.bulk_create(Products)
            models.SaleReturn.objects.filter(sale=instance).delete()
            models.SaleReturn.objects.bulk_create(Returns)
            models.SaleDue.objects.filter(sale=instance).delete()
            models.SaleDue.objects.bulk_create(Clients)
            models.SaleCommission.objects.filter(sale=instance).delete()
            models.SaleCommission.objects.bulk_create(Brands)
        except Exception as err:
            print(err)
            return False


class SavePurchase(forms.ModelForm):
    code = forms.CharField(max_length=250)
    brand = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_brand'}
    )
    status = forms.CharField(max_length=2)
    payment = forms.CharField(max_length=2)
    total_amount = forms.CharField(max_length=250)

    class Meta:
        model = models.Purchase
        fields = ('code', 'brand', 'status', 'payment', 'total_amount', )

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


class SaveCommissionBill(forms.ModelForm):
    brand = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_brand'}
    )
    month = forms.CharField(max_length=12)
    bill = forms.CharField(max_length=250)
    collect = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.CommissionBill
        fields = ('brand', 'month', 'bill', 'collect', 'status', )


class SaveAdvance(forms.ModelForm):
    code = forms.CharField(max_length=250)
    brand = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_brand'}
    )
    note = forms.CharField(max_length=250, required=False)
    due_amount = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Online
        fields = ('code', 'brand', 'note', 'due_amount', 'status', )

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.Online.objects.get(code=f"{pref}{code:04d}")
                    code = code + 1
                except:
                    return f"{pref}{code:04d}"
                    break
        else:
            return code

    def save(self):
        instance = self.instance
        Brands = []
        Credits = []

        if 'brand_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('brand_id[]')):
                brand = models.Brand.objects.get(id=val)
                advance = self.data.getlist('brand_advance[]')[k]
                day = self.data.getlist('brand_date[]')[k]
                total = float(advance)

                try:
                    Brands.append(models.OnlineAdvance(online=instance, brand=brand, advance=advance, day=day, total_amount=total))
                    print("Advance Brand..")
                except Exception as err:
                    print(err)
                    return False

        if 'credit_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('credit_id[]')):
                brand = models.Brand.objects.get(id=val)
                amount = self.data.getlist('credit_amount[]')[k]
                day = self.data.getlist('credit_date[]')[k]
                total = float(amount)

                try:
                    Credits.append(models.OnlineCredit(online=instance, brand=brand, amount=amount, day=day, total_amount=total))
                    print("Advance Credit..")
                except Exception as err:
                    print(err)
                    return False
        try:
            instance.save()
            models.OnlineAdvance.objects.filter(online=instance).delete()
            models.OnlineAdvance.objects.bulk_create(Brands)
            models.OnlineCredit.objects.filter(online=instance).delete()
            models.OnlineCredit.objects.bulk_create(Credits)

        except Exception as err:
            print(err)
            return False


class SaveDamage(forms.ModelForm):
    code = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)
    total_amount = forms.CharField(max_length=250)

    class Meta:
        model = models.DamageSale
        fields = ('code', 'status', 'total_amount', )

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.DamageSale.objects.get(code=f"{pref}{code:04d}")
                    code = code + 1
                except:
                    return f"{pref}{code:04d}"
                    break
        else:
            return code

    def save(self):
        instance = self.instance
        Products = []

        if 'product_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('product_id[]')):
                product = models.Products.objects.get(id=val)
                brand = self.data.getlist('product_brand[]')[k]
                price = self.data.getlist('product_price[]')[k]
                qty = self.data.getlist('product_quantity[]')[k]
                total = float(price)

                try:
                    Products.append(models.DamageProduct(damage=instance, product=product, brand=brand, price=price, quantity=qty, total_amount=total))
                    print("SaleDamageProducts..")
                except Exception as err:
                    print(err)
                    return False
        try:
            instance.save()
            models.DamageProduct.objects.filter(damage=instance).delete()
            models.DamageProduct.objects.bulk_create(Products)

        except Exception as err:
            print(err)
            return False


class SaveExpense(forms.ModelForm):
    name = forms.CharField(max_length=250)

    class Meta:
        model = models.Expense
        fields = ('name',)


class SaveSurplus(forms.ModelForm):
    code = forms.CharField(max_length=250)
    month = forms.CharField(max_length=12)
    total_sale = forms.CharField(max_length=250)
    total_cost = forms.CharField(max_length=250)
    total_extra = forms.CharField(max_length=250)
    total_damage = forms.CharField(max_length=250)
    total_expense = forms.CharField(max_length=250)
    margin = forms.CharField(max_length=250)

    class Meta:
        model = models.Surplus
        fields = ('code', 'month', 'total_sale', 'total_cost', 'total_extra', 'total_damage', 'total_expense', 'margin', )

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.Surplus.objects.get(code=f"{pref}{code:04d}")
                    code = code + 1
                except:
                    return f"{pref}{code:04d}"
                    break
        else:
            return code

    def save(self):
        instance = self.instance
        Expenses = []

        if 'expense_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('expense_id[]')):
                expense = models.Expense.objects.get(id=val)
                note = self.data.getlist('expense_note[]')[k]
                amount = self.data.getlist('expense_amount[]')[k]
                total = float(amount)

                try:
                    Expenses.append(models.Charge(surplus=instance, expense=expense, note=note, amount=amount, total_amount=total))
                    print("SurplusCharges..")
                except Exception as err:
                    print(err)
                    return False
        try:
            instance.save()
            models.Charge.objects.filter(surplus=instance).delete()
            models.Charge.objects.bulk_create(Expenses)

        except Exception as err:
            print(err)
            return False


class SaveLoan(forms.ModelForm):
    code = forms.CharField(max_length=250)
    note = forms.CharField(max_length=250, required=False)
    employee = forms.Select(
        attrs={'class': 'form-control form-control-sm rounded-0', 'value': '', 'id': 'id_employee'}
    )
    due_amount = forms.CharField(max_length=250)

    class Meta:
        model = models.Loan
        fields = ('code', 'note', 'employee', 'due_amount',)

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.Loan.objects.get(code=f"{pref}{code:04d}")
                    code = code + 1
                except:
                    return f"{pref}{code:04d}"
                    break
        else:
            return code

    def save(self):
        instance = self.instance
        Debits = []
        Credits = []

        if 'debit_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('debit_id[]')):
                debit = models.Debit.objects.get(id=val)
                day = self.data.getlist('debit_date[]')[k]
                amount = self.data.getlist('debit_amount[]')[k]
                total = float(amount)

                try:
                    Debits.append(models.LoanDebit(loan=instance, debit=debit, day=day, amount=amount, total_amount=total))
                    print("LoanDebits..")
                except Exception as err:
                    print(err)
                    return False

        if 'credit_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('credit_id[]')):
                credit = models.Credit.objects.get(id=val)
                day = self.data.getlist('credit_date[]')[k]
                amount = self.data.getlist('credit_amount[]')[k]
                total = float(amount)

                try:
                    Credits.append(models.LoanCredit(loan=instance, credit=credit, day=day, amount=amount, total_amount=total))
                    print("LoanCredits..")
                except Exception as err:
                    print(err)
                    return False

        try:
            instance.save()
            models.LoanDebit.objects.filter(loan=instance).delete()
            models.LoanDebit.objects.bulk_create(Debits)
            models.LoanCredit.objects.filter(loan=instance).delete()
            models.LoanCredit.objects.bulk_create(Credits)

        except Exception as err:
            print(err)
            return False


class SaveExpenditure(forms.ModelForm):
    code = forms.CharField(max_length=250)
    total_amount = forms.CharField(max_length=250)

    class Meta:
        model = models.Expenditure
        fields = ('code', 'total_amount', )

    def clean_code(self):
        code = self.cleaned_data['code']

        if code == 'generate':
            pref = datetime.datetime.now().strftime('%y%m%d')
            code = 1
            while True:
                try:
                    check = models.Expenditure.objects.get(code=f"{pref}{code:04d}")
                    code = code + 1
                except:
                    return f"{pref}{code:04d}"
                    break
        else:
            return code

    def save(self):
        instance = self.instance
        Expenses = []

        if 'expense_id[]' in self.data:
            for k, val in enumerate(self.data.getlist('expense_id[]')):
                expense = models.Expense.objects.get(id=val)
                note = self.data.getlist('expense_note[]')[k]
                amount = self.data.getlist('expense_amount[]')[k]
                total = float(amount)

                try:
                    Expenses.append(models.ExpenditureCharge(expenditure=instance, expense=expense, note=note, amount=amount, total_amount=total))
                    print("ExpenditureCharges..")
                except Exception as err:
                    print(err)
                    return False
        try:
            instance.save()
            models.ExpenditureCharge.objects.filter(expenditure=instance).delete()
            models.ExpenditureCharge.objects.bulk_create(Expenses)

        except Exception as err:
            print(err)
            return False


class SaveInvestment(forms.ModelForm):
    invest = forms.CharField(max_length=250)

    class Meta:
        model = models.Investment
        fields = ('invest',)


class SaveOnlineTransaction(forms.ModelForm):
    amount = forms.CharField(max_length=250)
    note = forms.CharField(max_length=250)

    class Meta:
        model = models.OnlineTransaction
        fields = ('amount', 'note',)


class SaveBank(forms.ModelForm):
    amount = forms.CharField(max_length=250)
    note = forms.CharField(max_length=250, required=False)

    class Meta:
        model = models.Bank
        fields = ('amount', 'note',)


class SaveBankTransaction(forms.ModelForm):
    amount = forms.CharField(max_length=250)
    type = forms.CharField(max_length=2)

    class Meta:
        model = models.BankTransaction
        fields = ('amount', 'type',)
