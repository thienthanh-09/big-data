from asyncore import read
import csv
import re
import pandas
import os
from pytz import timezone
from store.models import Product, ProductImage, Comment, Category, Store, Profile
from django.contrib.auth.models import User

# def run():
#     file = open('scripts\89_ds.204_Product.csv')
#     read_file=csv.reader(file)

#     Product.objects.all().delete()

#     count=1

#     for record in read_file:
#         if count==1:
#             pass
#         else:
#             print(record)
#             Product.objects.create(id=record[0], name=record[1],description=record[2], thumbnail=record[3], price=record[4], quantity=record[5], sold=record[6], available=record[7], rating=record[8], rating_count=record[9], view=record[10], slug=record[11], category_id=record[12], store_id=record[13])
#         count=count+1

# def run():
#     file = open('scripts/100_ds.204_ProductImage.csv')
#     read_file=csv.reader(file)

#     ProductImage.objects.all().delete()

#     count=1

#     for record in read_file:
#         if count==1:
#             pass
#         else:
#             print(record)
#             ProductImage.objects.create(id=record[0], image=record[1], product_id=record[2])
#         count=count+1

# def run():
#     file = open('scripts/424_ds.204_user.csv')
#     read_file=csv.reader(file)

#     User.objects.all().delete()

#     count=1

#     for record in read_file:
#         if count==1:
#             pass
#         else:
#             print(record)
#             User.objects.create(id=record[0], password=record[1], is_superuser=record[3], username=record[4], first_name=record[5], last_name=record[6], email=record[7], is_staff=record[8], is_active=record[9])
#         count=count+1

def run():
    file = open('scripts/1665_ds.204_Comment.csv', encoding="utf8")
    read_file=csv.reader(file)

    Comment.objects.all().delete()

    count=1

    for record in read_file:
        if count==1:
            pass
        else:
            print(record)
            Comment.objects.create(id=record[0], content=record[1], rate=record[2], product_id=record[4], user_id=record[5])
        count=count+1

# def run():
#     file = open('scripts/424_ds.204_Profile.csv', encoding="utf8")
#     read_file=csv.reader(file)

#     Profile.objects.all().delete()

#     count=1

#     for record in read_file:
#         if count==1:
#             pass
#         else:
#             print(record)
#             Profile.objects.create(id=record[0], name=record[1], gender=record[3], phone=record[4], address=record[5], avatar=record[6], timezone=record[7], user_id=record[8])
#         count=count+1

# def run():
#     file = open('scripts/21_ds.204_Category.csv')
#     read_file=csv.reader(file)

#     Category.objects.all().delete()

#     count=1

#     for record in read_file:
#         if count==1:
#             pass
#         else:
#             print(record)
#             Category.objects.create(id=record[0], name=record[1])
#         count=count+1

# def run():
#     file = open('scripts/11_ds.204_Store.csv', encoding="utf8")
#     read_file=csv.reader(file)

#     Store.objects.all().delete()

#     count=1

#     for record in read_file:
#         if count==1:
#             pass
#         else:
#             print(record)
#             Store.objects.create(id=record[0], name=record[1], description=record[2], phone=record[3], address=record[4], slug=record[5], owner_id=record[6])
#         count=count+1