from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from store.models import Product

class QuickView(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['pk'])
        product.description = product.description[:300] + '...' if len(product.description) > 300 else product.description
        return render(request, 'components/modal_body/quick_view.html', {'product': product})
    
class QuickAddCart(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['pk'])

        return render(request, 'components/modal_body/quick_add_cart.html', {'product': product})