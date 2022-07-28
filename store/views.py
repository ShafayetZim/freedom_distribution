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
        'system_short_name' : 'FDSMS',
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
    context['category'] = models.Category.objects.count()
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
                messages.success(request, "Category has been saved successfully.")
            else:
                messages.success(request, "Category has been updated successfully.")
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
        resp['msg'] = 'Category ID is invalid'
    else:
        try:
            models.Category.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Category has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Category Failed"

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
    context['category'] = models.Category.objects.all()
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
    context['category'] = models.Category.objects.all()
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
    context['sales'] = models.Sales.objects.order_by('-date_added').all()
    return render(request, 'sales.html', context)


@login_required
def save_sale(request):
    resp = { 'status': 'failed', 'msg' : '', 'id': '' }
    id=2
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            sale = models.Sales.objects.get(id = post['id'])
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
        # context['items'] = {}
        context['pitems'] = {}
    else:
        context['sale'] = models.Sales.objects.get(id=pk)
        # context['items'] = models.LaundryItems.objects.filter(laundry__id=pk).all()
        context['pitems'] = models.SaleProducts.objects.filter(sale__id=pk).all()

    return render(request, 'view_sale.html', context)


@login_required
def manage_sale(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_sale'
    context['page_title'] = 'Manage sale'
    context['category'] = models.Category.objects.all()
    context['products'] = models.Products.objects.filter(delete_flag=0, status=1).all()
    # context['prices'] = models.Prices.objects.filter(delete_flag=0, status=1).all()
    context['road'] = models.Road.objects.all()
    context['salesman'] = models.Employee.objects.filter(type=1).all()
    context['deliveryman'] = models.Employee.objects.filter(type=2).all()
    if pk is None:
        context['sale'] = {}
        # context['items'] = {}
        context['pitems'] = {}
    else:
        context['sale'] = models.Sales.objects.get(id=pk)
        # context['items'] = models.LaundryItems.objects.filter(laundry__id=pk).all()
        context['pitems'] = models.SaleProducts.objects.filter(sale__id=pk).all()

    return render(request, 'manage_sale.html', context)


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
            models.Sales.objects.filter(pk = request.POST['id']).update(status = request.POST['status'])
            messages.success(request, "Transaction Status has been updated successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_sale(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Sale ID is invalid'
    else:
        try:
            models.Sales.objects.filter(pk = pk).delete()
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
    for sale in context['sales']:
        grand_total += float(sale.total_amount)
    context['grand_total'] = grand_total

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
        # context['items'] = {}
        context['pitems'] = {}
    else:
        context['purchase'] = models.Purchase.objects.get(id=pk)
        # context['items'] = models.LaundryItems.objects.filter(laundry__id=pk).all()
        context['pitems'] = models.PurchaseProducts.objects.filter(purchase__id=pk).all()

    return render(request, 'view_purchase.html', context)


@login_required
def manage_purchase(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_purchase'
    context['page_title'] = 'Manage purchase'
    context['products'] = models.Products.objects.filter(delete_flag=0, status=1).all()
    # context['prices'] = models.Prices.objects.filter(delete_flag=0, status=1).all()
    if pk is None:
        context['purchase'] = {}
        # context['items'] = {}
        context['pitems'] = {}
    else:
        context['purchase'] = models.Purchase.objects.get(id=pk)
        # context['items'] = models.LaundryItems.objects.filter(laundry__id=pk).all()
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
    else:
        context['client'] = models.Client.objects.get(id=pk)

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
    print(invoice_item)
    total_qty = invoice_item.aggregate(Sum('quantity'))
    total_qty = total_qty.get('quantity__sum')
    print(total_qty)

    context = {
        'page-title': "invoice print",
        'sales_item': invoice_item,
        'total_qty': total_qty,
        'invoice_info': invoice,
    }
    pdf = render_to_pdf('sales_print.html', context)
    return HttpResponse(pdf, content_type='application/pdf')


def load_product(request):
    category_id = request.GET.get('category')
    products = models.Products.objects.filter(category_id=category_id).order_by('name')
    context = {'products': products}
    return render(request, 'dropdown_sales.html', context)


# low stock
@login_required
def low_stock(request):
    context = context_data(request)
    context['page'] = 'low_stock'
    context['page_title'] = 'Low Stocks'
    context['products'] = models.Products.objects.all()

    return render(request, 'low_stock.html', context)