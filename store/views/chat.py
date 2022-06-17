from urllib.robotparser import RobotFileParser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.generic import TemplateView, View
from django.utils.timezone import now

from store.views.utils import navbar_context
from ..models import Chat, Message, Store
class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat.html'

    @navbar_context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chat'
        context['role'] = self.request.GET.get('role', 'user')
        context['search'] = self.request.GET.get('search', '')
        try:
            Store.objects.get(owner=self.request.user)
            context['has_store'] = True
        except:
            context['has_store'] = False
        if context['role'] == 'user':
            context['chat_stores'] = Chat.objects.filter(user=self.request.user, store__name__icontains = context['search']) \
                                    .select_related('store').order_by('-last_modified')
        else:
            context['chat_users'] = Chat.objects.filter(store=self.request.user.store, user__username__icontains = context['search']) \
                                    .select_related('user').order_by('-last_modified')
        return context

class ChatMessage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data = request.GET
        id = data.get('id')
        role = data.get('role', 'user')

        if role == 'user':
            chat = Chat.objects.get(user=request.user, store__id=id)
        else:
            chat = Chat.objects.get(store=request.user.store, user__id=id)
        
        messages = Message.objects.filter(chat=chat).order_by('-id')[:20]
        res = []
        for message in reversed(messages):
            res.append({
                'role': 'user' if message.is_user else 'store',
                'image': message.image.url if message.image else None,
            })

        return JsonResponse(res, safe=False)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        role = request.POST.get('role', 'user')
        id = request.POST.get('id')
        image = request.FILES.get('image')
        
        if role == 'user':
            chat = Chat.objects.get(user=user, store__id=id)
        else:
            chat = Chat.objects.get(store=user.store, user__id=id)
        
        message = Message.objects.create(
            chat=chat,
            is_user=role == 'user',
            image=image,
        )
        message.save()
        return JsonResponse({'id': message.id}, safe=False)

class StartChat(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseBadRequest()
        store_id = request.POST.get('store_id')
        store = Store.objects.get(id=store_id)
        chat, _ = Chat.objects.get_or_create(user=user, store=store)
        if not _:
            chat.last_modified = now()
            chat.save()
        return HttpResponse(status=204)