from re import L
import pandas as pd

product_data = pd.read_csv('scripts\mock_content_based.csv')

# product = Product.objects.get(id=self.kwargs['pk'])

input = 12

content_based_list =product_data.list_product[input-1]
content_based_list = content_based_list.strip('[]')
content_based_list = content_based_list.split(', ')
