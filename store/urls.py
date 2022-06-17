from django.urls import path
from django.views.i18n import JavaScriptCatalog
from store.views import account, product, store, order, comment, payment, notification, chat, utils
from .views.dashboard import dashboard
from .views.render import product as render_product, dashboard as render_dashboard
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', product.Home.as_view(), name='index'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('set_time_zone/', utils.set_timezone, name='set_timezone'),
    path('login/', account.LoginView.as_view(), name='login'),
    path('signup/', account.SignUpView.as_view(), name='signup'),
    path('logout/', account.LogoutView.as_view(), name='logout'),
    path('reset/', account.ResetPasswordView.as_view(), name='reset'),
    path('reset/done/', account.ResetPasswordDoneView.as_view(), name='password_reset_done'),
    path('reset/confirm/<uidb64>/<token>/', account.ConfirmPasswordResetView.as_view(), name="password_reset_confirm"),

    path('chat/', chat.ChatView.as_view()),
    path('chat/start/', chat.StartChat.as_view()),
    path('chat/message/', chat.ChatMessage.as_view()),

    path('products/', product.ProductList.as_view(), name='products'),
    path('product/<pk>/<slug>/', product.ProductDetail.as_view(), name='product_detail'),
    path('product/', product.ProductView.as_view()),
    path('comment/<pk>/', comment.CommentView.as_view()),
    path('like/<pk>/', product.LikeProductView.as_view()),
    path('history/', order.OrderHistoryView.as_view(), name='order_history'),
    path('history/<pk>/', order.OrderHistoryDetail.as_view(), name='order_history_detail'),

    path('account/', account.AccountView.as_view(), name='account'),
    path('account/profile/<pk>/', account.UpdateProfileView.as_view(), name='profile'),
    path('account/change-password/', account.ChangePasswordView.as_view(), name='change_password'),
    path('store/<slug>/', store.StoreView.as_view(), name='store'),

    path('favorite/', product.FavoriteProduct.as_view(), name='favorite_product'),

    path('me/store/', dashboard.StoreDashboard.as_view(), name='dashboard_store'),
    path('me/store/statistic/', dashboard.DashboardStatistic.as_view(), name='dashboard_statistic'),
    path('me/store/history/', dashboard.DashboardHistory.as_view(), name='dashboard_history'),
    path('me/store/products/', dashboard.DashboardProducts.as_view(), name='dashboard_products'),
    path('me/store/orders/', store.PendingOrderView.as_view(), name='pending_order'),
    path('me/store/order/<pk>/', store.HandleOrderView.as_view(), name='handle_order'),
    path('store/', store.CreateStoreView.as_view()),
    path('me/store/edit/<pk>/', store.EditStoreView.as_view(), name='edit_store'),
    path('me/store/product/add/', dashboard.DashboardAddProduct.as_view(), name='add_product'),
    path('me/store/product/update/<pk>/', store.UpdateProductView.as_view(), name='update_product'),
    path('me/store/product/remove/<pk>/', store.RemoveProduct.as_view()),
    path('me/store/product/sale/<pk>/', store.ProductSaleView.as_view()),
    path('me/store/product/quantity/<pk>/', store.ProductQuantity.as_view(), name='product_quantity'),

    path('cart/detail/<pk>/', order.OrderDetailView.as_view()),
    path('cart/', order.CartView.as_view(), name='cart'),
    path('checkout/<pk>/', payment.Checkout.as_view(), name='checkout'),
    path('thank-you/', order.FinishPurchaseView.as_view(), name='thank_you'),

    path('notification/', notification.NotificationListView.as_view(), name='notification'),
    path('notification/get/', notification.GetNotificationView.as_view()),
    path('notification/read/<pk>/', notification.ReadNotificationView.as_view()),
    path('notification/read-all/', notification.ReadAllNotificationView.as_view()),

    path('currency/', utils.get_currency, name='currency'),

    path('render/quickview/<pk>/', render_product.QuickView.as_view(), name='render_quickview'),
    path('render/quickadd/<pk>/', render_product.QuickAddCart.as_view(), name='render_quickadd'),
    path('render/sale/<pk>/', render_dashboard.SaleEdit.as_view(), name='render_sale'),
]