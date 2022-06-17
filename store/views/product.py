from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.views.generic import ListView, DetailView, View, TemplateView
from ..models import LikedProduct, Product, Category, OrderDetail, Order, Comment
from typing import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.utils import timezone
from .utils import navbar_context, djdb_log
class Home(TemplateView):
    template_name = 'home_page.html'

    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Home')
        context["categories"] = Category.objects.all()

        if self.request.user.is_authenticated:
            favorited_products = LikedProduct.objects.filter(user = self.request.user).values_list('product__id', flat = True)
        else:
            favorited_products = []

        r = OrderDetail.objects.filter(order__created_at__gt = timezone.now() - timezone.timedelta(7)) \
            .values('product') \
            .annotate(total_buy = Sum('quantity')) \
            .order_by('-total_buy')[:8]
        r_ids = [i['product'] for i in r]
        context['recommended_products'] = Product.objects.filter(id__in = r_ids, available=True).select_related('category').select_related('sale')[:8]
        context['most_viewed_products'] = Product.objects.filter(available=True).select_related('category').select_related('sale').order_by('-view')[:8]
        context['trending_products'] = (context['recommended_products'] | context['most_viewed_products']).select_related('category').select_related('sale').distinct()[:8]
        for product in context['recommended_products']:
            product.favorited = product.id in favorited_products
        for product in context['most_viewed_products']:
            product.favorited = product.id in favorited_products
        for product in context['trending_products']:
            product.favorited = product.id in favorited_products        
        return context

class ProductList(ListView):
    template_name = 'product_page.html'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True).order_by('id').select_related('category').select_related('sale')

        data = self.request.GET
        if 'category' in data:
            category_id = data['category']
            queryset = queryset.filter(category__id = category_id)
        if 'rating' in data:
            rating = data['rating']
            queryset = queryset.filter(rating__gte = rating)
        if 'price_from' in data:
            price_from = data['price_from']
            queryset = queryset.filter(price__gte = price_from)
        if 'price_to' in data:
            if data['price_to'] != 'max':
                price_to = data['price_to']
                queryset = queryset.filter(price__lte = price_to)
        if 'sort' in data:
            field = data['sort']
            if field == 'name':
                queryset = queryset.order_by('name')
            if field == '-name':
                queryset = queryset.order_by('-name')
            if field == 'price':
                queryset = queryset.order_by('price')
            if field == '-price':
                queryset = queryset.order_by('-price')
        if 'search' in data:
            search = data['search']
            queryset = queryset.filter(name__icontains = search)

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
        context['title'] = _('Products')
        context["categories"] = Category.objects.all()
        context['price_range'] = [(i, i + 200) for i in range(0, 1000, 200)]
        return context
class ProductDetail(ListView):
    model = Comment
    template_name = 'product_detail_page.html'
    paginate_by = 8

    def get(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(id=self.kwargs['pk'])
            if not product.available:
                raise Product.DoesNotExist
        except Product.DoesNotExist:
            return HttpResponseNotFound()
        
        product.view += 1
        product.save()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(product=self.kwargs['pk']) \
            .select_related('user') \
            .select_related('user__profile') \
            .order_by('-created_at')[:8]

    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(id=self.kwargs['pk'])
        context['title'] = product.name
        context['object'] = product
        context['comment_count'] = Comment.objects.filter(product=product).count()
        context['can_comment'] = self.can_comment()
        context['can_chat'] = self.request.user.is_authenticated and self.request.user != context['object'].store.owner 
        context['liked'] = self.request.user.is_authenticated and LikedProduct.objects.filter(user=self.request.user, product=product).exists()
        context['images'] = context['object'].productimage_set.all()
        context['videos'] = context['object'].productvideo_set.all()
        context['related_products'] = Product.objects.filter(category=product.category, available=True).exclude(id=product.id).select_related('category').select_related('sale')[:8]
        return context

    def can_comment(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        product = Product.objects.get(id=self.kwargs['pk'])
        # comment_count = Comment.objects.filter(user=user, product=product).count()
        # buy_count = OrderDetail.objects.filter(order__user=user, product=product, order__status='Accepted').count()
        # if buy_count <= comment_count:
        #     return False
        return True

class ProductView(View):
    def get(self, request, *args, **kwargs):
        search_pattern = request.GET.get('search')
        products = Product.objects.filter(available=True, name__icontains=search_pattern)[:5]
        res = []
        for product in products:
            res.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
            })
        return JsonResponse(res, safe=False)

class LikeProductView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            product_id = self.kwargs['pk']
            product = Product.objects.get(id=product_id)
            instance, created = LikedProduct.objects.get_or_create(user=request.user, product=product)
            return JsonResponse({
                'message': _('You liked this product'),
            })
        except Exception as e:
            return HttpResponseBadRequest(e)

    def delete(self, request, *args, **kwargs):
        try:
            product_id = self.kwargs['pk']
            product = Product.objects.get(id=product_id)
            LikedProduct.objects.filter(user=request.user, product=product).delete()
            return JsonResponse({
                'message': _('You unliked this product'),
            })
        except Exception as e:
            return HttpResponseBadRequest(e)

class FavoriteProduct(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'favorite_product.html'
    paginate_by = 10

    def get_queryset(self):
        search_content = self.request.GET.get('search', '')
        queryset = Product.objects.filter(likedproduct__user=self.request.user, name__icontains=search_content) \
                    .select_related('sale', 'category') \
                    .order_by('-id')
        for product in queryset:
            product.favorited = True
            product.preview_description = product.description[:300] + '...' if len(product.description) > 300 else product.description
        return queryset

    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Favorite Products')
        return context