import random
import time
import math
import re
import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
import requests
import threading

logger = logging.getLogger(__name__)


def parse_loose_number(value_str):
    if not value_str or not value_str.strip():
        return None
    match = re.search(r'[+-]?[0-9]+(?:[.,][0-9]+)?', value_str.strip())
    if not match:
        return None
    number_str = match.group().replace(',', '.')
    try:
        return float(number_str)
    except ValueError:
        return None


def estimate_hz_and_planets(star_data):
    L = None
    if star_data.get('luminosity'):
        L = parse_loose_number(str(star_data['luminosity']))
    
    if L is None:
        R = parse_loose_number(str(star_data.get('radius', '')))
        T = parse_loose_number(str(star_data.get('temperature', '')))
        if R is not None and T is not None:
            L = (R * R) * math.pow(T / 5778.0, 4)
        else:
            return None, None
    
    SEFF_IN = 1.107
    SEFF_OUT = 0.356
    
    rin_au = math.sqrt(L / SEFF_IN)
    rout_au = math.sqrt(L / SEFF_OUT)
    
    habitable_zone = f"{rin_au:.2f}-{rout_au:.2f} a.e."
    
    M = parse_loose_number(str(star_data.get('mass', '')))
    FeH = parse_loose_number(str(star_data.get('metallicity', '')))
    
    if M is None:
        M = 1.0
    if FeH is None:
        FeH = 0.0
    
    n_planets = 2.5 * math.pow(M, 0.8) * math.pow(10, 0.3 * FeH)
    if n_planets < 0.5:
        n_planets = 0.5
    if n_planets > 10:
        n_planets = 10
    
    probable_number_of_planets = round(n_planets)
    
    return habitable_zone, probable_number_of_planets


def send_result_to_main_service(selected_stars_id, star_id, habitable_zone, probable_number_of_planets):
    url = f"{settings.MAIN_SERVICE_URL}/api/calculate-exoplanets/update-result"
    
    payload = {
        'selected_stars_id': selected_stars_id,
        'star_id': star_id,
        'habitable_zone': habitable_zone,
        'probable_number_of_planets': probable_number_of_planets,
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Service-Token': settings.MAIN_SERVICE_TOKEN,
    }
    
    try:
        logger.info(f"Отправляем результат в основной сервис: {url}")
        response = requests.put(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Результат успешно отправлен. Статус: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке результата в основной сервис: {e}")
        return False


def calculate_async(selected_stars_id, star_id, star_data):
    logger.info(f"Начинаем расчет для selected_stars_id={selected_stars_id}, star_id={star_id}")
    
    delay = random.uniform(5, 10)
    logger.info(f"Задержка: {delay:.2f} секунд")
    time.sleep(delay)
    
    habitable_zone, probable_number_of_planets = estimate_hz_and_planets(star_data)
    
    if habitable_zone is None:
        habitable_zone = ""
    if probable_number_of_planets is None:
        probable_number_of_planets = 0
    
    send_result_to_main_service(selected_stars_id, star_id, habitable_zone, probable_number_of_planets)


@api_view(['POST'])
def calculate_exoplanets(request):
    try:
        data = request.data
        
        selected_stars_id = data.get('selected_stars_id')
        star_id = data.get('star_id')
        star_data = data.get('star_data', {})
        
        if selected_stars_id is None or star_id is None:
            return JsonResponse(
                {'error': 'selected_stars_id and star_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        thread = threading.Thread(
            target=calculate_async,
            args=(selected_stars_id, star_id, star_data)
        )
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'status': 'accepted',
            'message': 'Calculation started',
            'selected_stars_id': selected_stars_id,
            'star_id': star_id,
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

