from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('',views.home, name="home-page"),
    path('login',views.login_page,name='login-page'),
    path('register',views.userregister,name='register-page'),
    path('save_register',views.save_register,name='register-user'),
    path('user_login',views.login_user,name='login-user'),
    path('home',views.home,name='home-page'),
    path('logout',views.logout_user,name='logout'),
    path('profile',views.profile,name='profile-page'),
    path('update_password',views.update_password,name='update-password'),
    path('update_profile',views.update_profile,name='update-profile'),
    path('users',views.users,name='user-page'),
    path('manage_user',views.manage_user,name='manage-user'),
    path('manage_user/<int:pk>',views.manage_user,name='manage-user-pk'),
    path('save_user',views.save_user,name='save-user'),
    path('delete_user/<int:pk>',views.delete_user,name='delete-user'),
    path('category',views.category,name='category-page'),
    path('manage_category',views.manage_category,name='manage-category'),
    path('manage_category/<int:pk>',views.manage_category,name='manage-category-pk'),
    path('view_category/<int:pk>',views.view_category,name='view-category-pk'),
    path('save_category',views.save_category,name='save-category'),
    path('delete_category/<int:pk>',views.delete_category,name='delete-category'),
    path('brand',views.brand,name='brand-page'),
    path('manage_brand',views.manage_brand,name='manage-brand'),
    path('manage_brand/<int:pk>',views.manage_brand,name='manage-brand-pk'),
    path('view_brand/<int:pk>',views.view_brand,name='view-brand-pk'),
    path('save_brand',views.save_brand,name='save-brand'),
    path('delete_brand/<int:pk>',views.delete_brand,name='delete-brand'),
    path('products',views.products,name='product-page'),
    path('manage_product',views.manage_product,name='manage-product'),
    path('manage_product/<int:pk>',views.manage_product,name='manage-product-pk'),
    path('view_product',views.view_product,name='view-product'),
    path('view_product/<int:pk>',views.view_product,name='view-product-pk'),
    path('save_product',views.save_product,name='save-product'),
    path('delete_product/<int:pk>',views.delete_product,name='delete-product'),
    path('manage_stockin/<int:pid>',views.manage_stockin,name='manage-stockin-pid'),
    path('manage_stockin/<int:pid>/<int:pk>',views.manage_stockin,name='manage-stockin-pid-pk'),
    path('save_stockin',views.save_stockin,name='save-stockin'),
    path('delete_stockin/<int:pk>',views.delete_stockin,name='delete-stockin'),
    path('sales',views.sales,name='sale-page'),
    path('manage_sale',views.manage_sale,name='manage-sale'),
    path('manage_sale/<int:pk>',views.manage_sale,name='manage-sale-pk'),
    path('view_sale',views.view_sale,name='view-sale'),
    path('view_sale/<int:pk>',views.view_sale,name='view-sale-pk'),
    path('save_sale',views.save_sale,name='save-sale'),
    path('delete_sale/<int:pk>',views.delete_sale,name='delete-sale'),
    path('update_transaction_form/<int:pk>',views.update_transaction_form,name='transacton-update-status'),
    path('update_transaction_status',views.update_transaction_status,name='update-sale-status'),
    path('daily_report',views.daily_report,name='daily-report'),
    path('daily_report/<str:date>',views.daily_report,name='daily-report-date'),
    path('purchase',views.purchase,name='purchase-page'),
    path('manage_purchase',views.manage_purchase,name='manage-purchase'),
    path('manage_purchase/<int:pk>',views.manage_purchase,name='manage-purchase-pk'),
    path('view_purchase',views.view_purchase,name='view-purchase'),
    path('view_purchase/<int:pk>',views.view_purchase,name='view-purchase-pk'),
    path('save_purchase',views.save_purchase,name='save-purchase'),
    path('delete_purchase/<int:pk>',views.delete_purchase,name='delete-purchase'),
    path('update_receipt_form/<int:pk>',views.update_receipt_form,name='receipt-update-status'),
    path('update_receipt_status',views.update_receipt_status,name='update-purchase-status'),
    path('ajax/load-purchase-product/', views.load_purchase_product, name='ajax_load_purchase_product'),
    path('employee',views.employee,name='employee-page'),
    path('manage_employee',views.manage_employee,name='manage-employee'),
    path('manage_employee/<int:pk>',views.manage_employee,name='manage-employee-pk'),
    path('save_employee',views.save_employee,name='save-employee'),
    path('view_employee',views.view_employee,name='view-employee'),
    path('view_employee/<int:pk>',views.view_employee,name='view-employee-pk'),
    path('delete_employee/<int:pk>',views.delete_employee,name='delete-employee'),
    path('road',views.road,name='road-page'),
    path('manage_road',views.manage_road,name='manage-road'),
    path('manage_road/<int:pk>',views.manage_road,name='manage-road-pk'),
    path('save_road',views.save_road,name='save-road'),
    path('delete_road/<int:pk>',views.delete_road,name='delete-road'),
    path('client',views.client,name='client-page'),
    path('manage_client',views.manage_client,name='manage-client'),
    path('manage_client/<int:pk>',views.manage_client,name='manage-client-pk'),
    path('view_client/<int:pk>',views.view_client,name='view-client-pk'),
    path('save_client',views.save_client,name='save-client'),
    path('delete_client/<int:pk>',views.delete_client,name='delete-client'),
    path('print-sales/<id>', views.print_sales, name='print-sales'),
    path('ajax/load-product/', views.load_product, name='ajax_load_product'),
    path('low_stock',views.low_stock,name='low-stock'),
    path('all_commission',views.all_commission,name='all-commission'),
    path('commission-preview', views.commission_preview, name="commission-preview"),
    path('commission_bill',views.commission_bill,name='commission-bill-page'),
    path('manage_commission_bill',views.manage_commission_bill,name='manage-commission-bill'),
    path('manage_commission_bill/<int:pk>',views.manage_commission_bill,name='manage-commission-bill-pk'),
    path('view_commission_bill',views.view_commission_bill,name='view-commission-bill'),
    path('view_commission_bill/<int:pk>',views.view_commission_bill,name='view-commission-bill-pk'),
    path('save_commission_bill',views.save_commission_bill,name='save-commission-bill'),
    path('delete_commission_bill/<int:pk>',views.delete_commission_bill,name='delete-commission-bill'),
    path('free_product_report', views.free_product_report, name="free-product-report"),
    path('free_report', views.free_report, name="free-report"),
    path('advance',views.advance,name='advance-page'),
    path('manage_advance',views.manage_advance,name='manage-advance'),
    path('manage_advance/<int:pk>',views.manage_advance,name='manage-advance-pk'),
    path('view_advance',views.view_advance,name='view-advance'),
    path('view_advance/<int:pk>',views.view_advance,name='view-advance-pk'),
    path('save_advance',views.save_advance,name='save-advance'),
    path('delete_advance/<int:pk>',views.delete_advance,name='delete-advance'),
    path('update_advance_form/<int:pk>',views.update_advance_form,name='advance-update-status'),
    path('update_advance_status',views.update_advance_status,name='update-advance-status'),
    path('advance_report', views.advance_report, name="advance-report"),
    path('damage',views.damage,name='damage-page'),
    path('manage_damage',views.manage_damage,name='manage-damage'),
    path('manage_damage/<int:pk>',views.manage_damage,name='manage-damage-pk'),
    path('view_damage',views.view_damage,name='view-damage'),
    path('view_damage/<int:pk>',views.view_damage,name='view-damage-pk'),
    path('save_damage',views.save_damage,name='save-damage'),
    path('delete_damage/<int:pk>',views.delete_damage,name='delete-damage'),
    path('update_damage_form/<int:pk>',views.update_damage_form,name='damage-update-status'),
    path('update_damage_status',views.update_damage_status,name='update-damage-status'),
    path('ajax/load-damage-product/', views.load_damage_product, name='ajax_load_damage_product'),
    path('expense',views.expense,name='expense-page'),
    path('manage_expense',views.manage_expense,name='manage-expense'),
    path('manage_expense/<int:pk>',views.manage_expense,name='manage-expense-pk'),
    path('save_expense',views.save_expense,name='save-expense'),
    path('delete_expense/<int:pk>',views.delete_expense,name='delete-expense'),
    path('surplus',views.surplus,name='surplus-page'),
    path('manage_surplus',views.manage_surplus,name='manage-surplus'),
    path('manage_surplus/<int:pk>',views.manage_surplus,name='manage-surplus-pk'),
    path('view_surplus',views.view_surplus,name='view-surplus'),
    path('view_surplus/<int:pk>',views.view_surplus,name='view-surplus-pk'),
    path('save_surplus',views.save_surplus,name='save-surplus'),
    path('delete_surplus/<int:pk>',views.delete_surplus,name='delete-surplus'),
    path('update_surplus_form/<int:pk>',views.update_surplus_form,name='surplus-update-month'),
    path('update_surplus_month',views.update_surplus_month,name='update-surplus-month'),
    path('loan',views.loan,name='loan-page'),
    path('manage_loan',views.manage_loan,name='manage-loan'),
    path('manage_loan/<int:pk>',views.manage_loan,name='manage-loan-pk'),
    path('view_loan',views.view_loan,name='view-loan'),
    path('view_loan/<int:pk>',views.view_loan,name='view-loan-pk'),
    path('save_loan',views.save_loan,name='save-loan'),
    path('delete_loan/<int:pk>',views.delete_loan,name='delete-loan'),
    path('deliveryman_report', views.deliveryman_report, name="deliveryman-report"),
    path('salesman_report', views.salesman_report, name="salesman-report"),
    path('damage_products',views.damage_products,name='damage-product-page'),
    path('damage_report',views.damage_report,name='damage-report'),
    path('fresh_product_report',views.fresh_product_report,name='fresh-product-report'),
    path('dues_report',views.dues_report,name='dues-report'),

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)