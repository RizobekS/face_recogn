import face_recognition
from PIL import Image
import numpy as np
import os

def get_face_encoding(image_path: str) -> list | None:
    try:
        # Чтение изображения через стандартный метод библиотеки
        image_np = face_recognition.load_image_file(image_path)

        # Попробуем получить encoding
        face_locations = face_recognition.face_locations(image_np)
        encodings = face_recognition.face_encodings(image_np, face_locations)

        if encodings:
            return encodings[0].tolist()
        else:
            print("⚠️ Лицо не найдено.")
            return None
    except Exception as e:
        print(f"❌ Ошибка при распознавании лица: {e}")
        return None