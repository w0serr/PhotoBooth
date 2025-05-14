from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.contrib.auth import logout
from .forms import RegistrationForm
from .models import *
from .forms import RequestForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

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

    def form_valid(self, form):
        form.instance.client = self.request.user.client
        form.save()

        # Отправка email
        send_mail(
            'Новая заявка создана',
            f"Заявка #{form.instance.id} была создана пользователем {self.request.user.username}.",
            'your_email@gmail.com',
            ['vzn.serg@gmail.com'],  # Email администратора
            fail_silently=False,
        )

        # Уведомление в Telegram
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"Новая заявка #{form.instance.id} от {self.request.user.username}: {form.instance.description}"
        )

        return redirect('request_list')

class ProfileView(TemplateView):
    template_name = 'photobooth/profile.html'

def custom_logout_view(request):
    logout(request)
    return redirect('home')  # Замените 'home' на нужный URL
