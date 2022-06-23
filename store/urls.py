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
    path('history/', order.OrderHistoryView.as_view(), name='order_history'),

    path('account/', account.AccountView.as_view(), name='account'),
    path('account/profile/<pk>/', account.UpdateProfileView.as_view(), name='profile'),
    path('account/change-password/', account.ChangePasswordView.as_view(), name='change_password'),
    path('store/<slug>/', store.StoreView.as_view(), name='store'),

    path('product/<pk>/like/', product.LikeProductView.as_view(), name='like'),
    path('favorite/', product.FavoriteProduct.as_view(), name='favorite_product'),

    path('me/store/', store.MyStoreView.as_view()),
    path('me/store/statistics/', store.StoreStatisticsView.as_view(), name='dashboard_store'),
    path('me/store/orders/', store.PendingOrderView.as_view()),
    path('me/store/create/', store.CreateStoreView.as_view()),
    path('me/store/edit/<pk>/', store.EditStoreView.as_view()),
    path('me/store/product/add/', store.AddProductView.as_view()),
    path('me/store/product/update/<pk>/', store.UpdateProductView.as_view()),
    path('me/store/product/remove/<pk>/', store.RemoveProduct.as_view()),
    path('me/store/product/sale/<pk>/', store.ProductSaleView.as_view()),

    path('me/cart/add/', order.AddCartView.as_view()),
    path('me/cart/remove/<pk>/', order.RemoveCartView.as_view()),
    path('me/cart/', order.CartView.as_view(), name='cart'),
    path('me/cart/purchase/', order.PurchaseView.as_view()),
    path('me/cart/purchase/payment/<pk>/', payment.PaymentMethodView.as_view()),
    path('me/cart/purchase/thank-you/', order.FinishPurchaseView.as_view()),

    path('me/notification/', notification.NotificationListView.as_view(), name='notification'),
    path('me/notification/get/', notification.GetNotificationView.as_view()),
    path('me/notification/read/<pk>/', notification.ReadNotificationView.as_view()),
    path('me/notification/read-all/', notification.ReadAllNotificationView.as_view()),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('currency/', utils.get_currency, name='currency'),
]