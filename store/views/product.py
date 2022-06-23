from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.views.generic import ListView, DetailView, View, TemplateView
from psutil import users
from sqlalchemy import true
from ..models import LikedProduct, Product, Category, OrderDetail, Order, Comment
from typing import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.utils import timezone
from .utils import navbar_context, djdb_log
from django.db.models import Q
import numpy as np
import pandas as pd
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from numpy import sqrt

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
        # context['most_viewed_products'] = Product.objects.filter(available=True).select_related('category').select_related('sale').order_by('-view')[:8]

        rating = pd.read_csv('I:\project\scripts/1665_ds.204_Comment.csv', index_col=0)

        rating_grouped = rating.groupby('product_id').agg({'rate': 'sum'}).reset_index()
        rating_grouped.rename(columns = {'rate': 'Total_score'},inplace=True)
        most_rating = rating_grouped.sort_values(['Total_score', 'product_id'], ascending = [0,1]) 
        most_rating['Rank'] = most_rating['Total_score'].rank(ascending=0, method='first') 
                
        def recommend_popular_product(user_id):     
            user_recommendations = most_rating 
            user_recommendations['UserId'] = user_id 
            cols = user_recommendations.columns.tolist() 
            cols = cols[-1:] + cols[:1] 
            user_recommendations = user_recommendations[cols] 
            return user_recommendations[:50]

        cold_start = recommend_popular_product(1)
        cold_start_list = cold_start.iloc[:,1].values.tolist()
        # print(cold_start_list)

        cold_start = recommend_popular_product(1)
        cold_start_list = cold_start.iloc[:,1].values.tolist()
        cold_start_list = cold_start_list[0:10]

        X_train = rating
        # Pivot table 
        df = pd.pivot_table(
            X_train,
            index = 'user_id', 
            columns = 'product_id', 
            values = "rate").fillna(0)

        # Get rating function
        def get_rating_(userid, productid):
            return (X_train.loc[(X_train.user_id == userid) & (X_train.product_id == productid), 'rate'].iloc[0])

        from numpy import sqrt
        # Function to calculate Pearson Correlation score
        def pearson_correlation_score(user1, user2):
            # product list which is rated by both user1 and user2
            both_watch_count = []
            for element in X_train.loc[X_train.user_id == user1, 'product_id'].to_list():
                if element in X_train.loc[X_train.user_id == user2, 'product_id'].to_list():
                    both_watch_count.append(element)
            if len(both_watch_count) == 0:
                return 0
            rating_sum_1 = sum([get_rating_(user1, element) for element in both_watch_count])
            avg_rating_sum_1 = rating_sum_1/len(both_watch_count)
            rating_sum_2 = sum([get_rating_(user2, element) for element in both_watch_count])
            avg_rating_sum_2 = rating_sum_2/len(both_watch_count)
            numerator = sum([(get_rating_(user1, element) - avg_rating_sum_1) * (get_rating_(user2, element) - avg_rating_sum_2) for element in both_watch_count])
            denominator = sqrt(sum([pow((get_rating_(user1, element) - avg_rating_sum_1), 2) for element in both_watch_count])) * sqrt(sum([pow((get_rating_(user2, element) - avg_rating_sum_2), 2) for element in both_watch_count]))
            if denominator == 0:
                return 0
            return numerator/denominator

        def similar_user_pearson_(user1, numuser):
            userids = X_train.user_id.unique().tolist()
            similarity_score = [(pearson_correlation_score(user1, userID), userID) for userID in userids if userID != user1]
            similarity_score.sort()
            similarity_score.reverse()
            return similarity_score[:numuser]

        def get_productids_(userid):
            return X_train.loc[(X_train.user_id == userid), 'product_id'].to_list()

        # Function to recommend products for user
        def recommend_product_pearson_(userid):
            total = {}
            similarity_sum = {} 
            for pearson, user in similar_user_pearson_(userid,10): #k=10
                score = pearson
                for productid in get_productids_(user):
                    if productid not in get_productids_(userid) or get_rating_(userid, productid) == 0:
                        if productid not in total:
                            total[productid] = 0
                            similarity_sum[productid] = 0
                        total[productid] += get_rating_(user, productid) * score  # tổng hợp đánh giá có trọng số - tử số 
                        similarity_sum[productid] += abs(score) # tổng hợp đánh giá có trọng số - mẫu số
            ranking = [(to/similarity_sum[productid], productid) for productid, to in total.items()]
            ranking.sort()
            ranking.reverse()
            recommend = [(productid, score) for score, productid in ranking]
            recommend = [check for check in recommend if not any(isinstance(n, float) and math.isnan(n) for n in check)]
            return recommend

        my_filter_cold_start = Q()
        for cold_start in cold_start_list:
            my_filter_cold_start = my_filter_cold_start | Q(id=cold_start)

        user_ = self.request.user
        user_input = user_.id
        
        result = recommend_product_pearson_(user_input)
        user_based_list = [i[0] for i in result if i[1] >= 4]
        user_based_list = user_based_list[0:29]

        my_filter_user_based = Q()
        for user_based in user_based_list:
            my_filter_user_based = my_filter_user_based | Q(id=user_based)

        user = self.request.user
        if not user.is_authenticated:
            context['recommended_products'] = Product.objects.filter(my_filter_cold_start)[:16]
            for product in context['recommended_products']:
                product.favorited = product.id in favorited_products 
            return context
        else:
            context['recommended_products'] = Product.objects.filter(my_filter_user_based)[:15]            
            for product in context['recommended_products']:
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
        # context['related_products'] = Product.objects.filter(content_based=product.content_based, available=True).exclude(id=product.id)[:8]
        product_data = pd.read_csv('I:\project\scripts\89_ds.204_Product.csv')

        # Function to process data
        def pre_processing(text):
            text = text.lower() # lowercase
            text = re.sub('<.*?>', '', text) # Remove html tag,...
            text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
            text = text.split(' ')
            stops = set(stopwords.words('english'))
            text = [w for w in text if not w in stops]
            text = ' '.join(text)
            return text

        product_data["description"] = product_data["description"].astype(str)

        for i in range(len(product_data)):
            product_data["description"].iloc[i] =  pre_processing(product_data["description"].iloc[i])

        product_data = product_data.dropna()

        # Calculate TF/IDF
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_vectorizer = vectorizer.fit(product_data["description"])
        overview_matrix = tfidf_vectorizer.transform(product_data["description"])

        # Calculate similarity matrix
        similarity_matrix = linear_kernel(overview_matrix, overview_matrix)

        def get_asin(productid):
            return product_data['asin'].iloc[productid]

        def recommend_product_based_on_description(product_input):
            # Calculate similarity score
            similarity_score = list(enumerate(similarity_matrix[product_input]))
            similarity_score = sorted(similarity_score, key = lambda x: x[1], reverse = True)
            similarity_score = similarity_score[1:]
            recommendations = [(productid, score) for productid, score in similarity_score]
            return recommendations

        product = Product.objects.get(id=self.kwargs['pk'])
        input = product.id

        result = recommend_product_based_on_description(input)
        content_based_list = [i[0] for i in result if i[1] > 0]

        my_filter_content_based = Q()
        for content_based in content_based_list:
            my_filter_content_based = my_filter_content_based | Q(id=content_based)
        context['related_products'] = Product.objects.filter(my_filter_content_based)[:12]
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

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render, get_object_or_404
class LikeProductView(LoginRequiredMixin, View):
    def add(self, request, *args, **kwargs):
        product = Product.objects.get(id=self.kwargs['pk'])
        product_input = product.id
        user_ = self.request.user
        user_input = user_.id
        instance, created = LikedProduct.objects.get_or_create(user=user_input, product=product_input)
        return JsonResponse({'message': _('You liked this product'),})

    def delete(self, request, *args, **kwargs):
        product_id = self.kwargs['pk']
        product = Product.objects.get(id=product_id)
        LikedProduct.objects.filter(user=request.user, product=product).delete()
        return JsonResponse({'message': _('You unliked this product'),})

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
