from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView
from news.models import Notification


class NotificationView(DetailView):
    model = Notification