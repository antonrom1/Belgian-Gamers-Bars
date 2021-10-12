from django.shortcuts import render
from django.views import generic
from bars.models import Bar, Event


def index(request):
    context = {
        "gaming_bars": Bar.objects.order_by("-name")[:5],
        "events": Event.objects.filter(),
    }
    return render(request, "bars/index.html", context)


class BarDetail(generic.DetailView):
    template_name = "bars/bar-detail.html"
    model = Bar


class AboutView(generic.TemplateView):
    template_name = "bars/index.html"

    def get_queryset(self):
        return Bar.objects.order_by("-name")[:5]
