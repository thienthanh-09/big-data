import math
import numpy as np 
import pandas as pd

rating = pd.read_csv ('I:\project\scripts/1665_ds.204_Comment.csv')

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

result = recommend_user_pearson_(6)
item_based_list = [i[0] for i in result if i[1] >= 4]
print(item_based_list)