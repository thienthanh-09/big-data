from typing import *
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import *

from store.views.utils import navbar_context

class PaymentMethodView(LoginRequiredMixin, TemplateView):
    template_name = 'payment/payment.html'

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        try: 
            context['order'] = self.request.user.order_set.get(pk=self.kwargs['pk'])
        except:
            raise Http404('Order not found')

        if context['order'].status != 'Cart':
            raise Http404('Invalid order')

        
        return context