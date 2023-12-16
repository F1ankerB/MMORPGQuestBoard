"""
URL configuration for QuestBoard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from board.views import NewsList,NewsDetail,ManageCommentsView,CreatePostView,DeletePostView,CommentCreateView, CommentDeleteView
from board import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('news/', NewsList.as_view(), name='news_list'),
    path('news/<int:pk>/', NewsDetail.as_view(), name='news_detail'),
    path('news/manage-comments/', ManageCommentsView.as_view(), name='manage_comments'),
    path('create-post/', CreatePostView.as_view(), name='create_post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete_post'),
    path('news/<int:post_pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('comment/<int:comment_pk>/delete/', CommentDeleteView.as_view(), name='delete_comment'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('verify/<int:user_id>/', views.verify, name='verify'),
    path('email-broadcast/', views.email_broadcast, name='email_broadcast'),
    path('pages/', include('django.contrib.flatpages.urls')),

]
