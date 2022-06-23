from concurrent.futures import thread
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from project.celery import send_email_task


from store.views.utils import navbar_context
from ..models import Order, OrderDetail, Product, Notification
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, TemplateView, DeleteView, View, ListView
from django.utils.translation import gettext_lazy as _
from typing import *
from .notification import create_notification

class AddCartView(CreateView):
    model = OrderDetail
    fields = '__all__'

    def post(self, request, *args: Any, **kwargs: Any):
        if not request.user.is_authenticated:
            return HttpResponseBadRequest(_('You must be logged in to add to cart'))

        data = request.POST.dict()
        quantity = int(data['quantity'])
        product = Product.objects.get(id=data['item_id'])
        if quantity > product.quantity:
            return HttpResponseBadRequest(_('Not enough product'))
        else:
            product.quantity -= quantity
            product.save()
        order, created = Order.objects.get_or_create(user=request.user, store=product.store, status='Cart')
        order_detail = OrderDetail.objects.get_or_create(order=order, product=product)[0]
        order_detail.quantity += quantity
        order_detail.cost = order_detail.product.sell_price * order_detail.quantity
        order_detail.save()
        return JsonResponse({
            'remain': product.quantity,
            'created': created,
        })

class RemoveCartView(LoginRequiredMixin, DeleteView):
    model = OrderDetail
    success_url = '/me/cart/'

    def delete(self, request, *args: Any, **kwargs: Any):
        order_detail = OrderDetail.objects.get(id=kwargs['pk'])
        product = order_detail.product
        product.quantity += order_detail.quantity
        product.save()
        remain_order_detail = OrderDetail.objects.filter(order=order_detail.order).count() - 1
        if remain_order_detail == 0:
            Order.objects.get(id=order_detail.order.id).delete()
        else:
            order_detail.delete()
        return HttpResponse(status=204)


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'order/cart.html'

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['orders'] = []
        for user_order in Order.objects.filter(user=self.request.user, status='Cart'):
            order = {
                'order': user_order,
                'order_details': OrderDetail.objects.filter(order=user_order),
                'cost': user_order.cost,
            }
            context['orders'].append(order)
        context['user'] = self.request.user
        return context

class PurchaseView(LoginRequiredMixin, View):
    def post(self, request):
        data = request.POST.dict()
        cart = Order.objects.get(id=data['id'])

        if OrderDetail.objects.filter(order=cart).count() == 0:
            return HttpResponseBadRequest()
        try:
            cart.purchase()
            owner = cart.store.owner
            create_notification(owner, '(Store) New Order', f'You have a new order (#{cart.id})')
            if owner.email:
                print('Sending email...')
                send_email_task.delay(
                    'New Order',
                    f'You have a new order (#{cart.id})',
                    from_email=settings.EMAIL_HOST_USER,
                    to_email=[owner.email],
                )
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseBadRequest()

class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = 'order/history.html'
    model = Order
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.filter(user=user).exclude(status='Cart').order_by('-id')
        return queryset
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)

class FinishPurchaseView(LoginRequiredMixin, TemplateView):
    template_name = 'order/thank_you.html'