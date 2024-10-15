from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import (
	vendor_dashboard_home,
    admin_dashboard_home, 
	product_list,
    product_request,
    declined_product_request,
    hidden_product_list,
	vendor_list,
    vendor_details,
	user_list,
	my_active_products,
    my_inactive_products,
    my_unapproved_products,
    my_pending_orders,
    my_cancel_orders,
	create_my_product,
	update_my_product,
    update_my_product_admin,
	my_orders,
	my_orders_details,
    OrdersListJson,
    ProductListJson,
    VendorListJson,
    deactivate_vendor_list,
    dashboard_properties,
    dashboard_shipping_method,
    dashboard_slider,
    dashboard_slider_create,
    dashboard_slider_update,
    dashboard_slider_delete,
    dashboard_free_shipping_create_or_update,
    dashboard_glossary_zipcode_create_or_update,
    dashboard_properties_logo_create_update,
    coupons,
    coupons_create,
    coupons_update,
    orders_list,
    pending_orders_list,
    cancel_orders_list,
    OrderListJson,

    AllProductListJson,
    product_categorys,
    category_create,
    category_update,
    subcategory_create,
    subcategory_update,
    product_category_create,
    product_category_update,

    product_colors_and_sizes,
    product_color_create,
    product_color_update,
    product_size_create,
    product_size_update,

    product_option,
    product_rejected,
    product_commission_update,
    vendor_active_deactive,

    orders_details,
    orders_mark_as_shipment,
    # pages
    mobile_apps_view,
    about_us_view,
    conract_us_view,
    faq_view,
    load_faq_view,
    update_faq_view,
    privacy_policy_view,
    terms_of_use_view,
    refund_return_policy_view,

    # vendor payment
    deu_payment,
    send_payment_request,
    payment_history,
    vendor_deu_payment,
    vendor_payment_history,
    cancel_orders_details,
    cancel_orders_accept,
    cancel_orders_regect,
    load_vendor_payment_request,
    pay_vendor_payment_request,
    load_payment_request,
    update_vendor_profile,
    vendor_change_password_view,
    admin_change_password_view,
    my_cancel_orders_details,
    dashboard_shipping_price_create_or_update,
    my_orders_is_complete,
    vendor_document_save



	)



urlpatterns = [
    #seller
    path('dashboard/vendor/', vendor_dashboard_home, name='vendor_dashboard_home'),
    path('dashboard/vendor/my-active-product/', my_active_products, name='my_active_products'),
    path('dashboard/vendor/my-inactive-product/', my_inactive_products, name='my_inactive_products'),
    path('dashboard/vendor/my-unapproved-product/', my_unapproved_products, name='my_unapproved_products'),
    path('dashboard/vendor/my-product/create/', create_my_product, name='create_my_product'),
    path('dashboard/vendor/my-product/update/<int:id>/', update_my_product, name='update_my_product'),
    path('dashboard/admin/my-product/update/<int:id>/', update_my_product_admin, name='update_my_product_admin'),
    path('dashboard/vendor/my-order/', my_orders, name='my_orders'),
    path('dashboard/vendor/my-pending-order/', my_pending_orders, name='my_pending_orders'),
    path('dashboard/vendor/my-cancel-orders/', my_cancel_orders, name='my_cancel_orders'),
    path('dashboard/vendor/my-order/<int:id>/details/', my_orders_details, name='my_orders_details'),
    path('dashboard/vendor/update-profile/', update_vendor_profile, name='update_vendor_profile'),
    path('dashboard/vendor/change-password/', vendor_change_password_view, name='vendor_change_password_view'),
    path('dashboard/vendor/my_cancel_orders_details/<int:id>/', my_cancel_orders_details, name='my_cancel_orders_details'),
    path('dashboard/vendor/my_orders_is_complete/<int:id>/', my_orders_is_complete, name='my_orders_is_complete'),
    #superuser
    path('dashboard/admin/', admin_dashboard_home, name='admin_dashboard_home'),
    path('dashboard/admin/change-password/', admin_change_password_view, name='admin_change_password_view'),
    #products
    path('dashboard/admin/products/', product_list, name='product_list'),
    path('dashboard/admin/product-requests/', product_request, name='product_request'),
    path('dashboard/admin/declined-product-requests/', declined_product_request, name='declined_product_request'),
    path('dashboard/admin/hidden-products/', hidden_product_list, name='hidden_product_list'),
    path('dashboard/admin/all_product_list/datatable/data/', login_required(AllProductListJson.as_view()), name='all_product_list_dt'),
    path('dashboard/admin/product_option/<int:id>/', product_option, name='product_option'),
    path('dashboard/admin/product_rejected/<int:id>/', product_rejected, name='product_rejected'),
    path('dashboard/admin/product_commission_update/<int:id>/', product_commission_update, name='product_commission_update'),
    path('dashboard/admin/admin_orders/<int:id>/details/', orders_details, name='orders_details'),
    path('dashboard/admin/dashboard_shipping_price_create_or_update/', dashboard_shipping_price_create_or_update, name='dashboard_shipping_price_create_or_update'),

    #vendors
    path('dashboard/admin/vendors/', vendor_list, name='vendor_list'),
    path('dashboard/admin/vendor_details/<int:id>/', vendor_details, name='vendor_details'),

    path('dashboard/admin/deactivate-vendors/', deactivate_vendor_list, name='deactivate_vendor_list'),
    path('dashboard/admin/vendors/datatable/data/', login_required(VendorListJson.as_view()), name='vendor_list_dt'),
    #users
    path('dashboard/admin/customers/', user_list, name='user_list'),
    #data table
    path('dashboard/vendor/orders_list/datatable/data/', login_required(OrdersListJson.as_view()), name='orders_list_dt'),
    path('dashboard/vendor/product_list/datatable/data/', login_required(ProductListJson.as_view()), name='products_list_dt'),
    #superuser settings
    path('dashboard/admin/properties/', dashboard_properties, name='dashboard_properties'),
    path('dashboard/admin/properties_logo_create_update/', dashboard_properties_logo_create_update, name='dashboard_properties_logo_create_update'),
    path('dashboard/admin/shipping-method/', dashboard_shipping_method, name='dashboard_shipping_method'),
    path('dashboard/admin/shipping_method_create_update/', dashboard_free_shipping_create_or_update, name='dashboard_free_shipping_create_or_update'),
    path('dashboard/admin/glossary_zipcode_create_update/', dashboard_glossary_zipcode_create_or_update, name='dashboard_glossary_zipcode_create_or_update'),
    #slider
    path('dashboard/admin/sliders/', dashboard_slider, name='dashboard_slider'),
    path('dashboard/admin/sliders-create/', dashboard_slider_create, name='dashboard_slider_create'),
    path('dashboard/admin/sliders-update/<int:id>/', dashboard_slider_update, name='dashboard_slider_update'),
    path('dashboard/admin/sliders-delete/<int:id>/', dashboard_slider_delete, name='dashboard_slider_delete'),
    #coupons
    path('dashboard/admin/coupons/', coupons, name='coupons'),
    path('dashboard/admin/coupons_create/', coupons_create, name='coupons_create'),
    path('dashboard/admin/coupons_update/<int:id>/', coupons_update, name='coupons_update'),
    #order
    path('dashboard/admin/all-orders/', orders_list, name='orders_list'),
    path('dashboard/admin/pending-orders/', pending_orders_list, name='pending_orders_list'),
    path('dashboard/admin/cancel-orders/', cancel_orders_list, name='cancel_orders_list'),
    path('dashboard/admin/order_list/datatable/data/', login_required(OrderListJson.as_view()), name='order_list_dt'),
    #categorys
    path('dashboard/admin/categorys/', product_categorys, name='product_categorys'),
    path('dashboard/admin/category_create/', category_create, name='category_create'),
    path('dashboard/admin/category_update/<int:id>/', category_update, name='category_update'),
    path('dashboard/admin/subcategory_create/', subcategory_create, name='subcategory_create'),
    path('dashboard/admin/subcategory_update/<int:id>/', subcategory_update, name='subcategory_update'),
    path('dashboard/admin/product_category_create/', product_category_create, name='product_category_create'),
    path('dashboard/admin/product_category_update/<int:id>/', product_category_update, name='product_category_update'),
    
    #color and size
    path('dashboard/admin/product-colors-and-sizes/', product_colors_and_sizes, name='product_colors_and_sizes'),
    path('dashboard/admin/product_color_create/', product_color_create, name='product_color_create'),
    path('dashboard/admin/product_color_update/<int:id>/', product_color_update, name='product_color_update'),
    path('dashboard/admin/product_size_create/', product_size_create, name='product_size_create'),
    path('dashboard/admin/product_size_update/<int:id>/', product_size_update, name='product_size_update'),

    # vendor_active_deactive
    path('dashboard/admin/vendor_active_deactive/<int:id>/', vendor_active_deactive, name='vendor_active_deactive'),
    path('dashboard/admin/orders_mark_as_shipment/<int:id>/', orders_mark_as_shipment, name='orders_mark_as_shipment'),
    # pages
    path('dashboard/admin/mobile-apps-view/', mobile_apps_view, name='mobile_apps_view'),
    path('dashboard/admin/about-us-view/', about_us_view, name='about_us_view'),
    path('dashboard/admin/conract-us-view/', conract_us_view, name='conract_us_view'),
    path('dashboard/admin/faq-view/', faq_view, name='faq_view'),
    path('dashboard/admin/load_faq_view/<int:id>/', load_faq_view, name='load_faq_view'),
    path('dashboard/admin/update_faq_view/<int:id>/', update_faq_view, name='update_faq_view'),


    path('dashboard/admin/privacy-policy-view/', privacy_policy_view, name='privacy_policy_view'),
    path('dashboard/admin/terms-of-use-view/', terms_of_use_view, name='terms_of_use_view'),
    path('dashboard/admin/refund-return-policy-view/', refund_return_policy_view, name='refund_return_policy_view'),
   
    # vendor payment
    path('dashboard/vendor/due-payment/', deu_payment, name='deu_payment'),
    path('dashboard/vendor/send-payment-request/', send_payment_request, name='send_payment_request'),
    path('dashboard/vendor/payment-history/', payment_history, name='payment_history'),

    # vendor payment for admin
    path('dashboard/admin/vendor-due-payment/', vendor_deu_payment, name='vendor_deu_payment'),
    path('dashboard/admin/vendor-payment-history/', vendor_payment_history, name='vendor_payment_history'),
    path('dashboard/admin/cancel_orders_details/<int:id>/', cancel_orders_details, name='cancel_orders_details'),
    path('dashboard/admin/cancel_orders_accept/<int:id>/', cancel_orders_accept, name='cancel_orders_accept'),
    path('dashboard/admin/cancel_orders_regect/<int:id>/', cancel_orders_regect, name='cancel_orders_regect'),
    path('dashboard/admin/load_vendor_payment_request/<int:id>/', load_vendor_payment_request, name='load_vendor_payment_request'),
    path('dashboard/admin/pay_vendor_payment_request/<int:id>/', pay_vendor_payment_request, name='pay_vendor_payment_request'),
    path('dashboard/admin/load_payment_request/<int:id>/', load_payment_request, name='load_payment_request'),
    
    path('dashboard/admin/vendor_document_save/<int:id>/', vendor_document_save, name='vendor_document_save'),
    
    

]


