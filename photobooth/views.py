from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.contrib.auth import logout
from .forms import RegistrationForm
from .models import *
from .forms import RequestForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
import asyncio
from telegram import Bot
from telegram.request import HTTPXRequest
from django.urls import reverse_lazy
from .models import Review, Request
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test
from .forms import GalleryImageForm
from django.views.decorators.http import require_POST

TELEGRAM_TOKEN = '7657287697:AAGPEfe0cosV0LD5loz-2IOALxc0UcG1o_c'
TELEGRAM_CHAT_ID = '755335572'

class HomeView(TemplateView):
    template_name = 'photobooth/home.html'

class AboutView(TemplateView):
    template_name = 'photobooth/about.html'

class ProcessView(TemplateView):
    template_name = 'photobooth/process.html'

class ContactsView(TemplateView):
    template_name = 'photobooth/contacts.html'

class RegisterView(CreateView):
    template_name = 'photobooth/register.html'
    form_class = UserCreationForm



@user_passes_test(lambda u: u.is_superuser)
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('review_list')

@method_decorator(login_required, name='dispatch')
class GalleryView(TemplateView):
    template_name = 'photobooth/gallery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = GalleryImage.objects.order_by('-uploaded_at')
        if self.request.user.is_superuser:
            context['gallery_form'] = GalleryImageForm()
        return context

@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def upload_image(request):
    form = GalleryImageForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
    else:
        print("Форма с ошибками:", form.errors)
    return redirect('gallery')

@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)
    image.delete()
    return redirect('gallery')

def contacts_view(request):
    # Получаем контактную информацию
    contact_info = ContactInfo.objects.first()  # Или используйте .get(), если уверены, что записи есть
    return render(request, 'photobooth/contacts.html', {'contact_info': contact_info})

@staff_member_required
def edit_contacts(request):
    contact_info = ContactInfo.objects.first()  # Получаем первые данные, или можно выбрать через filter()

    if request.method == 'POST':
        # Обновляем информацию
        contact_info.phone = request.POST.get('phone')
        contact_info.email = request.POST.get('email')
        contact_info.address = request.POST.get('address')
        contact_info.save()

        messages.success(request, 'Контактные данные успешно обновлены!')
        return redirect('contacts')

    return render(request, 'photobooth/contacts.html', {'contact_info': contact_info})

class HomeView(TemplateView):
    template_name = 'photobooth/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pricing_packages = PricingPackage.objects.all()

        for package in pricing_packages:
            if package.features:
                package.features_list = package.features.split(',')
            else:
                package.features_list = []

        context['pricing_packages'] = pricing_packages
        return context


@user_passes_test(lambda u: u.is_superuser)
def change_status(request, pk):
    # Получаем заявку
    request_obj = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        # Обновляем статус
        new_status = request.POST.get('status')
        if new_status:
            request_obj.status = new_status
            request_obj.save()

    return redirect('request_list')

@user_passes_test(lambda u: u.is_superuser)
def delete_request(request, pk):
    # Получаем заявку
    request_obj = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        request_obj.delete()  # Удаляем заявку
        return redirect('request_list')  # Перенаправляем на страницу со списком заявок

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем пользователя в базе данных
            return redirect('login')  # Перенаправляем на страницу входа после успешной регистрации
    else:
        form = RegistrationForm()

    return render(request, 'photobooth/register.html', {'form': form})

    def form_valid(self, form):
        user = form.save()
        return redirect('login')

class LoginView(TemplateView):
    template_name = 'photobooth/login.html'




@method_decorator(login_required, name='dispatch')
class RequestListView(ListView):
    model = Request
    template_name = 'photobooth/request_list.html'

    def get_queryset(self):
        queryset = Request.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(client__user=self.request.user)
        # Добавление фильтрации по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

@method_decorator(login_required, name='dispatch')
class RequestDetailView(DetailView):
    model = Request
    template_name = 'photobooth/request_detail.html'


@method_decorator(login_required, name='dispatch')
class RequestCreateView(CreateView):
    model = Request
    form_class = RequestForm
    template_name = 'photobooth/request_form.html'
    success_url = reverse_lazy('request_list')  # ✅ вот это обязательно

    def form_valid(self, form):
        form.instance.client = self.request.user.client
        response = super().form_valid(form)

        # ✉ Email
        email_text = (
            f"Создана новая заявка #{form.instance.id} пользователем {self.request.user.username}.\n"
            f"Пожелания: {form.instance.description}\n"
            f"Контакты: {form.instance.contact_info}\n"
            f"Дата мероприятия: {form.instance.event_date}\n"
            f"Количество гостей: {form.instance.guest_count}"
        )
        send_mail(
            'Новая заявка создана',
            email_text,
            'your_email@gmail.com',
            ['vzn.serg@gmail.com'],
            fail_silently=False,
        )

        # 🤖 Telegram
        async def send_telegram_message():
            request_obj = HTTPXRequest(connect_timeout=5.0, read_timeout=5.0)
            bot = Bot(token=TELEGRAM_TOKEN, request=request_obj)
            telegram_text = (
                f" Новая заявка #{form.instance.id}\n"
                f" Пользователь: {self.request.user.username}\n"
                f" Пожелания: {form.instance.description}\n"
                f" Контакты: {form.instance.contact_info}\n"
                f" Дата: {form.instance.event_date}\n"
                f" Гостей: {form.instance.guest_count}"
            )
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=telegram_text)

        try:
            asyncio.run(send_telegram_message())
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}")

        return response


class ProfileView(TemplateView):
    template_name = 'photobooth/profile.html'

def custom_logout_view(request):
    logout(request)
    return redirect('home')  # Замените 'home' на нужный URL

class GalleryView(TemplateView):
    template_name = 'photobooth/gallery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = GalleryImage.objects.order_by('-uploaded_at')
        return context

@method_decorator(login_required, name='dispatch')
class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'photobooth/review_form.html'
    success_url = reverse_lazy('review_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверка: есть ли заявки у пользователя
        has_request = Request.objects.filter(client=request.user.client).exists()
        if not has_request:
            return redirect('review_list')  # Или показ сообщения, что отзыв недоступен
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.request = Request.objects.filter(client=self.request.user.client).last()
        return super().form_valid(form)

class ReviewListView(ListView):
    model = Review
    template_name = 'photobooth/review_list.html'
    context_object_name = 'reviews'
    ordering = ['-created_at']


@method_decorator(login_required, name='dispatch')
class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'photobooth/review_form.html'
    success_url = reverse_lazy('review_list')

    def dispatch(self, request, *args, **kwargs):
        if not Request.objects.filter(client=request.user.client).exists():
            return redirect('review_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.request = Request.objects.filter(client=self.request.user.client).last()
        return super().form_valid(form)
