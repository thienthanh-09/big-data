from typing import *
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import *
from ..models import Order, OrderDetail
from .notification import create_notification
from django.conf import settings
from project.celery import send_email_task
from store.views.utils import djdb_log, navbar_context
from django.utils.translation import gettext_lazy as _
class Checkout(LoginRequiredMixin, TemplateView):
    template_name = 'checkout.html'

    def post(self, request, *args: Any, **kwargs: Any):
        data = request.POST
        order = Order.objects.get(pk=self.kwargs['pk'])
        address = data.get('address', '')

        if OrderDetail.objects.filter(order=order).count() == 0:
            return HttpResponseBadRequest()
        try:
            res = order.purchase(address)
            if not res:
                return HttpResponseBadRequest("Product out of stock")
            owner = order.store.owner
            create_notification(user=owner, actor=request.user.username, action='Order', target=order.id)
            if owner.email:
                print('Sending email...')
                send_email_task.delay(
                    'New Order',
                    f'You have a new order (#{order.id})',
                    from_email=settings.EMAIL_HOST_USER,
                    to_email=[owner.email],
                )
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseBadRequest()

    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        try:
            context['order'] = Order.objects.get(pk=self.kwargs['pk'])
        except:
            return HttpResponseBadRequest(_('Order not found'))
        
        if context['order'].user != self.request.user:
            return HttpResponseBadRequest(_('You are not allowed to view this order'))

        if context['order'].status != 'Cart':
            return HttpResponseBadRequest(_('This order is not in cart'))
        
        context['title'] = _('Checkout')        
        return context