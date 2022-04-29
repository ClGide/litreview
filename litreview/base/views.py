from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView
from django.db.models import CharField, Value
from itertools import chain

import base.models as models


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class Feed(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        all_tickets = models.Ticket.objects.all()
        all_tickets = all_tickets.annotate(content_type=Value("TICKET", CharField()))

        all_reviews = models.Review.objects.all()
        all_reviews = all_reviews.annotate(content_type=Value("REVIEW", CharField()))

        posts = chain(all_reviews, all_tickets)
        sorted_posts = sorted(posts,
                              key=lambda post: post.time_created,
                              reverse=True)
        ctx = {"feed": "well transmitted data from the view",
               "posts": sorted_posts}
        return render(request, "base/feed.html", ctx)


class TicketCreation(LoginRequiredMixin, generic.CreateView):
    model = models.Ticket
    fields = '__all__'
    success_url = reverse_lazy('base:feed')


class ReviewCreationDirect(LoginRequiredMixin, generic.CreateView):
    model = models.Review
    fields = '__all__'
    success_url = reverse_lazy('base:feed')


class ReviewCreationResponse(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        return render(request, "base/ticket_form.html")


class Posts(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        user = request.user
        tickets = models.Ticket.objects.all()
        tickets = tickets.annotate(
            content_type=Value("TICKET", CharField()))

        reviews = models.Review.objects.all()
        reviews = reviews.annotate(
            content_type=Value("REVIEW", CharField()))

        posts = list(filter(lambda x: x.user == user, chain(tickets, reviews)))
        sorted_posts = sorted(posts,
                              key=lambda post: post.time_created,
                              reverse=True)
        context = {"posts": sorted_posts}
        return render(request, "base/posts.html", context)


class EditTicket(LoginRequiredMixin, UpdateView):
    model = models.Ticket
    fields = "__all__"
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
        follower_followed = [(c.user, c.followed_user) for c in all_connections]
        following = [c[1] for c in follower_followed if c[0] == user]
        followers = [c[0] for c in follower_followed if c[1] == user]
        ctx = {"following": following,
               "followers": followers,
               "user": user}
        return render(request, "base/following.html", ctx)


