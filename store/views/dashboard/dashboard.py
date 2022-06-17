from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from typing import *
from django import http
from django.shortcuts import redirect
from store.views.utils import navbar_context
from store.models import Product, Order, OrderDetail, Comment, ProductImage, ProductVideo, Category
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.timezone import timedelta
from django.db.models import Count, Avg, Sum

class StoreDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'store_dashboard/general.html'
    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        if not hasattr(self.request.user, 'store'):
            return redirect('/store/')
        return super().get(request, *args, **kwargs)
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['sname'] = 'store'    
        context['title'] = _('Store Dashboard')
        context['store'] = self.request.user.store
        # context['products'] = Product.objects.filter(store=self.request.user.store) \
        #                         .filter(name__icontains=self.request.GET.get('search', '')) \
        #                         .select_related('sale', 'category') \
        #                         .order_by(self.request.GET.get('sort_by', 'id'))

        # for query in self.request.GET:
        #     context['query_' + query] = self.request.GET.get(query, '')
        #     print(context['query_' + query])
        # context['pending_count'] = Order.objects.filter(store=self.request.user.store, status='Pending').count()
        return context

class DashboardAddProduct(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'my_store/add_product.html'
    fields = ('name', 'description', 'thumbnail', 'price', 'quantity', 'category', 'available', )
    success_url = '/me/store/products/'

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

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Add Product')
        context['sname'] = 'add_product'
        context['category'] = Category.objects.all()
        return context

class DashboardProducts(LoginRequiredMixin, ListView):
    template_name = 'store_dashboard/product_list.html'
    paginate_by = 10

    def get_queryset(self):
        search_content = self.request.GET.get('search', '')
        return (Product.objects.filter(store=self.request.user.store, id__icontains=search_content) | \
                Product.objects.filter(store=self.request.user.store, name__icontains=search_content)).distinct() \
                .select_related('sale', 'category') \
                .order_by('id')

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['sname'] = 'products'
        context['title'] = _('Product List')
        return context

class DashboardHistory(LoginRequiredMixin, ListView):
    template_name = 'store_dashboard/history.html'
    paginate_by = 10

    def get_queryset(self):
        search_content = self.request.GET.get('search', '')
        return (Order.objects.filter(store=self.request.user.store, id__icontains=search_content) | \
                Order.objects.filter(store=self.request.user.store, user__username__icontains=search_content)).distinct() \
                .exclude(status='Cart') \
                .prefetch_related('orderdetail_set') \
                .select_related('user') \
                .order_by('-created_at')
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Store History')
        context['sname'] = 'history'
        return context

class DashboardStatistic(LoginRequiredMixin, TemplateView):
    template_name = 'store_dashboard/statistic.html'
    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        if not hasattr(self.request.user, 'store'):
            return redirect('/store/')
        return super().get(request, *args, **kwargs)
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['sname'] = 'statistic'
        self.selected_time = self.request.GET.get('time', 'year')
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if self.selected_time == 'year':
            self.time = now.replace(day=1, month=1)
        if self.selected_time == 'month':
            self.time = now.replace(day=1)
        if self.selected_time == 'week':
            self.time = now - timedelta(days=now.isocalendar()[2] - 1)
        if self.selected_time == 'day':
            self.time = now
        context['title'] = _('Store Statistics')
        context['store'] = self.request.user.store
        context['products_sell_most'] = OrderDetail.objects.select_related('order') \
                                        .filter(product__store=self.request.user.store, order__created_at__gte = self.time, order__status = 'Accepted') \
                                        .values('product__name') \
                                        .annotate(Sum('quantity')) \
                                        .order_by('-quantity__sum')
        
        context['products_highest_rates'] = Comment.objects.filter(product__store=self.request.user.store, created_at__gte = self.time) \
                                            .values('product__name') \
                                            .annotate(avg_rate=Avg('rate')) \
                                            .order_by('-avg_rate')
        
        accepted_count = Order.objects.filter(store=self.request.user.store, status='Accepted').count()
        rejected_count = Order.objects.filter(store=self.request.user.store, status='Rejected').count()
        if accepted_count + rejected_count != 0:
            context['accepted_rates'] = accepted_count / (accepted_count + rejected_count) * 100
        else:
            context['accepted_rates'] = 0
        
        current_date = timezone.now()
        context['orders_in_week'] = Order.objects.filter(store=self.request.user.store, created_at__gte=current_date - timezone.timedelta(days=7)) \
                                    .exclude(status='Cart') \
                                    .count()
        context['orders_in_month'] = Order.objects.filter(store=self.request.user.store, created_at__gte=current_date - timezone.timedelta(days=30)) \
                                    .exclude(status='Cart') \
                                    .count()
        monthly_income = 0
        for order in Order.objects.filter(store=self.request.user.store, status='Accepted', created_at__gte=current_date - timezone.timedelta(days=30)):
            monthly_income += order.cal_cost
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

        # The code below use to prepare the data for the chart
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