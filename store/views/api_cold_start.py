import numpy as np
import pandas as pd
import math

rating = pd.read_csv ('I:/project/scripts/1665_ds.204_Comment.csv', index_col=0)
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

# my_filter_cold_start = Q()
# for cold_start in cold_start_list:
#     my_filter_cold_start = my_filter_cold_start | Q(id=cold_start)

# context['recommended_products'] = Product.objects.filter(my_filter_cold_start)[:16]
# for product in context['recommended_products']:
#     product.favorited = product.id in favorited_products 
# return context