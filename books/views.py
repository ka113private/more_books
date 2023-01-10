from django.shortcuts import render
from django.views import generic

# Creattee your views here.
class IndexView(generic.TemplateView):
    template_name = "index.html"