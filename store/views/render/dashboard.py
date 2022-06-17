from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from store.models import Product

class SaleEdit(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['pk'])
        return render(request, 'components/modal_body/product_sale.html', {'product': product})