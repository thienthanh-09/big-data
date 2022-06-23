from .notification import create_notification
from ..models import Comment, Product
from django.views.generic import CreateView
from typing import *

class CommentView(CreateView):
    model = Comment
    fields = ['content', 'rate']
    template_name = 'example/blank.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = Product.objects.get(id=self.kwargs['pk'])
        rate = (form.instance.product.rating * form.instance.product.rating_count + form.instance.rate) / (form.instance.product.rating_count + 1)
        form.instance.product.rating = rate
        form.instance.product.rating_count += 1
        form.instance.product.save()
        create_notification(form.instance.product.store.owner, '(Store) New comment on your product', self.request.user.username + ' commented on your product ' + form.instance.product.name)
        return super().form_valid(form)