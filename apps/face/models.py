from ckeditor.fields import RichTextField
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from face_recogn.settings import EMAIL_HOST_USER

from .face_recognition_core.utils import get_face_encoding


class UserRegistration(models.Model):

    class Meta:
        verbose_name = _('Регистрация пользователя')
        verbose_name_plural = _('Регистрация пользователей')

    participation_role = models.CharField(max_length=120, null=True)
    first_name = models.CharField(max_length=120, null=True)
    last_name = models.CharField(max_length=120, null=True)
    birthday = models.DateField(null=True, auto_now=False, auto_now_add=False)
    gender = models.CharField(max_length=120, null=True)
    email = models.CharField(max_length=120, null=True)
    phone = models.CharField(max_length=20, null=True)
    passport_id = models.CharField(max_length=20, null=True)
    country = models.CharField(null=True)
    place_of_birth = models.CharField(max_length=255, null=True)
    living_address = models.CharField(max_length=100, null=True)
    organization = models.CharField(max_length=255, null=True)
    position = models.CharField(max_length=255, null=True)
    passport_image = models.ImageField(upload_to='registration/passport_image')
    user_image = models.ImageField(upload_to='registration/user_face_image')
    face_encoding = ArrayField(models.FloatField(), null=True, blank=True)

    entry_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    # for moderator
    reply_subject = models.CharField(max_length=255, blank=True, null=True)
    reply_message = RichTextField(max_length=1000, blank=True, null=True)
    replied_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def user_photo(self):
        if self.user_image:
            return mark_safe('<img src="%s" style="width: 45px; height:45px;" />' % self.user_image.url)
        else:
            return 'No Image Found'

    user_photo.short_description = 'photo'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.reply_subject and self.reply_message:
            self.replied_date = timezone.now()
            send_mail(self.reply_subject, self.reply_message, EMAIL_HOST_USER, [self.email], fail_silently=False)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CheckIn(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Проверка пользователя')
        verbose_name_plural = _('Проверка пользователей')
