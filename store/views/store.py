from datetime import timedelta
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView, View
from typing import *
from django import http
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from store.views.utils import djdb_log, navbar_context
from ..models import OrderDetail, Product, Store, Order, Comment, ProductSale, ProductImage, ProductVideo, Category, LikedProduct
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from .notification import create_notification
from django.db.models import Count, Avg, Sum
from ..forms.store import StoreForm

class ProductQuantity(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        quantity = request.POST.get('quantity')
        if not product_id or not quantity:
            return HttpResponseBadRequest()
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return HttpResponseBadRequest()
        except ValueError:
            return HttpResponseBadRequest()
        try:
            product = Product.objects.get(id=product_id)
            product.quantity += quantity
            product.save()
        except Product.DoesNotExist:
            return HttpResponseNotFound()
        return HttpResponse()

class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'
    paginate_by = 16

    def get_queryset(self):
        search_data = self.request.GET.get('search', '')
        queryset = Product.objects.filter(store__slug=self.kwargs['slug'], name__icontains=search_data, available=True).order_by('-sold')

        if self.request.user.is_authenticated:
            favorited_products = LikedProduct.objects.filter(user = self.request.user).values_list('product__id', flat = True)
        else:
            favorited_products = []
        
        for product in queryset:
            if product.id in list(favorited_products):
                product.favorited = True
            else:
                product.favorited = False
            product.preview_description = product.description[:300] + '...' if len(product.description) > 300 else product.description
        return queryset

    @navbar_context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Store')
        context['store'] = Store.objects.get(slug=self.kwargs['slug'])
        return context

class UpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'my_store/add_product.html'
    fields = ('name', 'description', 'thumbnail', 'price', 'quantity', 'category', 'available', )
    success_url = '/me/store/products/'

    def form_valid(self, form):
        images = self.request.FILES.getlist('images', None)
        if images:
            for image in images:
                ProductImage.objects.create(product=self.object, image=image)
        removed_images = self.request.POST.getlist('removed_images', None)
        if removed_images:
            for image in removed_images:
                ProductImage.objects.get(id=image).delete()

        videos = self.request.FILES.getlist('videos', None)
        if videos:
            for video in videos:
                ProductVideo.objects.create(product=self.object, video=video)
        removed_videos = self.request.POST.getlist('removed_videos', None)
        if removed_videos:
            for video in removed_videos:
                ProductVideo.objects.get(id=video).delete()
        return super().form_valid(form)
    
    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Update product')
        context['category'] = Category.objects.all()
        context['is_update'] = True
        context['images'] = ProductImage.objects.filter(product=self.object)
        context['videos'] = ProductVideo.objects.filter(product=self.object)
        return context

class RemoveProduct(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = '/me/store/'

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)

class CreateStoreView(LoginRequiredMixin, CreateView):
    form_class = StoreForm
    template_name = 'my_store/create_store.html'
    success_url = '/me/store/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create Store')
        return context

class EditStoreView(LoginRequiredMixin, UpdateView):
    form_class = StoreForm
    template_name = 'my_store/edit_store.html'
    success_url = '/me/store/'

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any):
        store = Store.objects.get(id=self.kwargs['pk'])
        if store.owner != self.request.user:
            return HttpResponseRedirect('/me/store/')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)
    
    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Edit Store')
        return context

class HandleOrderView(LoginRequiredMixin, TemplateView):
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
        context['title'] = _('Pending Order')
        context['order'] = Order.objects.get(id=kwargs['pk'])
        context['handle'] = True
        return context

class PendingOrderView(LoginRequiredMixin, ListView):
    template_name = 'store_dashboard/pending_orders.html'
    model = Order
    paginate_by = 10

    def get_queryset(self):
        search_content = self.request.GET.get('search', '')
        return (Order.objects.filter(store=self.request.user.store, status='Pending', id__icontains=search_content) | \
                Order.objects.filter(store=self.request.user.store, status='Pending', user__username__icontains=search_content)).distinct() \
                .prefetch_related('orderdetail_set') \
                .select_related('user') \
                .order_by('-created_at')

    def post(self, request, **kwargs):
        data = request.POST
        order_id = data.get('id', None)
        result = data.get('result', None)
        if order_id and result:
            order = Order.objects.get(id=order_id)
            if order.status != 'Pending':
                return HttpResponseForbidden()
            if result == 'Accepted':
                create_notification(user=order.user, actor=order.store.name, action='Accept', target=order.id)
            elif result == 'Rejected':
                for order_detail in order.orderdetail_set.all():
                    product = order_detail.product
                    product.quantity += order_detail.quantity
                    product.save()
                create_notification(user=order.user, actor=order.store.name, action='Reject', target=order.id)
            order.status = result
            order.created_at = timezone.now()
            order.save()
        else:
            return HttpResponse(status=400)
        try:
            obj = {
                'next': reverse('handle_order', kwargs={'pk': Order.objects.get(store=self.request.user.store, status='Pending').id}),
            }
        except Order.DoesNotExist:
            obj = {
                'next': reverse('pending_order'),
            }
        return JsonResponse(obj)

    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Pending Orders')
        context['sname'] = 'pending'
        context['count'] = Order.objects.filter(store=self.request.user.store, status='Pending').count()
        return context

class ProductSaleView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        product = Product.objects.get(id=kwargs['pk'])
        try:
            sale = ProductSale.objects.get(product=product, expired_at__gte = timezone.now())
            return JsonResponse({'type': sale.sale_type, 'value': sale.value})
        except:
            return HttpResponseNotFound()
    
    def delete(self, request, **kwargs):
        product = Product.objects.get(id=kwargs['pk'])
        if product.store != request.user.store:
            return HttpResponseForbidden()
        ProductSale.objects.filter(product=product).delete()
        return HttpResponse(status=204)

    def post(self, request, **kwargs):
        data = request.POST
        product = Product.objects.get(id=self.kwargs['pk'])
        if product.store != self.request.user.store:
            return HttpResponse(status=400)
        sale_type = 'F' if data.get('type', None) == 'fixed' else 'P'
        sale_duration = data.get('duration', None)
        sale_value = data.get('value', None)
        if product and sale_type and sale_duration and sale_value:
            if not self.validate_sale(product, sale_type, int(sale_duration), int(sale_value)):
                return HttpResponseBadRequest()
            expired_at = timezone.now() + timezone.timedelta(days=int(sale_duration))
            ProductSale.objects.filter(product=product).delete()
            ProductSale.objects.create(product=product, sale_type=sale_type, expired_at=expired_at, value=sale_value)
            return HttpResponse("Sale created successfully", status=200)
        else:
            return HttpResponse(status=400)

    def validate_sale(self, product: Product, sale_type, sale_duration, sale_value):
        if sale_duration <= 0:
            return False
        if sale_type == 'F':
            if sale_value <= 0 or sale_value > product.price:
                return False
        if sale_type == 'P':
            if sale_value > 100 or sale_value <= 0:
                return False
        return True
