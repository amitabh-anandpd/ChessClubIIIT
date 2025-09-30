from django.shortcuts import render, get_object_or_404
from .models import Newsletter

def newsletter_list(request):
    newsletters = Newsletter.objects.all()
    return render(request, 'newsletters.html', {
        "newsletters": newsletters
    })

def newsletter_article(request, slug):
    newsletter = get_object_or_404(Newsletter, slug=slug)
    return render(request, 'newsletter-article.html', {
        "newsletter": newsletter
    })
