from django.contrib.auth import views as auth_views
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, TemplateView, UpdateView
from django.utils.translation import gettext_lazy as _
from ..models import Profile
from typing import *
from .utils import djdb_log, navbar_context
from . import utils
class LoginView(auth_views.LoginView):
    next_page = '/'

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Login')
        return context

class SignUpView(CreateView):
    template_name = 'registration/signup.html'
    form_class = UserCreationForm
    success_url = '/login/'

    def form_valid(self, form) -> HttpResponse:
        profile = Profile(user=form.save())
        profile.save()
        return super().form_valid(form)

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Sign Up')
        return context

class LogoutView(auth_views.LogoutView):
    next_page = '/login/'

class ChangePasswordView(auth_views.PasswordChangeView):
    success_url = '/login/'
    @navbar_context
    def get_context_data(self, **kwargs: Any):
        return super().get_context_data(**kwargs)

class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account.html'

    def post(self, request):
        if User.objects.filter(email=request.POST.get('email', '')).exists():
            return HttpResponseBadRequest(_('Email already in use'))
        try:
            email = request.POST.get('email')
            request.user.email = email
            request.user.save()
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseBadRequest()

    @djdb_log
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = _('Account')
        context['user'] = self.request.user
        context['profile'] = Profile.objects.get(user=self.request.user)
        return context

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['name', 'birthday',  'gender', 'phone', 'address', 'avatar']
    template_name = 'user/update_profile.html'
    success_url = '/account/'

    def get(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user != self.get_object().user:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)
    
    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)

class ResetPasswordView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

    @navbar_context
    def get_context_data(self, **kwargs: Any):
        return super().get_context_data(**kwargs)

class ResetPasswordDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

    @navbar_context
    def get_context_data(self, **kwargs: Any):
        return super().get_context_data(**kwargs)

class ConfirmPasswordResetView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = '/login/'

    @navbar_context
    def get_context_data(self, **kwargs: Any):
        return super().get_context_data(**kwargs)