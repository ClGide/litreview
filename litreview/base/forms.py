""" Forms allowing end-users to create and edit Ticket and Review instances.

Django built-in ModelForm enables easy HTML form creation. Each instance of its
subclasses it's a form. The forms are based on the model field of the inside
Meta Class.
"""


from django.forms import ModelForm, CheckboxSelectMultiple
from django.forms import ChoiceField, CheckboxInput, IntegerField, Select, SelectMultiple

import base.models as models


class TicketForm(ModelForm):
    """Allows creating or editing instances of the Ticket model.

    Tne user field isn't included because it is automatically filled
    in View.py. The reason is that the title and description fields
    are filled by the end-user whereas the user field is always the
    user attribute of the request.
    """

    class Meta:
        model = models.Ticket
        fields = ["title", "description"]


class ReviewForm(ModelForm):
    """Allows creating or editing instances of the Review model.

    Tne user field isn't included because it is automatically filled
    in View.py. The reason is that the headlines, rating and body fields
    are filled by the end-user whereas the user field is always the
    user attribute of the request.
    """

    rating = IntegerField(max_value=5)

    class Meta:
        model = models.Review
        fields = ["headline", "rating", "body"]
