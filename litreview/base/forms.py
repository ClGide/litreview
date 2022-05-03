from django.forms import Form, ModelForm, CharField, IntegerField
from django.core.validators import MinValueValidator, MaxLengthValidator, MaxValueValidator
import base.models as models


class ReviewDirectForm(Form):
    # I am not subclassing CreateView and UpdateView
    # because they do no let me give default value. Sure, I can
    # give a default value in models.py. But I cannot access
    # request.user in models.py.

    ticket_title = CharField(
        validators=[MaxLengthValidator(128)],
    )
    ticket_description = CharField(
        validators=[MaxLengthValidator(2048)],
        required=False
    )

    review_rating = IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_headline = CharField(
        validators=[MaxLengthValidator(128)]
    )
    review_body = CharField(
        validators=[MaxLengthValidator(8192)],
        required=False
    )


class ReviewResponseForm(ModelForm):
    class Meta:
        model = models.Review
        fields = ["rating", "headline", "body"]
