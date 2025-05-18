from django.contrib import admin
from .models import *

admin.site.register(PricingPackage)
admin.site.register(ContactInfo)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'request', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('created_at',)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'uploaded_at')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'description', 'pricing_package', 'status', 'created_at')
    list_filter = ('status', 'pricing_package')  # Фильтрация по статусу и пакету
    search_fields = ('description', 'client__user__username')  # Поиск по описанию и имени клиента
    actions = ['delete_selected', 'mark_as_in_progress', 'mark_as_completed']  # Доступные действия

    # Настроим действия, чтобы администратор мог изменять статус заявки
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_as_in_progress.short_description = "Отметить как 'В процессе'"

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Отметить как 'Завершено'"

    # Настроим возможность массового удаления
    def delete_selected(self, request, queryset):
        queryset.delete()
    delete_selected.short_description = "Удалить выбранные заявки"

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client', 'content', 'created_at')

