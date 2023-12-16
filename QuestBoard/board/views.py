from .models import Post,Comment,UserProfile
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView,DeleteView,TemplateView
)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse

class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.order_by('-created_at')

class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news_detail'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.get_object())
        return context


class ManageCommentsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'manage_comments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(author__user=self.request.user)
        post_id = self.request.GET.get('post_id')

        if post_id:
            comments = Comment.objects.filter(post_id=post_id)
        else:
            comments = Comment.objects.filter(post__in=posts)

        context['posts'] = posts
        context['comments'] = comments
        return context

    def post(self, request, *args, **kwargs):
        comment_id = request.POST.get('comment_id')
        action = request.POST.get('action')

        if comment_id and action:
            comment = get_object_or_404(Comment, id=comment_id)
            posts = Post.objects.filter(author__user=request.user)

            # Проверка, что комментарий принадлежит одному из постов пользователя
            if comment.post in posts:
                print(f"До: Comment ID: {comment.id}, Approved: {comment.approved}")

                if action == 'approve':
                    comment.approved = True
                elif action == 'reject':
                    comment.approved = False

                comment.save()

        return redirect('manage_comments')

    def test_func(self):
        return self.request.user.is_authenticated
from django.views.generic.edit import CreateView
from .forms import PostForm
from django.urls import reverse_lazy
class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'
    success_url = reverse_lazy('news_list')
    def form_valid(self, form):
        form.instance.author = UserProfile.objects.get(user=self.request.user)
        return super().form_valid(form)

from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('news_list')  # Убедитесь, что у вас есть URL с именем 'index'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user.userprofile  # Сравнение с UserProfile пользователя

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user.userprofile)


from .forms import CommentForm

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment_form.html'  # Указывает на шаблон для создания комментария

    def form_valid(self, form):
        form.instance.user = self.request.user.userprofile  # Установка автора комментария
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_pk'])  # Установка связанного поста
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news_detail', kwargs={'pk': self.kwargs['post_pk']})  # Вернуться на страницу поста

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'  # Указывает на шаблон для подтверждения удаления комментария
    pk_url_kwarg = 'comment_pk'
    success_url = reverse_lazy('news_list')
    def test_func(self):
        comment = self.get_object()
        return comment.user == self.request.user.userprofile  # Только автор комментария может удалить его

    def get_success_url(self):
        post_pk = self.get_object().post.pk
        return reverse_lazy('news_detail', kwargs={'pk': post_pk})
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.models import User
from .models import EmailNotification
from django.core.mail import send_mail

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user, created = User.objects.get_or_create(username=email, email=email)
            if created:
                # Сохраняем профиль пользователя
                user_profile = UserProfile.objects.create(user=user)
                user_profile.save()
                # Отправляем письмо с кодом
                notification = EmailNotification.objects.create(user=user_profile)
                send_mail(
                    'Код подтверждения',
                    f'Ваш код: {notification.message}',
                    'te4kkaunt@yandex.ru',
                    [email],
                    fail_silently=False,
                )
                return redirect('verify', user_id=user.id) # Переход на страницу верификации
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                # Отправляем письмо с кодом
                notification = EmailNotification.objects.create(user=user.userprofile)
                send_mail(
                    'Код подтверждения',
                    f'Ваш код: {notification.message}',
                    'te4kkaunt@yandex.ru',
                    [email],
                    fail_silently=False,
                )
                return redirect('verify', user_id=user.id) # Переход на страницу верификации
            except User.DoesNotExist:
                form.add_error('email', 'Пользователь с таким email не найден')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login
from .models import User, EmailNotification

def verify(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            notification = EmailNotification.objects.get(user=user.userprofile, message=code)
            if timezone.now() - notification.sent_at < timedelta(minutes=10):  # Срок действия кода - 10 минут
                # Успешная верификация
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # Указываем backend
                login(request, user)  # Авторизуем пользователя
                return redirect('news_list')  # Перенаправляем на главную страницу
            else:
                # Код истек
                return render(request, 'verify.html', {'error': 'Срок действия кода истек'})
        except EmailNotification.DoesNotExist:
            # Неверный код
            return render(request, 'verify.html', {'error': 'Неверный код'})
    else:
        return render(request, 'verify.html')
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from .forms import EmailForm
from .utils import send_bulk_email

@user_passes_test(lambda u: u.is_superuser)
def email_broadcast(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            send_bulk_email(subject, message)
            return redirect('news_list')  # Перенаправление на страницу успеха
    else:
        form = EmailForm()

    return render(request, 'email_broadcast.html', {'form': form})