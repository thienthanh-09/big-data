from pyspark.sql import SparkSession
from pyspark.sql import functions as f

import pandas as pd
from IPython.core.display import display
import seaborn as sns

spark = SparkSession.builder.config("spark.executor.memory", "4g").getOrCreate()

from pyspark.ml.feature import (StopWordsRemover, Tokenizer, HashingTF, IDF, CountVectorizer, StringIndexer, NGram, VectorAssembler, ChiSqSelector)
from pyspark.ml.classification  import LogisticRegression, DecisionTreeClassifier, RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
import time

tokenizer = Tokenizer(inputCol="description", outputCol="words1")
stopword_remover = StopWordsRemover(
    inputCol="words1",
    outputCol= "words2",
    stopWords= StopWordsRemover.loadDefaultStopWords("english")
)
hashing_tf = HashingTF(inputCol="words2", outputCol="term_frequency")
idf= IDF(inputCol="term_frequency", outputCol="features", minDocFreq=5)
lr = LogisticRegression(labelCol="label", featuresCol="features", regParam=0.2)
pipe =  Pipeline(
    stages=[tokenizer, stopword_remover, hashing_tf, idf, lr]
)

ratingdemo_schema = "id int, subject string, review string, label float, status string, item_id int, user_id int, created_at string, updated_at string"
ratingdemo = spark.read.csv('/content/drive/MyDrive/Recommender System on E-commerce platform/BigData/data/Rating_Demo.csv', schema=ratingdemo_schema, header=True).select('item_id', 'user_id', 'label')
print(ratingdemo.count())
ratingdemo.show()

productdemo_schema = "id int, name string, description string, thumbnail string, price float, quantity int, sold  int, available boolean, rating int, rating_count int, view int, slug string, category_id int, store_id int"
productdemo = spark.read.csv('/content/drive/MyDrive/Recommender System on E-commerce platform/BigData/data/Product_Demo.csv', schema=productdemo_schema, header=True).select('id', 'description')
print(productdemo.count())
productdemo.show()

combinedemo = ratingdemo.join(productdemo, ratingdemo.item_id == productdemo.id, "inner").select('item_id', 'user_id', 'label', 'description')
print(combinedemo.count())
combinedemo.printSchema()

user_regex = r"(@\w{1,15})"
hashtag_replace_regex = "#(\w{1,})"
url_regex = r"((https?|ftp|file):\/{2,3})+([-\w+&@#/%=~|$?!:,.]*)|(www.)+([-\w+&@#/%=~|$?!:,.]*)"
email_regex = r"[\w.-]+@[\w.-]+\.[a-zA-Z]{1,}"
number_regex = "[^a-zA-Z0-9]"
space_regex = " +"

df = (combinedemo.withColumn("description",f.regexp_replace(f.col("description"), user_regex, ""))
                    .withColumn("description",f.regexp_replace(f.col("description"), hashtag_replace_regex, ""))
                    .withColumn("description",f.regexp_replace(f.col("description"), url_regex, ""))
                    .withColumn("description",f.regexp_replace(f.col("description"), email_regex, ""))
                    .withColumn("description",f.regexp_replace(f.col("description"), number_regex, " "))
                    .withColumn("description",f.regexp_replace(f.col("description"), space_regex, " "))
                    .withColumn("description",f.trim(f.col("description")))
                    .withColumn("description",f.lower(f.col("description")))
                    .filter("description != ''")
)
print('Rows:', df.count())
df.show()

model = pipe.fit(df)

product_list = df.select('item_id', 'description').distinct().sort('item_id')
print(product_list.count())
product_list.show()

def recommend_product(customer):
    rated_product = df.filter(df.user_id == customer).select('item_id').rdd.flatMap(lambda x: x).collect()
    not_rated = product_list.filter(~product_list.item_id.isin(rated_product)).withColumn('user_id', f.lit(customer))

    get_recommend = model.transform(not_rated).select('user_id', 'item_id', 'prediction')
    get_recommend1 = get_recommend.sort(get_recommend.prediction.desc())
    
    return get_recommend1

recommend_product(20).show()

# get list product cho em Thanh mặp
def get_product_list(customer, num_of_product):
    return recommend_product(customer).select('item_id').limit(num_of_product).rdd.flatMap(lambda x: x).collect()

get_product_list(20,10)