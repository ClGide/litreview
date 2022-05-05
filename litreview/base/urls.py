from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

app_name = 'base'
urlpatterns = [
    path('',
         auth_views.LoginView.as_view(
             redirect_authenticated_user=True,
             success_url=reverse_lazy("base:feed")
         ),
         name='landing page'),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("accounts/profile/", views.Feed.as_view(), name="feed"),

    path("create_ticket/",
         views.TicketCreation.as_view(),
         name="ticket_creation"),

    path("create_review_direct/",
         views.ReviewCreationDirect.as_view(),
         name="review_creation_direct"),

    path("<int:ticket_pk>/create_review_response/",
         views.review_create_response,
         name="review_create_response"),

    path("posts/",
         views.Posts.as_view(),
         name="posts"),
    path("posts/<int:pk>/edit_ticket/",
         views.EditTicket.as_view(),
         name="ticket_update"),
    path("posts/<int:review_pk>/<int:ticket_pk>/edit_review/",
         views.edit_review,
         name="review_update"),
    path("posts/<int:pk>/delete_ticket/",
         views.DeleteTicket.as_view(),
         name="ticket_delete"),
    path("posts/<int:pk>/delete_review/",
         views.DeleteReview.as_view(),
         name="review_delete"),

    path("following/",
         views.Following.as_view(),
         name="following"),
    path("following/<int:pk>/unfollow/",
         views.Unfollow.as_view(),
         name="unfollow"),
    path("following/follow/",
         views.Follow.as_view(),
         name="search_result"),
]

