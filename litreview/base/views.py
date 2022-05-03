from itertools import chain

import base.forms as forms
import base.models as models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import CharField, Value, Q
from django.forms import modelform_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class Feed(LoginRequiredMixin, View):
    def get(self, request):
        all_tickets = models.Ticket.objects.all()
        all_tickets = all_tickets.annotate(
            content_type=Value("TICKET", CharField()))

        all_reviews = models.Review.objects.all()
        all_reviews = all_reviews.annotate(
            content_type=Value("REVIEW", CharField()))

        posts = chain(all_reviews, all_tickets)

        filtered_posts = self.filter_posts(request, posts)
        sorted_posts = sorted(list(filtered_posts),
                              key=lambda post: post.time_created,
                              reverse=True)

        ctx = {"posts": sorted_posts}
        return render(request, "base/feed.html", ctx)

    @staticmethod
    def filter_posts(request, posts):
        followed_users = models.UserFollows.objects.filter(user=request.user)
        followed_users = [x.followed_user for x in followed_users]
        filtered_posts = [post for post in posts if post.user in followed_users]
        return filtered_posts


class TicketCreation(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        ticket_form = forms.TicketForm()
        ctx = {"form": ticket_form}
        return render(request, "base/ticket_form.html", ctx)

    @staticmethod
    def post(request):
        data_for_ticket = forms.TicketForm(request.POST)
        ticket = data_for_ticket.save(commit=False)
        ticket.user = request.user
        ticket.save()
        return redirect(reverse_lazy("base:posts"))


class ReviewCreationDirect(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        ticket_creation = forms.TicketForm()
        review_form = forms.ReviewForm()
        ctx = {"ticket_form": ticket_creation,
               "review_form": review_form}
        return render(request, "base/review_direct_form.html", ctx)

    @staticmethod
    def post(request):
        data_for_ticket = forms.TicketForm(request.POST)
        ticket = data_for_ticket.save(commit=False)
        ticket.user = request.user
        ticket.save()

        data_for_review = forms.ReviewtForm()
        review = data_for_review.save(commit=False)
        review.ticket = ticket
        review.user = request.user
        review.save()

        return redirect(reverse_lazy("base:posts"))


@login_required(redirect_field_name=reverse_lazy("base:landing page"))
def review_create_response(request, ticket_pk):
    # I should find a more straightforward way of inserting data into
    # context. Now I am creating a one item list.
    # Two requirements for ticket_snippet - include it in a template
    # where data on multiple tickets is displayed and in a template
    # where there's only one ticket.

    ticket_list = [models.Ticket.objects.get(id=ticket_pk)]
    ticket = ticket_list[0]
    review_form = forms.ReviewForm()
    ctx = {"posts": ticket_list,
           "review_form": review_form}

    # Instead of a class-based view with two methods handling the two
    # request methods GET and POST, I am using the function-based view.
    # That's because I need the instance of ticket retrieved in the get
    # response. Indeed, the review attribute ticket will take that value.
    if request.method == "POST":
        data_for_review = forms.ReviewForm(request.POST)
        if data_for_review.is_valid():
            review = data_for_review.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            ticket.has_review = True
            return redirect(reverse_lazy("base:posts"))

    return render(request, "base/review_response_form.html", ctx)


class Posts(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        user = request.user
        tickets = models.Ticket.objects.all()
        tickets = tickets.annotate(
            content_type=Value("TICKET", CharField())
        )
        reviews = models.Review.objects.all()
        reviews = reviews.annotate(
            content_type=Value("REVIEW", CharField())
        )
        posts = list(filter(lambda x: x.user == user, chain(tickets, reviews)))
        sorted_posts = sorted(posts,
                              key=lambda post: post.time_created,
                              reverse=True)
        context = {"posts": sorted_posts}
        return render(request, "base/posts.html", context)


class EditTicket(LoginRequiredMixin, UpdateView):
    model = models.Ticket
    fields = ["title", "description"]
    success_url = reverse_lazy('base:posts')


class EditReview(LoginRequiredMixin, UpdateView):
    model = models.Review
    fields = "__all__"
    success_url = reverse_lazy('base:posts')


class DeleteTicket(LoginRequiredMixin, DeleteView):
    model = models.Ticket
    fields = "__all__"
    success_url = reverse_lazy('base:posts')


class DeleteReview(LoginRequiredMixin, DeleteView):
    model = models.Review
    fields = "__all__"
    success_url = reverse_lazy('base:posts')


class Following(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        user = request.user
        all_connections = models.UserFollows.objects.all()
        follower_followed = [(c.user, c.followed_user) for c in
                             all_connections]
        following = [c[1] for c in follower_followed if c[0] == user]
        followers = [c[0] for c in follower_followed if c[1] == user]
        ctx = {"following": following,
               "followers": followers,
               "user": user}
        return render(request, "base/following.html", ctx)


class Unfollow(LoginRequiredMixin, View):
    model = models.UserFollows
    template = "base/unfollow_user.html"
    success_url = reverse_lazy("base:following")

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        to_unfollow = models.UserFollows.objects.get(
            Q(user=request.user) & Q(followed_user=user)
        )
        ctx = {"username": user.username,
               "to_unfollow": to_unfollow.followed_user
               }
        return render(request, self.template, ctx)

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        to_unfollow = models.UserFollows.objects.get(
            Q(user=request.user) & Q(followed_user=user)
        )
        to_unfollow.delete()
        return redirect(self.success_url)


class Follow(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        username = request.GET.get("username")
        users = User.objects.filter(username__iexact=username)
        ctx = {"to_follow": users}
        return render(request, "base/follow_new_user.html", ctx)

    @staticmethod
    def post(request):
        id = request.POST.get("id")
        user_to_follow = User.objects.get(id=id)
        following = models.UserFollows(
            user=request.user, followed_user=user_to_follow
        )
        try:
            following.save()
        except IntegrityError:
            # If this wasn't a MVP, I could notify the
            # user he's trying to follow an already followed
            # user via a modal window.
            pass
        return redirect(reverse_lazy("base:following"))
