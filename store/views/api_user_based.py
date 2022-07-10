import math
import pandas as pd
import numpy as np

# Load data
rating = pd.read_csv('N:\GoldenOwl\FinalAssigment/source-ds204/scripts/1665_ds.204_Comment.csv', index_col=0)

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

result = recommend_product_pearson_(18)
user_based_list = [i[0] for i in result if i[1] >= 4]
print(user_based_list)


        # user_ = users.objects.get(id=self.kwargs['pk'])
        # user_input = user_.id

        # result = recommend_product_pearson_(user_input)
        # user_based_list = [i[0] for i in result if i[1] >= 4]

        # my_filter_user_based = Q()
        # for user_based in user_based_list:
        #     my_filter_user_based = my_filter_user_based | Q(id=user_based)

        # user = self.request.user

        # if not user.is_authenticated:
            
        #     for product in context['recommended_products']:
        #         product.favorited = product.id in favorited_products 
        # else:
        #     context['recommended_products'] = Product.objects.filter(my_filter_user_based)[:16]
        #     for product in context['recommended_products']:
        #         product.favorited = product.id in favorited_products 