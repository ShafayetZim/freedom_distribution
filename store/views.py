import json
import datetime
from email import message
from cryptography import CryptographyDeprecationWarning
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from store import models, forms
from django.db.models import Q, Sum
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from store.utils import render_to_pdf

# Create your views here.
def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host' : abs_uri,
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'Freedom Distribution',
        'system_short_name' : 'Freedom',
        'topbar' : True,
        'footer' : True,
    }

    return context


def userregister(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_title'] = "User Registration"
    if request.user.is_authenticated:
        return redirect("home-page")
    return render(request, 'register.html', context)


def save_register(request):
    resp={'status':'failed', 'msg':''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = forms.SaveUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully")
            resp['status'] = 'success'
        else:
            for field in forms:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def update_profile(request):
    context = context_data(request)
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile-page")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
def update_password(request):
    context = context_data(request)
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = forms.UpdatePasswords(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    return render(request, 'update_password.html', context)


def login_page(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request, 'login.html', context)


def login_user(request):
    logout(request)
    resp = {"status":'failed', 'msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = "success"
            else:
                resp['msg'] = "Incorrect username of password"
        else:
            resp['msg'] = "Incorrect username of password"
    return HttpResponse(json.dumps(resp), content_type='application/json')


def logout_user(request):
    logout(request)
    return redirect('login-page')


@login_required
def profile(request):
    context = context_data(request)
    context['page'] = 'profile'
    context['page_title'] = "Profile"
    return render(request,'profile.html', context)


@login_required
def users(request):
    context = context_data(request)
    context['page'] = 'users'
    context['page_title'] = "User List"
    context['users'] = User.objects.exclude(pk=request.user.pk).filter(is_superuser = False).all()
    return render(request, 'users.html', context)


@login_required
def save_user(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            user = User.objects.get(id = post['id'])
            form = forms.UpdateUser(request.POST, instance=user)
        else:
            form = forms.SaveUser(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "User has been saved successfully.")
            else:
                messages.success(request, "User has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def manage_user(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_user'
    context['page_title'] = 'Manage User'
    if pk is None:
        context['user'] = {}
    else:
        context['user'] = User.objects.get(id=pk)
    
    return render(request, 'manage_user.html', context)


@login_required
def delete_user(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        try:
            User.objects.filter(pk = pk).delete()
            messages.success(request, "User has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting User Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def home(request):
    context = context_data(request)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    date = datetime.datetime.now()
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    context['brand'] = models.Brand.objects.count()
    context['products'] = models.Products.objects.count()
    context['stocks'] = models.Products.objects.all()
    context['todays_transaction'] = models.Sales.objects.filter(
            date_added__year = year,
            date_added__month = month,
            date_added__day = day,
    ).count()
    context['todays_sales'] = models.Sales.objects.filter(
            date_added__year = year,
            date_added__month = month,
            date_added__day = day,
    ).aggregate(Sum('total_amount'))['total_amount__sum']
    return render(request, 'home.html', context)


@login_required
def category(request):
    context = context_data(request)
    context['page'] = 'Category'
    context['page_title'] = "Category List"
    context['categories'] = models.Category.objects.filter(delete_flag = 0).all()
    return render(request, 'category.html', context)


@login_required
def save_category(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            category = models.Category.objects.get(id = post['id'])
            form = forms.SaveCategory(request.POST, instance=category)
        else:
            form = forms.SaveCategory(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Group has been saved successfully.")
            else:
                messages.success(request, "Group has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_category'
    context['page_title'] = 'View Category'
    if pk is None:
        context['category'] = {}
    else:
        context['category'] = models.Category.objects.get(id=pk)
    
    return render(request, 'view_category.html', context)


@login_required
def manage_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_category'
    context['page_title'] = 'Manage category'
    if pk is None:
        context['category'] = {}
    else:
        context['category'] = models.Category.objects.get(id=pk)
    
    return render(request, 'manage_category.html', context)


@login_required
def delete_category(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Group ID is invalid'
    else:
        try:
            models.Category.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Group has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Group Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def brand(request):
    context = context_data(request)
    context['page'] = 'Brand'
    context['page_title'] = "Brand List"
    context['brands'] = models.Brand.objects.filter(delete_flag=0).all()
    return render(request, 'brand.html', context)


@login_required
def save_brand(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            brand = models.Brand.objects.get(id = post['id'])
            form = forms.SaveBrand(request.POST, instance=brand)
        else:
            form = forms.SaveBrand(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Brand has been saved successfully.")
            else:
                messages.success(request, "Brand has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_brand(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_brand'
    context['page_title'] = 'View Brand'
    if pk is None:
        context['brand'] = {}
    else:
        context['brand'] = models.Brand.objects.get(id=pk)

    return render(request, 'view_brand.html', context)


@login_required
def manage_brand(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_brand'
    context['page_title'] = 'Manage Brand'
    if pk is None:
        context['brand'] = {}
    else:
        context['brand'] = models.Brand.objects.get(id=pk)

    return render(request, 'manage_brand.html', context)


@login_required
def delete_brand(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Brand ID is invalid'
    else:
        try:
            models.Brand.objects.filter(pk=pk).update(delete_flag=1)
            messages.success(request, "Brand has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Brand Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def products(request):
    context = context_data(request)
    context['page'] = 'Product'
    context['page_title'] = "Product List"
    context['products'] = models.Products.objects.filter(delete_flag = 0).all()
    return render(request, 'products.html', context)


@login_required
def save_product(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            product = models.Products.objects.get(id = post['id'])
            form = forms.SaveProducts(request.POST, instance=product)
        else:
            form = forms.SaveProducts(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Product has been saved successfully.")
                pid = models.Products.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Product has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_product(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_product'
    context['page_title'] = 'View Product'
    if pk is None:
        context['product'] = {}
        context['stockins'] = {}
    else:
        context['product'] = models.Products.objects.get(id=pk)
        context['stockins'] = models.StockIn.objects.filter(product__id=pk)
        context['stockouts'] = models.SaleProducts.objects.filter(product__id=pk).order_by('sale__code')
    
    return render(request, 'view_product.html', context)


@login_required
def manage_product(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_product'
    context['page_title'] = 'Manage product'
    context['brand'] = models.Brand.objects.filter(delete_flag=0).all()
    if pk is None:
        context['product'] = {}
    else:
        context['product'] = models.Products.objects.get(id=pk)
    
    return render(request, 'manage_product.html', context)


@login_required
def delete_product(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Product ID is invalid'
    else:
        try:
            models.Products.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Product has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Product Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def manage_stockin(request, pid=None, pk=None):
    context = context_data(request)
    context['page'] = 'manage_stockin'
    context['page_title'] = 'Manage Stockin'
    context['pid'] = pid
    print(pid)
    print(pk)
    if pk is None:
        context['stockin'] = {}
    else:
        context['stockin'] = models.StockIn.objects.get(id=pk)

    return render(request, 'manage_stockin.html', context)


@login_required
def save_stockin(request):
    resp = { 'status': 'failed', 'msg' : ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            stockin = models.StockIn.objects.get(id = post['id'])
            form = forms.SaveStockIn(request.POST, instance=stockin)
        else:
            form = forms.SaveStockIn(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Stock Entry has been saved successfully.")
            else:
                messages.success(request, "Stock Entry has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_stockin(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Stock-in ID is invalid'
    else:
        try:
            models.StockIn.objects.filter(pk = pk).delete()
            messages.success(request, "Stock Entry Details has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Stock Entry Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def sales(request):
    context = context_data(request)
    context['page'] = 'sale'
    context['page_title'] = "Sale List"
    context['sales'] = models.Sales.objects.order_by('status', '-date_added').all()
    return render(request, 'sales.html', context)


@login_required
def save_sale(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    id=2
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            sale = models.Sales.objects.get(id=post['id'])
            form = forms.SaveSale(request.POST, instance=sale)
        else:
            form = forms.SaveSale(request.POST)
        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Sales has been saved successfully.")
                pid = models.Sales.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Sales has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_sale(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_sale'
    context['page_title'] = 'View Sale'
    if pk is None:
        context['sale'] = {}
        context['items'] = {}
        context['pitems'] = {}
        context['ritems'] = {}
        context['bitems'] = {}
    else:
        context['sale'] = models.Sales.objects.get(id=pk)
        context['items'] = models.SaleDue.objects.filter(sale__id=pk).all()
        context['pitems'] = models.SaleProducts.objects.filter(sale__id=pk).all()
        context['ritems'] = models.SaleReturn.objects.filter(sale__id=pk).all()
        context['bitems'] = models.SaleCommission.objects.filter(sale__id=pk).all()

    return render(request, 'view_sale.html', context)


@login_required
def manage_sale(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_sale'
    context['page_title'] = 'Manage sale'
    context['brand'] = models.Brand.objects.filter(delete_flag=0).all()
    context['products'] = models.Products.objects.filter(delete_flag=0, status=1).all()
    context['client'] = models.Client.objects.filter(delete_flag=0).all()
    context['brands'] = models.Brand.objects.filter(delete_flag=0).all()
    context['road'] = models.Road.objects.all()
    context['salesman'] = models.Employee.objects.filter(type=1).all()
    context['deliveryman'] = models.Employee.objects.filter(type=2).all()
    if pk is None:
        context['sale'] = {}
        context['items'] = {}
        context['pitems'] = {}
        context['ritems'] = {}
        context['bitems'] = {}
    else:
        context['sale'] = models.Sales.objects.get(id=pk)
        context['items'] = models.SaleDue.objects.filter(sale__id=pk).all()
        context['pitems'] = models.SaleProducts.objects.filter(sale__id=pk).all()
        context['ritems'] = models.SaleReturn.objects.filter(sale__id=pk).all()
        context['bitems'] = models.SaleCommission.objects.filter(sale__id=pk).all()

    return render(request, 'manage_sale.html', context)


@login_required
def edit_sale(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_sale'
    context['page_title'] = 'Manage sale'
    context['brand'] = models.Brand.objects.filter(delete_flag=0).all()
    context['products'] = models.Products.objects.filter(delete_flag=0, status=1).all()
    context['prices'] = models.Client.objects.filter(delete_flag=0).all()
    context['brands'] = models.Brand.objects.filter(delete_flag=0).all()
    context['road'] = models.Road.objects.all()
    context['salesman'] = models.Employee.objects.filter(type=1).all()
    context['deliveryman'] = models.Employee.objects.filter(type=2).all()
    if pk is None:
        context['sale'] = {}
        context['items'] = {}
        context['pitems'] = {}
        context['ritems'] = {}
        context['bitems'] = {}
    else:
        context['sale'] = models.Sales.objects.get(id=pk)
        context['items'] = models.SaleDue.objects.filter(sale__id=pk).all()
        context['pitems'] = models.SaleProducts.objects.filter(sale__id=pk).all()
        context['ritems'] = models.SaleReturn.objects.filter(sale__id=pk).all()
        context['bitems'] = models.SaleCommission.objects.filter(sale__id=pk).all()

    return render(request, 'edit_sale.html', context)


@login_required
def update_transaction_form(request, pk=None):
    context = context_data(request)
    context['page'] = 'update_sale'
    context['page_title'] = 'Update Transaction'
    if pk is None:
        context['sale'] = {}
    else:
        context['sale'] = models.Sales.objects.get(id=pk)

    return render(request, 'update_status.html', context)


@login_required
def update_transaction_status(request):
    resp = { 'status' : 'failed', 'msg':''}
    if request.POST['id'] is None:
        resp['msg'] = 'Transaction ID is invalid'
    else:
        try:
            models.Sales.objects.filter(pk=request.POST['id']).update(status=request.POST['status'])
            messages.success(request, "Transaction Status has been updated successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Updating Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_sale(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Sale ID is invalid'
    else:
        try:
            models.Sales.objects.filter(pk=pk).delete()
            messages.success(request, "Sale has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Sale Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def daily_report(request, date=None):
    context = context_data(request)
    context['page'] = 'view_sale'
    context['page_title'] = 'Daily Transaction Report'

    if date is None:
        date = datetime.datetime.now()
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
    else:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')

    context['date'] = date
    context['sales'] = models.Sales.objects.filter(
        date_added__year=year,
        date_added__month=month,
        date_added__day=day,
    )
    grand_total = 0
    extra = 0
    cost = 0
    sum = 0
    for sale in context['sales']:
        grand_total += float(sale.total_amount)
        extra += float(sale.extra)
        cost += float(sale.cost)
    sum = grand_total + extra - cost
    context['grand_total'] = grand_total
    context['extra'] = extra
    context['cost'] = cost
    context['sum'] = sum

    return render(request, 'report.html', context)


@login_required
def purchase(request):
    context = context_data(request)
    context['page'] = 'purchase'
    context['page_title'] = "Purchase List"
    context['purchases'] = models.Purchase.objects.order_by('-date_added').all()
    return render(request, 'purchase.html', context)


@login_required
def save_purchase(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            purchase = models.Purchase.objects.get(id = post['id'])
            form = forms.SavePurchase(request.POST, instance=purchase)
        else:
            form = forms.SavePurchase(request.POST)
        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Purchase has been saved successfully.")
                pid = models.Purchase.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Purchases has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_purchase(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_purchase'
    context['page_title'] = 'View Purchase'
    if pk is None:
        context['purchase'] = {}
        context['pitems'] = {}
    else:
        context['purchase'] = models.Purchase.objects.get(id=pk)
        context['pitems'] = models.PurchaseProducts.objects.filter(purchase__id=pk).all()

    return render(request, 'view_purchase.html', context)


@login_required
def manage_purchase(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_purchase'
    context['page_title'] = 'Manage purchase'
    context['brand'] = models.Brand.objects.filter(delete_flag=0).all()
    context['products'] = models.Products.objects.filter(delete_flag=0, status=1).all()

    if pk is None:
        context['purchase'] = {}
        context['pitems'] = {}
    else:
        context['purchase'] = models.Purchase.objects.get(id=pk)
        context['pitems'] = models.PurchaseProducts.objects.filter(purchase__id=pk).all()

    return render(request, 'manage_purchase.html', context)


@login_required
def update_receipt_form(request, pk=None):
    context = context_data(request)
    context['page'] = 'update_purchase'
    context['page_title'] = 'Update Transaction'
    if pk is None:
        context['purchase'] = {}
    else:
        context['purchase'] = models.Purchase.objects.get(id=pk)

    return render(request, 'update_track.html', context)


@login_required
def update_receipt_status(request):
    resp = { 'status' : 'failed', 'msg':''}
    if request.POST['id'] is None:
        resp['msg'] = 'Transaction ID is invalid'
    else:
        try:
            models.Purchase.objects.filter(pk = request.POST['id']).update(status = request.POST['status'])
            messages.success(request, "Transaction Status has been updated successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Updating Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def delete_purchase(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Sale ID is invalid'
    else:
        try:
            models.Purchase.objects.filter(pk = pk).delete()
            messages.success(request, "Purchase has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Purchase Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def load_purchase_product(request):
    brand_id = request.GET.get('brand')
    products = models.Products.objects.filter(brand_id=brand_id, delete_flag=0, status=1).order_by('name')
    context = {'products': products}
    return render(request, 'dropdown_purchase.html', context)


@login_required
def employee(request):
    context = context_data(request)
    context['page'] = 'employee'
    context['page_title'] = "Employee List"
    context['employee'] = models.Employee.objects.order_by('-date_added').all()
    return render(request, 'employee.html', context)


@login_required
def manage_employee(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_employee'
    context['page_title'] = 'Manage employee'
    if pk is None:
        context['employee'] = {}
    else:
        context['employee'] = models.Employee.objects.get(id=pk)

    return render(request, 'manage_employee.html', context)


@login_required
def save_employee(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            employee = models.Employee.objects.get(id=post['id'])
            form = forms.SaveEmployee(request.POST, instance=employee)
        else:
            form = forms.SaveEmployee(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Employee Entry has been saved successfully.")
            else:
                messages.success(request, "Employee Entry has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_employee(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_employee'
    context['page_title'] = 'View Employee'
    if pk is None:
        context['employee'] = {}
        context['loan'] = {}
    else:
        context['employee'] = models.Employee.objects.get(id=pk)
        context['loan'] = models.Loan.objects.filter(employee__id=pk).order_by('code')

    return render(request, 'view_employee.html', context)


@login_required
def delete_employee(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Employee ID is invalid'
    else:
        try:
            models.Employee.objects.filter(pk=pk).delete()
            messages.success(request, "Employee Entry Details has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Employee Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def road(request):
    context = context_data(request)
    context['page'] = 'road'
    context['page_title'] = "Road List"
    context['road'] = models.Road.objects.order_by('-date_added').all()
    return render(request, 'road.html', context)


@login_required
def manage_road(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_road'
    context['page_title'] = 'Manage road'
    if pk is None:
        context['road'] = {}
    else:
        context['road'] = models.Road.objects.get(id=pk)

    return render(request, 'manage_road.html', context)


@login_required
def save_road(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            road = models.Road.objects.get(id=post['id'])
            form = forms.SaveRoad(request.POST, instance=road)
        else:
            form = forms.SaveRoad(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Road Entry has been saved successfully.")
            else:
                messages.success(request, "Road Entry has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_road(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Road ID is invalid'
    else:
        try:
            models.Road.objects.filter(pk=pk).delete()
            messages.success(request, "Road Entry Details has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Road Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def client(request):
    context = context_data(request)
    context['page'] = 'Client'
    context['page_title'] = "Client List"
    context['clients'] = models.Client.objects.filter(delete_flag=0).all()
    return render(request, 'client.html', context)


@login_required
def save_client(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            client = models.Client.objects.get(id=post['id'])
            form = forms.SaveClient(request.POST, instance=client)
        else:
            form = forms.SaveClient(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Client has been saved successfully.")
            else:
                messages.success(request, "Client has been updated successfully.")
            resp['status'] = 'success'

        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')

    else:
        resp['msg'] = "There's no data sent on the request."

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_client(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_client'
    context['page_title'] = 'View Client'
    if pk is None:
        context['client'] = {}
        context['dues'] = {}
    else:
        context['client'] = models.Client.objects.get(id=pk)
        context['dues'] = models.SaleDue.objects.filter(client__id=pk).order_by('-sale__code')

    return render(request, 'view_client.html', context)


@login_required
def manage_client(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_client'
    context['page_title'] = 'Manage Client'
    context['road'] = models.Road.objects.all()
    if pk is None:
        context['client'] = {}
    else:
        context['client'] = models.Client.objects.get(id=pk)

    return render(request, 'manage_client.html', context)


@login_required
def delete_client(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Client ID is invalid'
    else:
        try:
            models.Client.objects.filter(pk=pk).update(delete_flag=1)
            messages.success(request, "Client has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Client Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def print_sales(request, id=None):
    print(id)
    invoice = get_object_or_404(models.Sales, id=id)
    invoice_item = models.SaleProducts.objects.filter(sale=id)
    return_item = models.SaleReturn.objects.filter(sale=id)
    commission_item = models.SaleCommission.objects.filter(sale=id)
    due_item = models.SaleDue.objects.filter(sale=id)
    print(invoice_item)
    total_qty = invoice_item.aggregate(Sum('quantity'))
    total_qty = total_qty.get('quantity__sum')
    print(total_qty)

    context = {
        'page-title': "invoice print",
        'sales_item': invoice_item,
        'sales_return': return_item,
        'sales_commission': commission_item,
        'sales_due': due_item,
        'total_qty': total_qty,
        'invoice_info': invoice,
    }
    pdf = render_to_pdf('invoice_print.html', context)
    return HttpResponse(pdf, content_type='application/pdf')


def load_product(request):
    brand_id = request.GET.get('brand')
    products = models.Products.objects.filter(brand_id=brand_id, delete_flag=0, status=1).order_by('name')
    context = {'products': products}
    return render(request, 'dropdown_sales.html', context)


# low stock
@login_required
def low_stock(request):
    context = context_data(request)
    context['page'] = 'low_stock'
    context['page_title'] = 'Low Stocks'

    request_data = request.GET
    check_brand = request_data.get("check_brand")
    brand = models.Brand.objects.filter(delete_flag=0).all()

    if check_brand == "All":
        context['products'] = models.Products.objects.all()
    else:
        context['products'] = models.Products.objects.filter(brand=check_brand)

    context['brand'] = brand
    context['check_brand'] = 'check_brand'

    return render(request, 'low_stock.html', context)


def commission_preview(request):
    context = context_data(request)
    context['page'] = 'commission_list'
    context['page_title'] = 'Commission List'

    request_data = request.GET
    check_brand = request_data.get("check_brand")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")

    brand = models.Brand.objects.filter(delete_flag=0).all()
    if check_brand == "All":
        date = models.Sales.objects.filter(date__range=[start_date, end_date])
        commission = models.SaleCommission.objects.filter(sale__in=date)
    else:
        date = models.Sales.objects.filter(date__range=[start_date, end_date])
        commission = models.SaleCommission.objects.filter(sale__in=date, brand=check_brand)

    context['check_brand'] = 'check_brand'
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['brand'] = brand
    context['commission'] = commission

    grand_total = 0
    for item in context['commission']:
        grand_total += float(item.total_amount)
    context['grand_total'] = grand_total

    return render(request, 'commission_preview.html', context)


def all_commission(request):
    context = context_data(request)
    context['page'] = 'commission'
    context['page_title'] = 'All Commission'
    context['items'] = models.SaleCommission.objects.all()

    return render(request, 'all_commission.html', context)


@login_required
def commission_bill(request):
    context = context_data(request)
    context['page'] = 'commission bill'
    context['page_title'] = "Commission Bill"
    context['bills'] = models.CommissionBill.objects.filter(delete_flag=0).all()
    return render(request, 'commission_bill.html', context)


@login_required
def save_commission_bill(request):
    resp = {'status': 'failed', 'msg': '', 'id': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            bill = models.CommissionBill.objects.get(id=post['id'])
            form = forms.SaveCommissionBill(request.POST, instance=bill)
        else:
            form = forms.SaveCommissionBill(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Bill has been saved successfully.")
                pid = models.CommissionBill.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Bill has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_commission_bill(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_bill'
    context['page_title'] = 'View Bill'
    if pk is None:
        context['bills'] = {}
    else:
        context['bills'] = models.CommissionBill.objects.get(id=pk)

    return render(request, 'view_commission_bill.html', context)


@login_required
def manage_commission_bill(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_bill'
    context['page_title'] = 'Manage Bill'
    context['brand'] = models.Brand.objects.filter(delete_flag=0).all()
    if pk is None:
        context['bills'] = {}
    else:
        context['bills'] = models.CommissionBill.objects.get(id=pk)

    return render(request, 'manage_commission_bill.html', context)


@login_required
def delete_commission_bill(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Bill ID is invalid'
    else:
        try:
            models.CommissionBill.objects.filter(pk=pk).update(delete_flag=1)
            messages.success(request, "Bill has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Bill Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def free_product_report(request):
    context = context_data(request)
    context['page'] = 'free_product_report'
    context['page_title'] = 'Free Product Report'

    request_data = request.GET
    check_product = request_data.get("check_product")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")

    product = models.Products.objects.filter(delete_flag=0).all()
    date = models.Sales.objects.filter(date__range=[start_date, end_date])
    free = models.SaleProducts.objects.filter(sale__in=date, product=check_product)

    context['check_product'] = 'check_product'
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['product'] = product
    context['free'] = free

    grand_total = 0
    quantity = 0
    price = 0
    for item in context['free']:
        quantity += float(item.free_quantity)
        price = float(item.price)
    grand_total = price * quantity
    context['quantity'] = quantity
    context['price'] = price
    context['grand_total'] = grand_total

    return render(request, 'free_product_report.html', context)


@login_required
def advance(request):
    context = context_data(request)
    context['page'] = 'advance'
    context['page_title'] = "Advance List"
    context['online'] = models.Online.objects.order_by('status', '-date_added').all()
    return render(request, 'advance.html', context)


@login_required
def save_advance(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            online = models.Online.objects.get(id = post['id'])
            form = forms.SaveAdvance(request.POST, instance=online)
        else:
            form = forms.SaveAdvance(request.POST)
        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Advance has been saved successfully.")
                pid = models.Online.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Advance has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_advance(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_advance'
    context['page_title'] = 'View Advance'
    if pk is None:
        context['online'] = {}
        context['items'] = {}
        context['pitems'] = {}
    else:
        context['online'] = models.Online.objects.get(id=pk)
        context['items'] = models.OnlineCredit.objects.filter(online__id=pk).all()
        context['pitems'] = models.OnlineAdvance.objects.filter(online__id=pk).all()

    return render(request, 'view_advance.html', context)


@login_required
def manage_advance(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_advance'
    context['page_title'] = 'Manage Advance'
    context['brand'] = models.Brand.objects.filter(delete_flag=0).all()
    if pk is None:
        context['online'] = {}
        context['items'] = {}
        context['pitems'] = {}
    else:
        context['online'] = models.Online.objects.get(id=pk)
        context['items'] = models.OnlineCredit.objects.filter(online__id=pk).all()
        context['pitems'] = models.OnlineAdvance.objects.filter(online__id=pk).all()

    return render(request, 'manage_advance.html', context)


def delete_advance(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Advance ID is invalid'
    else:
        try:
            models.Online.objects.filter(pk = pk).delete()
            messages.success(request, "Advance has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Advance Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def update_advance_form(request, pk=None):
    context = context_data(request)
    context['page'] = 'update_advance'
    context['page_title'] = 'Update Advance Transaction'
    if pk is None:
        context['advance'] = {}
    else:
        context['advance'] = models.Online.objects.get(id=pk)

    return render(request, 'update_advance.html', context)


@login_required
def update_advance_status(request):
    resp = { 'status' : 'failed', 'msg':''}
    if request.POST['id'] is None:
        resp['msg'] = 'Transaction ID is invalid'
    else:
        try:
            models.Online.objects.filter(pk=request.POST['id']).update(status=request.POST['status'])
            messages.success(request, "Advance Transaction Status has been updated successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Updating Advance Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def advance_report(request):
    context = context_data(request)
    context['page'] = 'advance_report'
    context['page_title'] = 'Advance Report'

    request_data = request.GET
    check_brand = request_data.get("check_brand")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")

    brand = models.Brand.objects.filter(delete_flag=0).all()
    if check_brand == "All":
        date = models.Online.objects.filter(date__range=[start_date, end_date])
        online = models.OnlineAdvance.objects.filter(online__in=date)
        credit = models.OnlineCredit.objects.filter(online__in=date)
    else:
        date = models.Online.objects.filter(date__range=[start_date, end_date])
        online = models.OnlineAdvance.objects.filter(online__in=date, brand=check_brand)
        credit = models.OnlineCredit.objects.filter(online__in=date, brand=check_brand)

    context['check_brand'] = check_brand
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['brand'] = brand
    context['online'] = online
    context['credit'] = credit

    advance = 0
    amount = 0
    due = 0
    for item in context['online']:
        advance += float(item.advance)

    for item in context['credit']:
        amount += float(item.amount)

    due = advance-amount
    context['advance'] = advance
    context['receive'] = amount
    context['due'] = due

    return render(request, 'advance_report.html', context)


@login_required
def damage(request):
    context = context_data(request)
    context['page'] = 'damage'
    context['page_title'] = "Damage List"
    context['damage'] = models.DamageSale.objects.order_by('status', '-date_added').all()
    return render(request, 'damage.html', context)


@login_required
def save_damage(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            damage = models.DamageSale.objects.get(id=post['id'])
            form = forms.SaveDamage(request.POST, instance=damage)
        else:
            form = forms.SaveDamage(request.POST)
        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Damage Sale has been saved successfully.")
                pid = models.DamageSale.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Damage Sale has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_damage(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_damage'
    context['page_title'] = 'View Damage'
    if pk is None:
        context['damage'] = {}
        context['pitems'] = {}
    else:
        context['damage'] = models.DamageSale.objects.get(id=pk)
        context['pitems'] = models.DamageProduct.objects.filter(damage__id=pk).all()

    return render(request, 'view_damage.html', context)


@login_required
def manage_damage(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_damage'
    context['page_title'] = 'Manage Damage'
    context['brand'] = models.Brand.objects.filter(delete_flag=0).all()
    context['products'] = models.Products.objects.filter(delete_flag=0, status=1).all()
    if pk is None:
        context['damage'] = {}
        context['pitems'] = {}
    else:
        context['damage'] = models.DamageSale.objects.get(id=pk)
        context['pitems'] = models.DamageProduct.objects.filter(damage__id=pk).all()

    return render(request, 'manage_damage.html', context)


def delete_damage(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Damage Sale ID is invalid'
    else:
        try:
            models.DamageSale.objects.filter(pk = pk).delete()
            messages.success(request, "Damage Sale has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Damage Sale Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def update_damage_form(request, pk=None):
    context = context_data(request)
    context['page'] = 'update_damage'
    context['page_title'] = 'Update Damage Transaction'
    if pk is None:
        context['damage'] = {}
    else:
        context['damage'] = models.DamageSale.objects.get(id=pk)

    return render(request, 'update_damage.html', context)


@login_required
def update_damage_status(request):
    resp = { 'status' : 'failed', 'msg':''}
    if request.POST['id'] is None:
        resp['msg'] = 'Transaction ID is invalid'
    else:
        try:
            models.DamageSale.objects.filter(pk=request.POST['id']).update(status=request.POST['status'])
            messages.success(request, "Transaction Status has been updated successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Updating Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def load_damage_product(request):
    brand_id = request.GET.get('brand')
    products = models.Products.objects.filter(brand_id=brand_id, delete_flag=0, status=1).order_by('name')
    context = {'products': products}
    return render(request, 'dropdown_damage.html', context)


@login_required
def expense(request):
    context = context_data(request)
    context['page'] = 'expense'
    context['page_title'] = "Expense List"
    context['expense'] = models.Expense.objects.order_by('-date_added').all()
    return render(request, 'expense.html', context)


@login_required
def manage_expense(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_expense'
    context['page_title'] = 'Manage Expense'
    if pk is None:
        context['expense'] = {}
    else:
        context['expense'] = models.Expense.objects.get(id=pk)

    return render(request, 'manage_expense.html', context)


@login_required
def save_expense(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            expense = models.Expense.objects.get(id=post['id'])
            form = forms.SaveExpense(request.POST, instance=expense)
        else:
            form = forms.SaveExpense(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Expense Entry has been saved successfully.")
            else:
                messages.success(request, "Expense Entry has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_expense(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Expense ID is invalid'
    else:
        try:
            models.Expense.objects.filter(pk=pk).delete()
            messages.success(request, "Expense Entry Details has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Expense Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def surplus(request):
    context = context_data(request)
    context['page'] = 'surplus'
    context['page_title'] = "Surplus List"
    context['surplus'] = models.Surplus.objects.order_by('-date_added').all()
    return render(request, 'surplus.html', context)


@login_required
def save_surplus(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            surplus = models.Surplus.objects.get(id=post['id'])
            form = forms.SaveSurplus(request.POST, instance=surplus)
        else:
            form = forms.SaveSurplus(request.POST)
        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Surplus operation has been saved successfully.")
                pid = models.Surplus.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Surplus operation has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_surplus(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_surplus'
    context['page_title'] = 'View Surplus'
    if pk is None:
        context['surplus'] = {}
        context['pitems'] = {}
    else:
        context['surplus'] = models.Surplus.objects.get(id=pk)
        context['pitems'] = models.Charge.objects.filter(surplus__id=pk).all()

    return render(request, 'view_surplus.html', context)


@login_required
def manage_surplus(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_surplus'
    context['page_title'] = 'Manage Surplus'

    request_data = request.GET
    check_brand = request_data.get("check_brand")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")

    brand = models.Brand.objects.filter(delete_flag=0).all()
    if check_brand == "All":
        other = models.Sales.objects.filter(date__range=[start_date, end_date])
        online = models.SaleProducts.objects.filter(sale__in=other)
        expenditure = models.Expenditure.objects.filter(date__range=[start_date, end_date])

    else:
        other = models.Sales.objects.filter(brand=check_brand, date__range=[start_date, end_date])
        online = models.SaleProducts.objects.filter(sale__in=other)
        expenditure = models.Expenditure.objects.filter(date__range=[start_date, end_date])

    context['check_brand'] = check_brand
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['brand'] = brand
    context['online'] = online
    context['other'] = other
    context['expenditure'] = expenditure

    outlay = 0

    for item in context['expenditure']:
        outlay += float(item.total_amount)

    gross = 0
    knockout = 0

    for item in context['online']:
        gross += float(item.total_amount)
        damage = float(item.damage_quantity)
        price = float(item.price)
        knockout += damage * price
    gross = (5*gross)/100
    knockout = (5*knockout)/100

    cost = 0
    extra = 0
    for item in context['other']:
        cost += float(item.cost)
        extra += float(item.extra)

    context['gross'] = gross
    context['knockout'] = knockout
    context['cost'] = cost
    context['extra'] = extra
    context['outlay'] = outlay

    context['expense'] = models.Expense.objects.filter(delete_flag=0).all()
    if pk is None:
        context['surplus'] = {}
        context['pitems'] = {}
    else:
        context['surplus'] = models.Surplus.objects.get(id=pk)
        context['pitems'] = models.Charge.objects.filter(surplus__id=pk).all()

    return render(request, 'manage_surplus.html', context)


def delete_surplus(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Surplus ID is invalid'
    else:
        try:
            models.Surplus.objects.filter(pk = pk).delete()
            messages.success(request, "Surplus has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Surplus Sale Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def update_surplus_form(request, pk=None):
    context = context_data(request)
    context['page'] = 'update_month'
    context['page_title'] = 'Update Surplus Month'
    if pk is None:
        context['surplus'] = {}
    else:
        context['surplus'] = models.Surplus.objects.get(id=pk)

    return render(request, 'update_month.html', context)


@login_required
def update_surplus_month(request):
    resp = { 'status' : 'failed', 'msg':''}
    if request.POST['id'] is None:
        resp['msg'] = 'Transaction ID is invalid'
    else:
        try:
            models.Surplus.objects.filter(pk=request.POST['id']).update(month=request.POST['month'])
            messages.success(request, "Surplus Month has been updated successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Updating Month Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def free_report(request):
    context = context_data(request)
    context['page'] = 'free_report'
    context['page_title'] = 'Free Report'

    request_data = request.GET
    check_brand = request_data.get("check_brand")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")

    brand = models.Brand.objects.filter(delete_flag=0).all()

    if check_brand != "All":
        free = models.SaleProducts.objects.filter(brand=check_brand,date__range=[start_date, end_date]).values('brand', 'product', 'product__name', 'price').annotate(sum=Sum('free_quantity'))
    else:
        free = models.SaleProducts.objects.filter(date__range=[start_date, end_date]).values('brand', 'product', 'product__name', 'price').annotate(
            sum=Sum('free_quantity'))

    context['check_brand'] = 'check_brand'
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['brand'] = brand
    context['free'] = free

    return render(request, 'free_report.html', context)


@login_required
def loan(request):
    context = context_data(request)
    context['page'] = 'loan'
    context['page_title'] = "Loan List"
    context['loan'] = models.Loan.objects.order_by('-date_added').all()
    return render(request, 'loan.html', context)


@login_required
def manage_loan(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_loan'
    context['page_title'] = 'Manage Loan'
    context['employee'] = models.Employee.objects.filter(delete_flag=0, status=1).all()
    context['debit'] = models.Debit.objects.filter(delete_flag=0).all()
    context['credit'] = models.Credit.objects.filter(delete_flag=0).all()
    if pk is None:
        context['loan'] = {}
        context['items'] = {}
        context['pitems'] = {}
    else:
        context['loan'] = models.Loan.objects.get(id=pk)
        context['items'] = models.LoanDebit.objects.filter(loan__id=pk).all()
        context['pitems'] = models.LoanCredit.objects.filter(loan__id=pk).all()

    return render(request, 'manage_loan.html', context)


@login_required
def save_loan(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            loan = models.Loan.objects.get(id=post['id'])
            form = forms.SaveLoan(request.POST, instance=loan)
        else:
            form = forms.SaveLoan(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Loan Entry has been saved successfully.")
            else:
                messages.success(request, "Loan Entry has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_loan(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_loan'
    context['page_title'] = 'View Loan'
    if pk is None:
        context['loan'] = {}
        context['items'] = {}
        context['pitems'] = {}
    else:
        context['loan'] = models.Loan.objects.get(id=pk)
        context['items'] = models.LoanDebit.objects.filter(loan__id=pk).all()
        context['pitems'] = models.LoanCredit.objects.filter(loan__id=pk).all()

    return render(request, 'view_loan.html', context)


@login_required
def delete_loan(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Loan ID is invalid'
    else:
        try:
            models.Loan.objects.filter(pk=pk).delete()
            messages.success(request, "Loan Entry Details has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Loan Info Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def deliveryman_report(request):
    context = context_data(request)
    context['page'] = 'free_report'
    context['page_title'] = 'Free Report'

    request_data = request.GET
    check_deliveryman = request_data.get("check_deliveryman")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")

    deliveryman = models.Employee.objects.filter(delete_flag=0, type=2).all()

    if check_deliveryman != "All":
        man = models.Sales.objects.filter(deliveryman=check_deliveryman, date__range=[start_date, end_date])
        trade = models.SaleProducts.objects.filter(sale__in=man,).values('brand',).annotate(sum=Sum('total_amount'))
        # damage = models.SaleReturn.objects.filter(sale__in=man, ).values('brand').annotate(sum=Sum('total_amount'))
        damage = models.SaleReturn.objects.filter(sale__in=man,).values('brand').annotate(sum=Sum('total_amount'))
        due = models.SaleDue.objects.filter(sale__in=man,).values('client', 'client__name').annotate(sum=Sum('balance'))
        commission = models.SaleCommission.objects.filter(sale__in=man,).values('brand', 'brand__name').annotate(sum=Sum('total_amount'))

    else:
        man = models.Sales.objects.filter(date__range=[start_date, end_date])
        trade = models.SaleProducts.objects.filter(sale__in=man).values('brand').annotate(
            sum=Sum('total_amount'))
        # damage = models.SaleReturn.objects.filter(sale__in=man, ).values('brand').annotate(sum=Sum('total_amount'))
        damage = models.SaleReturn.objects.filter(sale__in=man, ).values('brand').annotate(sum=Sum('total_amount'))
        due = models.SaleDue.objects.filter(sale__in=man, ).values('client', 'client__name').annotate(
            sum=Sum('balance'))
        commission = models.SaleCommission.objects.filter(sale__in=man, ).values('brand', 'brand__name').annotate(
            sum=Sum('total_amount'))

    context['man'] = man
    context['damage'] = damage

    cost = 0
    extra = 0
    paid = 0
    for item in context['man']:
        cost += float(item.cost)
        extra += float(item.extra)
        paid += float(item.tendered)
    cost = cost
    extra = extra
    paid = paid

    # amount = 0
    # for item in context['damage']:
        # amount += float(item.total_amount)
    # amount = amount

    context['check_deliveryman'] = 'check_deliveryman'
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['deliveryman'] = deliveryman
    context['trade'] = trade
    context['due'] = due
    context['commission'] = commission
    context['cost'] = cost
    context['extra'] = extra
    context['paid'] = paid
    # context['amount'] = amount

    return render(request, 'deliveryman_report.html', context)


def salesman_report(request):
    context = context_data(request)
    context['page'] = 'free_report'
    context['page_title'] = 'Free Report'

    request_data = request.GET
    check_salesman = request_data.get("check_salesman")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")
    salesman = models.Employee.objects.filter(delete_flag=0, type=1).all()

    if check_salesman != "All":
        man = models.Sales.objects.filter(salesman=check_salesman, date__range=[start_date, end_date])
        trade = models.SaleProducts.objects.filter(sale__in=man,).values('brand',).annotate(sum=Sum('total_amount'))
        damage = models.SaleReturn.objects.filter(sale__in=man,).values('brand').annotate(sum=Sum('total_amount'))
        due = models.SaleDue.objects.filter(sale__in=man,).values('client', 'client__name').annotate(sum=Sum('balance'))
        commission = models.SaleCommission.objects.filter(sale__in=man,).values('brand', 'brand__name').annotate(sum=Sum('total_amount'))

    else:
        man = models.Sales.objects.filter(date__range=[start_date, end_date])
        trade = models.SaleProducts.objects.filter(sale__in=man).values('brand').annotate(
            sum=Sum('total_amount'))
        damage = models.SaleReturn.objects.filter(sale__in=man, ).values('brand').annotate(sum=Sum('total_amount'))
        due = models.SaleDue.objects.filter(sale__in=man, ).values('client', 'client__name').annotate(
            sum=Sum('balance'))
        commission = models.SaleCommission.objects.filter(sale__in=man, ).values('brand', 'brand__name').annotate(
            sum=Sum('total_amount'))

    context['man'] = man
    context['damage'] = damage

    cost = 0
    extra = 0
    paid = 0
    for item in context['man']:
        cost += float(item.cost)
        extra += float(item.extra)
        paid += float(item.tendered)
    cost = cost
    extra = extra
    paid = paid

    context['check_salesman'] = check_salesman
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['salesman'] = salesman
    context['trade'] = trade
    context['due'] = due
    context['commission'] = commission
    context['cost'] = cost
    context['extra'] = extra
    context['paid'] = paid

    return render(request, 'salesman_report.html', context)


@login_required
def damage_products(request):
    context = context_data(request)
    context['page'] = 'Damage Product'
    context['page_title'] = "Damage Product List"
    context['products'] = models.Products.objects.filter(delete_flag=0).all()

    request_data = request.GET
    check_brand = request_data.get("check_brand")
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")

    brand = models.Brand.objects.filter(delete_flag=0).all()

    if check_brand != "All":
        free = models.DamageProduct.objects.filter(brand=check_brand,).values('brand', 'product', 'product__name').annotate(sum=Sum('quantity'), add=Sum('price'))
        stockin = models.SaleReturn.objects.filter(brand=check_brand,).values('brand', 'product', 'product__name').annotate(sum=Sum('quantity'), add=Sum('price'))
    else:
        free = models.DamageProduct.objects.values('brand', 'product', 'product__name',).annotate(
            sum=Sum('quantity'), add=Sum('price'))
        stockin = models.SaleReturn.objects.values('brand', 'product', 'product__name', ).annotate(
            sum=Sum('quantity'), add=Sum('price'))

    context['check_brand'] = 'check_brand'
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['brand'] = brand
    context['free'] = free
    context['stockin'] = stockin

    return render(request, 'damage_products.html', context)


@login_required
def damage_report(request):
    context = context_data(request)
    context['page'] = 'Damage Product'
    context['page_title'] = "Damage Product Report"

    request_data = request.GET
    check_brand = request_data.get("check_brand")

    brand = models.Brand.objects.filter(delete_flag=0).all()

    if check_brand != "All":
        product = models.Products.objects.filter(brand=check_brand).all()
    else:
        product = models.Products.objects.all()

    context['check_brand'] = check_brand
    context['brand'] = brand
    context['product'] = product

    return render(request, 'damage_report.html', context)


@login_required
def fresh_product_report(request):
    context = context_data(request)
    context['page'] = 'Fresh Product'
    context['page_title'] = "Fresh Product Report"

    request_data = request.GET
    check_brand = request_data.get("check_brand")

    brand = models.Brand.objects.filter(delete_flag=0).all()

    if check_brand != "All":
        product = models.Products.objects.filter(brand=check_brand).all()
    else:
        product = models.Products.objects.all()

    context['check_brand'] = check_brand
    context['brand'] = brand
    context['product'] = product

    return render(request, 'fresh_product_report.html', context)


def dues_report(request):
    context = context_data(request)
    context['page'] = 'dues_report'
    context['page_title'] = 'Dues Report'

    request_data = request.GET
    check_brand = request_data.get("check_brand")

    brand = models.Brand.objects.filter(delete_flag=0).all()

    if check_brand != "All":
        dues = models.SaleDue.objects.filter(brand=check_brand,).values('brand', 'client', 'client__name',).annotate(sum=Sum('balance'))
    else:
        dues = models.SaleDue.objects.all().values('brand', 'client', 'client__name',).annotate(
            sum=Sum('balance'))

    context['check_brand'] = 'check_brand'
    context['brand'] = brand
    context['dues'] = dues

    return render(request, 'dues_report.html', context)


@login_required
def expenditure(request):
    context = context_data(request)
    context['page'] = 'expenditure'
    context['page_title'] = "Expenditure List"
    context['expenditure'] = models.Expenditure.objects.order_by('-date_added').all()
    return render(request, 'expenditure.html', context)


@login_required
def save_expenditure(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            expenditure = models.Expenditure.objects.get(id=post['id'])
            form = forms.SaveExpenditure(request.POST, instance=expenditure)
        else:
            form = forms.SaveExpenditure(request.POST)
        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Expenditure operation has been saved successfully.")
                pid = models.Expenditure.objects.last().id
                resp['id'] = pid
            else:
                messages.success(request, "Expenditure operation has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_expenditure(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_expenditure'
    context['page_title'] = 'View Expenditure'
    if pk is None:
        context['expenditure'] = {}
        context['pitems'] = {}
    else:
        context['expenditure'] = models.Expenditure.objects.get(id=pk)
        context['pitems'] = models.ExpenditureCharge.objects.filter(expenditure__id=pk).all()

    return render(request, 'view_expenditure.html', context)


@login_required
def manage_expenditure(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_expenditure'
    context['page_title'] = 'Manage Expenditure'

    context['expense'] = models.Expense.objects.filter(delete_flag=0).all()
    if pk is None:
        context['expenditure'] = {}
        context['pitems'] = {}
    else:
        context['expenditure'] = models.Expenditure.objects.get(id=pk)
        context['pitems'] = models.ExpenditureCharge.objects.filter(expenditure__id=pk).all()

    return render(request, 'manage_expenditure.html', context)


def delete_expenditure(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Expenditure ID is invalid'
    else:
        try:
            models.Expenditure.objects.filter(pk = pk).delete()
            messages.success(request, "Expenditure has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Expenditure Sale Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def investment(request):
    context = context_data(request)
    context['page'] = 'Investment'
    context['page_title'] = "Investment List"
    context['investment'] = models.Investment.objects.filter(delete_flag=0).all()
    return render(request, 'investment.html', context)


@login_required
def save_investment(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            investment = models.Investment.objects.get(id = post['id'])
            form = forms.SaveInvestment(request.POST, instance=investment)
        else:
            form = forms.SaveInvestment(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Investment has been saved successfully.")
            else:
                messages.success(request, "Investment has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_investment(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_investment'
    context['page_title'] = 'View Investment'
    if pk is None:
        context['investment'] = {}
    else:
        context['investment'] = models.Investment.objects.get(id=pk)

    return render(request, 'view_investment.html', context)


@login_required
def manage_investment(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_investment'
    context['page_title'] = 'Manage Investment'
    if pk is None:
        context['investment'] = {}
    else:
        context['investment'] = models.Investment.objects.get(id=pk)

    return render(request, 'manage_investment.html', context)


@login_required
def delete_investment(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Investment ID is invalid'
    else:
        try:
            models.Investment.objects.filter(pk=pk).update(delete_flag=1)
            messages.success(request, "Investment has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Investment Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def online_transaction(request):
    context = context_data(request)
    context['page'] = 'online_transaction'
    context['page_title'] = "Online Transaction List"
    context['online'] = models.OnlineTransaction.objects.filter(delete_flag=0).all()
    return render(request, 'online_transaction.html', context)


@login_required
def save_online_transaction(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            online = models.OnlineTransaction.objects.get(id = post['id'])
            form = forms.SaveOnlineTransaction(request.POST, instance=online)
        else:
            form = forms.SaveOnlineTransaction(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Online transaction has been saved successfully.")
            else:
                messages.success(request, "Online transaction has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_online_transaction(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_online_transaction'
    context['page_title'] = 'View Online_Transaction'
    if pk is None:
        context['online'] = {}
    else:
        context['online'] = models.OnlineTransaction.objects.get(id=pk)

    return render(request, 'view_online_transaction.html', context)


@login_required
def manage_online_transaction(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_online_transaction'
    context['page_title'] = 'Manage Online Transaction'
    if pk is None:
        context['online'] = {}
    else:
        context['online'] = models.OnlineTransaction.objects.get(id=pk)

    return render(request, 'manage_online_transaction.html', context)


@login_required
def delete_online_transaction(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Online Transaction ID is invalid'
    else:
        try:
            models.OnlineTransaction.objects.filter(pk=pk).update(delete_flag=1)
            messages.success(request, "Online Transaction has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Online Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

