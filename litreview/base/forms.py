import base.models as models
from django.forms import ModelForm


class TicketForm(ModelForm):
    # I am not subclassing CreateView and UpdateView
    # because they do no let me give default value. Sure, I can
    # give a default value in models.py. But I cannot access
    # request.user in models.py.
    class Meta:
        model = models.Ticket
        fields = ["title", "description"]


class ReviewForm(ModelForm):
    class Meta:
        model = models.Review
        fields = ["headline", "rating", "body"]
