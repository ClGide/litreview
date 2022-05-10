"""Classes and functions managing requests and returning response objects."""


from itertools import chain

import base.forms as forms
import base.models as models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import CharField, Value, Q, QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView


class SignUpView(generic.CreateView):
    """Makes a form allowing the user to """
    form_class = UserCreationForm
    success_url: str = reverse_lazy("login")
    template_name = "registration/signup.html"


class Feed(LoginRequiredMixin, View):
    def get(self, request) -> HttpResponse:
        """retrieves the feed's content and sorts it."""
        all_tickets: QuerySet = models.Ticket.objects.all()
        all_tickets = all_tickets.annotate(
            content_type=Value("TICKET", CharField())
        )

        all_reviews: QuerySet = models.Review.objects.all()
        all_reviews = all_reviews.annotate(
            content_type=Value("REVIEW", CharField())
        )

        posts: chain[QuerySet] = chain(all_reviews, all_tickets)
        filtered_posts = self.filter_posts(request, posts)

        user_posts = self.user_own_posts(request)
        tickets = self.tickets_responding_to_user_tickets(request)
        filtered_posts.extend(user_posts)
        filtered_posts.extend(tickets)
        sorted_posts = sorted(list(filtered_posts),
                              key=lambda post: post.time_created,
                              reverse=True)

        context = {"posts": sorted_posts}
        return render(request, "base/feed.html", context)

    @staticmethod
    def filter_posts(request, posts) -> list[models.Ticket | models.Review]:
        followed_users = models.UserFollows.objects.filter(user=request.user)
        followed_users = [x.followed_user for x in followed_users]
        filtered_posts = [post for post in posts if
                          post.user in followed_users]
        return filtered_posts

    @staticmethod
    def user_own_posts(request):
        user_tickets = models.Ticket.objects.filter(user=request.user)
        user_tickets = user_tickets.annotate(
            content_type=Value("TICKET", CharField())
        )

        user_reviews = models.Review.objects.filter(user=request.user)
        user_reviews = user_reviews.annotate(
            content_type=Value("REVIEW", CharField())
        )

        user_posts = list(chain(list(user_tickets), list(user_reviews)))
        return user_posts

    @staticmethod
    def tickets_responding_to_user_tickets(request):
        tickets = models.Review.objects.filter(ticket__user=request.user)
        tickets = tickets.annotate(
            content_type=Value("REVIEW", CharField())
        )
        return list(tickets)


class TicketCreation(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        ticket_form = forms.TicketForm()
        context = {"form": ticket_form}
        return render(request, "base/ticket_form.html", context)

    @staticmethod
    def post(request):
        data_for_ticket = forms.TicketForm(request.POST)
        ticket = data_for_ticket.save(commit=False)
        ticket.user = request.user
        ticket.save()
        return redirect(reverse_lazy("base:feed"))


class ReviewCreationDirect(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        ticket_form = forms.TicketForm()
        review_form = forms.ReviewForm()
        context = {"ticket_form": ticket_form,
                   "review_form": review_form}
        return render(request, "base/review_direct_form.html", context)

    @staticmethod
    def post(request):
        data_for_ticket = forms.TicketForm(request.POST)
        ticket = data_for_ticket.save(commit=False)
        ticket.user = request.user
        ticket.save()

        data_for_review = forms.ReviewForm(request.POST)
        review = data_for_review.save(commit=False)
        review.ticket = ticket
        review.user = request.user
        review.save()

        return redirect(reverse_lazy("base:feed"))


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
    context = {"posts": ticket_list,
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
            ticket.save()
            return redirect(reverse_lazy("base:feed"))

    return render(request, "base/review_response_form.html", context)


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


@login_required(redirect_field_name=reverse_lazy("base:landing page"))
def edit_review(request, review_pk, ticket_pk):
    review_instance = models.Review.objects.get(id=review_pk)
    ticket = models.Ticket.objects.get(id=ticket_pk)
    ticket_list = [ticket]
    review_form = forms.ReviewForm(instance=review_instance)
    context = {"posts": ticket_list,
               "review_form": review_form}

    if request.method == "POST":
        review_form = forms.ReviewForm(request.POST, instance=review_instance)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect(reverse_lazy("base:posts"))

    return render(request, "base/review_form.html", context)


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
        context = {"following": following,
                   "followers": followers,
                   "user": user}
        return render(request, "base/following.html", context)


class Unfollow(LoginRequiredMixin, View):
    model = models.UserFollows
    template = "base/unfollow_user.html"
    success_url = reverse_lazy("base:following")

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        to_unfollow = models.UserFollows.objects.get(
            Q(user=request.user) & Q(followed_user=user)
        )
        context = {"username": user.username,
                   "to_unfollow": to_unfollow.followed_user}
        return render(request, self.template, context)

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
        context = {"to_follow": users}
        return render(request, "base/follow_new_user.html", context)

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
