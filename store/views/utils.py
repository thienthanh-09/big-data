from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from ..models import Order, Notification, Category
from django.utils.timezone import now
from pytz import all_timezones
import logging
def navbar_context(func):
    def inner(self, *args, **kwargs):
        context = func(self, *args, **kwargs)
        context['categories'] = Category.objects.all()
        context['timezones'] = all_timezones
        context['user'] = self.request.user
        if not self.request.user.is_anonymous:
            context['cart_size'] = Order.objects.filter(user=self.request.user, status='Cart').count()
            context['noti_size'] = Notification.objects.filter(user=self.request.user, status='Unread').count()
            context['noti'] = context['noti_size'] > 0

            # last access check point
            self.request.user.profile.last_access = now()
            self.request.user.profile.save()
        return context
    return inner

def djdb_log(func):
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logging.error(e)
            return None
    return inner

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

def set_timezone(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            request.user.profile.timezone = request.POST['timezone']
            request.user.profile.save()
        else:
            request.session['django_timezone'] = request.POST['timezone']
        return redirect(request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else '/')

import requests
import os
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def get_currency(request):
    if request.method == 'GET':
        api_key = os.environ.get('CURRENCY_API_KEY')
        url = 'https://free.currconv.com/api/v7/convert?q=USD_VND&compact=ultra&apiKey=' + api_key
        response = requests.get(url)
        res = response.content.decode()
        return JsonResponse(res, safe=False)