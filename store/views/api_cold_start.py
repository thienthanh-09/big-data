import pyspark
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
import pyspark.sql.types as t
from pyspark.ml import Pipeline
spark = SparkSession.builder.getOrCreate()

ratingdemo_schema = "id int, subject string, review string, label float, status string, item_id int, user_id int, created_at string, updated_at string"
ratingdemo = spark.read.csv('scripts/1665_ds.204_Comment.csv', schema=ratingdemo_schema, header=True).select('item_id', 'user_id', 'label')

avg_groupdemo = ratingdemo.groupby('item_id').agg(f.mean('label').alias('avg_score'))
total_groupdemo = ratingdemo.groupby('item_id').agg(f.sum('label').alias('total_score')).withColumnRenamed('item_id', 'temp')

groupdemo = avg_groupdemo.join(total_groupdemo, total_groupdemo.temp == avg_groupdemo.item_id, "inner").select('item_id', 'avg_score', 'total_score')

from pyspark.sql.functions import *
rankeddemo =  groupdemo.orderBy(desc("avg_score"), desc("total_score"))

list_popular = rankeddemo.select('item_id').limit(20).rdd.flatMap(lambda x: x).collect()
print(list_popular)
