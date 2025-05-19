import base64

import io
import json
import random
import string
from datetime import datetime, date

import face_recognition
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from .models import UserRegistration, CheckIn


def full_registration(request):
    if request.method == "POST":
        registration_data = UserRegistration()
        registration_data.participation_role = request.POST.get("participation_role")
        registration_data.first_name = request.POST.get("first_name")
        registration_data.last_name = request.POST.get("last_name")
        registration_data.birthday = request.POST.get("date_of_birth")
        registration_data.gender = request.POST.get("personal_gender")
        registration_data.email = request.POST.get("user_email")
        registration_data.phone = request.POST.get("mobile_number")
        registration_data.passport_id = request.POST.get("passport_id")
        registration_data.country = request.POST.get("country")
        registration_data.place_of_birth = request.POST.get("place_of_birth")
        registration_data.living_address = request.POST.get("living_address")
        registration_data.organization = request.POST.get("organization")
        registration_data.position = request.POST.get("position")
        registration_data.passport_image = request.FILES.get("passport_copy")
        registration_data.user_image = request.FILES.get("user_photo")

        # Этап 1: сохраняем модель (файл запишется на диск)
        registration_data.save()

        # Этап 2: вычисляем encoding и обновляем
        from .face_recognition_core.utils import get_face_encoding

        if registration_data.user_image and not registration_data.face_encoding:
            encoding = get_face_encoding(registration_data.user_image.path)
            if encoding:
                registration_data.face_encoding = encoding
                registration_data.save(update_fields=["face_encoding"])  # только обновим нужное поле

        numbers = string.digits
        random_id = ''.join(random.choices(numbers, k=6))
        return redirect('face:success-page', random_id)

    return render(request, 'face/registration.html')


def success_page(request, id):
    return render(request, 'face/success_page.html')


def face_check_in(request):
    return render(request, 'face/face_checkin.html')

@csrf_exempt  # Убери, если используешь CSRF-токен на клиенте
@require_POST
def verify_face(request):
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({'success': False, 'error': 'Нет данных изображения'}, status=400)

        # Удаление заголовка base64 и декодирование
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)

        # Получение face encoding
        unknown_encodings = face_recognition.face_encodings(image_np)
        if not unknown_encodings:
            return JsonResponse({'success': False, 'error': 'Лицо не найдено'})

        unknown_encoding = unknown_encodings[0]

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ошибка обработки изображения: {str(e)}'}, status=400)

    # Получаем всех пользователей с сохранённым encoding
    users = UserRegistration.objects.exclude(face_encoding__isnull=True).only(
        'id', 'face_encoding', 'first_name', 'last_name', 'user_image'
    )

    for user in users:
        try:
            known_encoding = np.array(user.face_encoding)
            match = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.45)[0]

            if match:
                already_checked_in = CheckIn.objects.filter(user=user, timestamp__date=date.today()).exists()

                if not already_checked_in:
                    CheckIn.objects.create(user=user)

                # Получаем список уже прошедших проверку
                checked_in_users = CheckIn.objects.filter(timestamp__date=date.today()).select_related('user')
                checked_users_data = [
                    {
                        'user_id': checkin.user.id,
                        'name': f"{checkin.user.first_name} {checkin.user.last_name}",
                        'photo_url': checkin.user.user_image.url,
                        'timestamp': checkin.timestamp.isoformat()
                    }
                    for checkin in checked_in_users
                ]

                return JsonResponse({
                    'success': True,
                    'user_id': user.id,
                    'user': f"{user.first_name} {user.last_name}",
                    'timestamp': now().isoformat(),
                    'already_checked_in': already_checked_in,
                    'photo_url': user.user_image.url,
                    'checked_users': checked_users_data
                })

        except Exception:
            continue

    return JsonResponse({'success': False, 'error': 'Совпадений не найдено'})