

from django.urls import path

from dashboard.views import UpdateUserView, OrderListView, UserListView, AdminDashboardView, ProductListView

urlpatterns = [
path('userlist',UserListView.as_view()),
    path('useredit/',UpdateUserView.as_view()),
    path('order/',OrderListView.as_view()),
    path('product/',ProductListView.as_view()),
    path('',AdminDashboardView.as_view()),
]