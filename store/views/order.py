from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.http import QueryDict

from store.views.utils import djdb_log, navbar_context
from ..models import Order, OrderDetail, Product, Notification
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, TemplateView, DeleteView, View, ListView
from django.utils.translation import gettext_lazy as _
from typing import *

class OrderDetailView(LoginRequiredMixin, View):
    def delete(self, request, *args: Any, **kwargs: Any):
        detail = OrderDetail.objects.get(id=kwargs['pk'])
        if detail.order.user != request.user:
            return HttpResponseBadRequest(_('You are not allowed to delete this item'))
        remain_detail = OrderDetail.objects.filter(order=detail.order).count() - 1
        if remain_detail == 0:
            detail.order.delete()
        else:
            detail.delete()        
        return HttpResponse(status=204)
    
    def patch(self, request, *args: Any, **kwargs: Any):
        detail = OrderDetail.objects.get(id=kwargs['pk'])
        if detail.order.user != request.user:
            return HttpResponseBadRequest(_('You are not allowed to update this item'))
        data = QueryDict(request.body)
        try:
            quantity = int(data['quantity'])
        except:
            return HttpResponseBadRequest(_('Quantity must be an integer'))
        if quantity < 0:
            return HttpResponseBadRequest(_('Quantity must be greater than 0'))
        if quantity == 0:
            return self.delete(request, *args, **kwargs)
        if quantity > detail.product.quantity:
            return HttpResponseBadRequest(_('Not enough product'))
        detail.quantity = quantity
        detail.save()
        return HttpResponse(status=204)

class CartView(TemplateView):
    template_name = 'cart_page.html'

    def post(self, request, *args: Any, **kwargs: Any):
        if not request.user.is_authenticated:
            return HttpResponseBadRequest(_('You must be logged in to add to cart'))
        data = request.POST.dict()
        try:
            quantity = int(data['quantity'])
        except:
            return HttpResponseBadRequest(_('Quantity must be an integer'))
        product = Product.objects.get(id=data['item_id'])
        if quantity > product.quantity:
            return HttpResponseBadRequest(_('Not enough product'))
        if quantity <= 0:
            return HttpResponseBadRequest(_('Quantity must be greater than 0'))
        order, created = Order.objects.get_or_create(user=request.user, store=product.store, status='Cart')
        order_detail = OrderDetail.objects.get_or_create(order=order, product=product)[0]
        order_detail.quantity += quantity
        order_detail.cost = order_detail.product.sell_price * order_detail.quantity
        order_detail.save()
        return JsonResponse({
            'created': created,
        })
    
    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Cart')
        context['orders'] = []
        for user_order in Order.objects.filter(user=self.request.user, status='Cart').select_related('store'):
            order = {
                'order': user_order,
                'order_details': OrderDetail.objects.filter(order=user_order).select_related('product'),
                'cost': user_order.cal_cost,
            }
            context['orders'].append(order)
        context['user'] = self.request.user
        return context

class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = 'order/history.html'
    model = Order
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        search_data = self.request.GET.get('search', '')
        queryset = self.model.objects.filter(user=user, id__icontains=search_data).exclude(status='Cart') \
            .prefetch_related('orderdetail_set', 'orderdetail_set__product').select_related('store', 'user') \
            .order_by('-id')
        return queryset
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Order History')
        return context

class OrderHistoryDetail(LoginRequiredMixin, TemplateView):
    template_name = 'history_detail.html'

    def dispatch(self, request, *args: Any, **kwargs: Any):
        order = Order.objects.get(id=kwargs['pk'])
        if order.user != request.user and order.store.owner != request.user:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)

    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Order History')
        context['order'] = Order.objects.get(id=kwargs['pk'])
        return context

class FinishPurchaseView(LoginRequiredMixin, TemplateView):
    template_name = 'thank_you.html'

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Thank you')
        return context