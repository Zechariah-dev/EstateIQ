import random
import string
import time

import requests
from decouple import config
from django.conf import settings
from django.http import Http404, HttpResponseBadRequest
from rest_framework.exceptions import APIException, ParseError

from estates.models import Estate, EstateZone
from users.models import User


def check_admin_access_estate(user: User, estate: Estate):
    # check if the user is the owner of the estate
    if user == estate.owner:
        return True
    # check if the user is one of the admin
    if estate.estateuser_set.filter(user=user, status="ACTIVE", user_type="ADMIN").first():
        return True
    return False


def check_user_access_estate(user: User, estate: Estate):
    # check if the user is the owner of the estate
    if user == estate.owner:
        return True
    # check if the user is one of the admin or resident
    if estate.estateuser_set.filter(user=user, status="ACTIVE").first():
        return True
    return False


def get_estate(estate_id):
    """
    this get the esate if the estate_id is passed in the params
    :param estate_id: estate_id
    :return:
    """
    # the estate_id is created randomly (10 alphanumeric values)
    estate = Estate.objects.filter(estate_id=estate_id).first()
    # send message if the estate is inactive
    # if estate.status == "INACTIVE":
    #     raise ParseError({"error": "Estate not Active. Wait for admin approval"})
    if not estate:
        raise ParseError({"error": "Estate with this ID does not exist"})
    return estate


def get_estate_zone(estate_zone_id):
    """
    this get the esate if the estate_id is passed in the params
    :param estate_id: estate_id
    :return:
    """
    # the estate_id is created randomly (10 alphanumeric values)
    estate_zone = EstateZone.objects.filter(id=estate_zone_id).first()
    if not estate_zone:
        raise Http404
    return estate_zone


def get_estate_user(estate: Estate, user: User):
    """
    It raises error or return the current loggedin estate user
    using the estate and the logged-in user in arguments
    :return:
    """
    estate_user = estate.estateuser_set.filter(user=user).first()
    if not estate_user:
        raise Http404
    # if estate_user.status != "ACTIVE":
    #     raise ParseError({"error": "Account Currently not Active."})
    return estate_user


def generate_random_string():
    # Generate two random uppercase letters

    # Generate five random digits
    digits = ''.join(random.choices(string.digits, k=5))

    # Combine the letters and digits to create the random string

    return digits


def create_unique_estate_id(instance):
    """
    :param instance: the estate object
    :return:
    """
    random_id = generate_random_string()
    if instance.objects.filter(estate_id=random_id).exists():
        # it calls the function again to try creating it
        return create_unique_estate_id(instance)
    # it returns the estate_id
    return random_id


def generateTransactionRef(model_class, type):
    """
    instance: the current model we are editing
    model: Model instance
    type: either utility or plan
    :returns a transaction reference
    """
    available_types = ["utility", "plan"]
    if type not in available_types:
        # It raise http404 for now
        # fixme: add a valid error to catch
        raise HttpResponseBadRequest
    rawTime = round(time.time() * 10)
    timestamp = int(rawTime)
    transaction_reference = f'EstateIQ-{type}-{str(timestamp)}'
    # Check if the transaction reference already exists
    if model_class.objects.filter(transaction_reference=transaction_reference).exists():
        return generateTransactionRef(model_class, type)
    return transaction_reference


def flutterwave_payment(path, payload, request_type):
    """
    :param path: the path on the base url
    :param payload: the json we're currently sending to flutterwave
    :param request_type: either POST,GET,PUT or delete
    :return:
    """
    try:
        secret_key = settings.RAVE_SECRET_KEY
        base_url = settings.RAVE_BASE_URL
        url = f"{base_url}{path}"
        headers = {"Content-Type": "application/json",
                   "Authorization": f'Bearer {secret_key}'}
        response = requests.request(request_type, url, json=payload, headers=headers)
        print(response.json())
        print(response.text)
        if response.json().get('status') == 'success':
            return response.json()
    except Exception as a:
        print(a)
    return None


def paystack_payment(path, payload, request_type):
    """

    :param path: the path on the base url
    :param payload: the json we're currently sending to flutterwave
    :param request_type: either POST,GET,PUT or delete
    :return:
    """
    try:
        secret_key = config('RAVE_SECRET_KEY')
        url = f"{config('FLUTTERWAVE_BASE_URL')}{path}"
        headers = {"Content-Type": "application/json",
                   "Authorization": f'Bearer {secret_key}'}
        response = requests.request(request_type, url, json=payload, headers=headers)
        print(response.json())
        print(response.text)
        if response.json().get('status') == 'success':
            return response.json()
    except Exception as a:
        print(a)
    return None


def verify_flutterwave_reference(transaction_ref):
    """
    this is used to verify the payment made from flutterwave
    :param transaction_ref: The transaction id gotten from flutterwave webhook
    :return: Bool
    """
    try:
        # This returns the json format from flutterwave
        response = flutterwave_payment(
            request_type='GET',
            payload={},
            path=f'transactions/verify_by_reference/?tx_ref={transaction_ref}')
        if response.get("data").get("status") == "successful":
            return True
        return False
    except Exception as a:
        print(a)
        return False


def verify_paystack_reference(transaction_ref):
    """
    this is used to verify the payment made from flutterwave
    :param transaction_ref: The transaction id gotten from flutterwave webhook
    :return: Bool
    """
    try:
        isVerified = flutterwave_payment(
            request_type='GET',
            path=f'transactions/verify_by_reference/?tx_ref{transaction_ref}')
        if isVerified:
            return True
        return False
    except Exception as a:
        print(a)
        return False
