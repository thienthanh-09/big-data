from datetime import timedelta
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView, View
from typing import *
from django import http
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from psutil import users

from store.views.utils import navbar_context
from ..models import OrderDetail, Product, Store, Order, Comment, ProductSale, ProductImage, ProductVideo, Profile
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from .notification import create_notification
from django.db.models import Count, Avg, Sum
from ..forms.store import StoreForm
import math
from django.db.models import Q
import numpy as np 
import pandas as pd


class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'
    paginate_by = 16

    @navbar_context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Store')
        context['store'] = Store.objects.get(slug=self.kwargs['slug'])
        return context
class AddProductView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'my_store/add_product.html'
    fields = ('name', 'description', 'thumbnail', 'price', 'quantity', 'category', 'available', )
    success_url = '/me/store/'

    def form_valid(self, form):
        form.instance.store = self.request.user.store
        self.object = form.save()
        images = self.request.FILES.getlist('images', None)
        if images:
            for image in images:
                ProductImage.objects.create(product=self.object, image=image)
        videos = self.request.FILES.getlist('videos', None)
        if videos:
            for video in videos:
                ProductVideo.objects.create(product=self.object, video=video)
        return super().form_valid(form)

class UpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'my_store/add_product.html'
    fields = ('name', 'description', 'thumbnail', 'price', 'quantity', 'category', 'available', )
    success_url = '/me/store/'

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
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
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

class MyStoreView(LoginRequiredMixin, TemplateView):
    template_name = 'my_store/store.html'
    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        if not hasattr(self.request.user, 'store'):
            return redirect('/me/store/create/')
        return super().get(request, *args, **kwargs)
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['store'] = self.request.user.store
        context['products'] = Product.objects.filter(store=self.request.user.store) \
                                .filter(name__icontains=self.request.GET.get('search', '')) \
                                .order_by(self.request.GET.get('sort_by', 'id'))

        for query in self.request.GET:
            context['query_' + query] = self.request.GET.get(query, '')
            print(context['query_' + query])
        context['pending_count'] = Order.objects.filter(store=self.request.user.store, status='Pending').count()
        rating = pd.read_csv('I:\project\scripts/1665_ds.204_Comment.csv', index_col=0) 
        X_train = rating

        df = pd.pivot_table(
            X_train,
            index= 'product_id', 
            columns = 'user_id', 
            values = "rate").fillna(0)

            # Get rating function
        def get_rating_(productid, userid):
            return (X_train.loc[(X_train.user_id==userid) & (X_train.product_id==productid), 'rate'].iloc[0])

        get_rating_(1, 9)

        from numpy import sqrt
        # Calculate Pearson Correlation score
        def pearson_correlation_score(product1, product2):
            # user list which ratings both product1 and product2
            both_watch_count = []
            for element in X_train.loc[X_train.product_id == product1, 'user_id'].to_list():
                if element in X_train.loc[X_train.product_id == product2, 'user_id'].to_list():
                    both_watch_count.append(element)
            if len(both_watch_count) == 0:
                return 0
            rating_sum_1 = sum([get_rating_(product1, element) for element in both_watch_count])
            avg_rating_sum_1 = rating_sum_1/len(both_watch_count)
            rating_sum_2 = sum([get_rating_(product2, element) for element in both_watch_count])
            avg_rating_sum_2 = rating_sum_2/len(both_watch_count)
            numerator = sum([(get_rating_(product1, element) - avg_rating_sum_1) * (get_rating_(product2, element) - avg_rating_sum_2) for element in both_watch_count])
            denominator = sqrt(sum([pow((get_rating_(product1, element) - avg_rating_sum_1), 2) for element in both_watch_count])) * sqrt(sum([pow((get_rating_(product2, element) - avg_rating_sum_2), 2) for element in both_watch_count]))
            if (denominator == 0):
                return 0
            return numerator/denominator

        def similar_product_pearson_(product1, numproduct):
            productids = df.index.unique().tolist()
            similarity_score = [(pearson_correlation_score(product1, productID), productID)  for productID in productids if productID != product1]
            similarity_score.sort()
            similarity_score.reverse()
            return similarity_score[:numproduct]

        def get_userids_(productid):
            return X_train.loc[X_train.product_id == productid, 'user_id'].to_list()

        # Function to recommend users for product
        def recommend_user_pearson_(productid):
            total = {}
            similarity_sum = {}
            for pearson, product in similar_product_pearson_(productid,10): #k=10
                score = pearson
                for userid in get_userids_(product):
                    if userid not in get_userids_(productid) or get_rating_(productid, userid)==0:
                        if userid not in total:
                            total[userid] = 0
                            similarity_sum[userid] = 0
                            total[userid] += get_rating_(product,  userid)*score # tổng hợp đánh giá có trọng số - tử số
                            similarity_sum[userid] += abs(score) # tổng hợp đánh giá có trọng số - mẫu số
            ranking = [(to/similarity_sum[userid], userid) for userid, to in total.items()]
            ranking.sort()
            ranking.reverse()
            recommend = [(userid, score) for score, userid in ranking] 
            recommend = [check for check in recommend if not any(isinstance(n, float) and math.isnan(n) for n in check)]
            return recommend

        # product = Product.objects.get(id=self.kwargs['pk'])
        # product_input = product.id
        result = recommend_user_pearson_(18)
        item_based_list = [i[0] for i in result if i[1] >= 4]
        item_based_list = item_based_list[0:10]

        my_filter_item_based = Q()
        for item_based in item_based_list:
            my_filter_item_based = my_filter_item_based | Q(id=item_based)
        context['user_based_CF'] = Profile.objects.filter(gender='Female')[:50]   
        return context
    
class CreateStoreView(LoginRequiredMixin, CreateView):
    form_class = StoreForm
    template_name = 'my_store/create_store.html'
    success_url = '/me/store/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class EditStoreView(LoginRequiredMixin, UpdateView):
    form_class = StoreForm
    template_name = 'my_store/edit_store.html'
    success_url = '/me/store/'

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

class StoreStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'my_store/store_statistics.html'

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        self.selected_time = request.GET.get('time', 'year')
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if self.selected_time == 'year':
            self.time = now.replace(day=1, month=1)
        if self.selected_time == 'month':
            self.time = now.replace(day=1)
        if self.selected_time == 'week':
            self.time = now - timedelta(days=now.isocalendar()[2] - 1)
        if self.selected_time == 'day':
            self.time = now
        return super().get(request, *args, **kwargs)
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['store'] = self.request.user.store
        context['products_sell_most'] = OrderDetail.objects.select_related('order') \
                                        .filter(product__store=self.request.user.store, order__created_at__gte = self.time, order__status = 'Accepted') \
                                        .values('product__name') \
                                        .annotate(Sum('quantity')) \
                                        .order_by('-quantity__sum')[:5]

        context['products_total_sold'] = (OrderDetail.objects.select_related('order') \
                                        .filter(product__store=self.request.user.store, order__created_at__gte = self.time, order__status = 'Accepted') \
                                        .aggregate(total_sold = Sum('quantity'))['total_sold'] or 0) - \
                                        (context['products_sell_most'] \
                                        .aggregate(total_sold = Sum('quantity__sum'))['total_sold'] or 0)
        
        context['products_highest_rates'] = Comment.objects.filter(product__store=self.request.user.store, created_at__gte = self.time) \
                                            .values('product__name') \
                                            .annotate(avg_rate=Avg('rate')) \
                                            .order_by('-avg_rate')[:5]
        
        accepted_count = Order.objects.filter(store=self.request.user.store, status='Accepted').count()
        rejected_count = Order.objects.filter(store=self.request.user.store, status='Rejected').count()
        if accepted_count + rejected_count != 0:
            context['accepted_rates'] = accepted_count / (accepted_count + rejected_count) * 100
        else:
            context['accepted_rates'] = 0
        
        current_date = timezone.now()
        context['orders_in_week'] = Order.objects.filter(store=self.request.user.store, status='Accepted', created_at__gte=current_date - timezone.timedelta(days=7)) \
                                            .count()
        context['orders_in_month'] = Order.objects.filter(store=self.request.user.store, status='Accepted', created_at__gte=current_date - timezone.timedelta(days=30)) \
                                            .count()
        monthly_income = 0
        for order in Order.objects.filter(store=self.request.user.store, status='Accepted', created_at__gte=current_date - timezone.timedelta(days=30)):
            monthly_income += order.cost
        context['monthly_income'] = monthly_income
        context['time_range'] = [
            {
                'text': _('day'),
                'value': 'day',
            },
            {
                'text': _('week'),
                'value': 'week',
            },
            {
                'text': _('month'),
                'value': 'month',
            },
            {
                'text': _('year'),
                'value': 'year',
            }]
        context['selected_range'] = self.selected_time

        spot_length = 10
        context['products_sold_by_range'] = []
        for i in range(spot_length - 1, -1, -1):
            if self.selected_time == 'day':
                products_sold_by_range = OrderDetail.objects.select_related('order') \
                                        .filter(product__store=self.request.user.store, order__created_at__gte = self.time - timedelta(days=i), \
                                                order__created_at__lt = self.time - timedelta(days=i - 1), order__status = 'Accepted') \
                                        .values('product__name') \
                                        .annotate(total_sold = Sum('quantity'))
                item = {
                    'time': (self.time - timedelta(days=i)).strftime('%d/%m/%Y'),
                    'products': [
                        {
                            'name': product['product__name'],
                            'total_sold': product['total_sold']
                        } for product in products_sold_by_range
                    ]
                }
                context['products_sold_by_range'].append(item)
            if self.selected_time == 'week':
                products_sold_by_range = OrderDetail.objects.select_related('order') \
                                        .filter(product__store=self.request.user.store, order__created_at__gte = self.time - timedelta(days=i*7), \
                                                order__created_at__lt = self.time - timedelta(days=(i-1)*7), order__status = 'Accepted') \
                                        .values('product__name') \
                                        .annotate(total_sold = Sum('quantity'))
                item = {
                    'time': (self.time - timedelta(days=i*7)).strftime('%d/%m/%Y'),
                    'products': [
                        {
                            'name': product['product__name'],
                            'total_sold': product['total_sold']
                        } for product in products_sold_by_range
                    ]
                }
                context['products_sold_by_range'].append(item)
            if self.selected_time == 'month':
                def past_month(date, k):
                    if k < 0:
                        return timezone.now()
                    for _ in range(k):
                        date = (date - timedelta(days=1)).replace(day=1)
                    return date

                products_sold_by_range = OrderDetail.objects.select_related('order') \
                                        .filter(product__store=self.request.user.store, order__created_at__gte = past_month(self.time, i), \
                                                order__created_at__lt = past_month(self.time, i - 1), order__status = 'Accepted') \
                                        .values('product__name') \
                                        .annotate(total_sold = Sum('quantity'))
                item = {
                    'time': past_month(self.time, i).strftime('%m/%Y'),
                    'products': [
                        {
                            'name': product['product__name'],
                            'total_sold': product['total_sold']
                        } for product in products_sold_by_range
                    ]
                }
                context['products_sold_by_range'].append(item)
            if self.selected_time == 'year':
                def past_year(date, k):
                    if k < 0:
                        return timezone.now()
                    for _ in range(k):
                        date = (date - timedelta(days=1)).replace(day=1, month=1)
                    return date
                products_sold_by_range = OrderDetail.objects.select_related('order') \
                                        .filter(product__store=self.request.user.store, order__created_at__gte = past_year(self.time, i), \
                                                order__created_at__lt = past_year(self.time, i - 1), order__status = 'Accepted') \
                                        .values('product__name') \
                                        .annotate(total_sold = Sum('quantity'))
                item = {
                    'time': past_year(self.time, i).strftime('%Y'),
                    'products': [
                        {
                            'name': product['product__name'],
                            'total_sold': product['total_sold']
                        } for product in products_sold_by_range
                    ]
                }
                context['products_sold_by_range'].append(item)


        import json
        from django.core.serializers.json import DjangoJSONEncoder
        context['products_sold_by_range'] = json.dumps(context['products_sold_by_range'], cls=DjangoJSONEncoder)
        return context

class PendingOrderView(LoginRequiredMixin, ListView):
    template_name = 'my_store/pending_orders.html'
    model = Order
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(store=self.request.user.store, status='Pending').order_by('-created_at')

    def post(self, request, **kwargs):
        data = request.POST
        order_id = data.get('id', None)
        result = data.get('result', None)
        if order_id and result:
            order = Order.objects.get(id=order_id)
            if result == 'Accepted':
                for order_detail in order.orderdetail_set.all():
                    create_notification(order.user, 'Order Accepted', f'Your order (#{order.id}) has been accepted.')
            elif result == 'Rejected':
                for order_detail in order.orderdetail_set.all():
                    product = order_detail.product
                    product.quantity += order_detail.quantity
                    product.save()
                    create_notification(order.user, 'Order Rejected', f'Your order (#{order.id}) has been rejected.')
            order.status = result
            order.created_at = timezone.now()
            order.save()
        else:
            return HttpResponse(status=400)
        return HttpResponse(status=204)

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['count'] = Order.objects.filter(store=self.request.user.store, status='Pending').count()
        return context

class ProductSaleView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        product = Product.objects.get(id=kwargs['pk'])
        sale = ProductSale.objects.filter(product=product, expired_at__gte = timezone.now()).order_by('-created_at')
        if sale.count() == 0:
            return HttpResponseNotFound()
        return JsonResponse({'type': sale[0].sale_type, 'value': sale[0].value})
    
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
