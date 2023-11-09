import csv
import random
import re
import string
from io import TextIOWrapper

from estate_users.models import EstateUser, EstateUserProfile
from users.models import User


def create_user(first_name, last_name, email, mobile, password):
    # Check if the user exists first
    new_user = User.objects.filter(email=email).first()
    if not new_user:
        # Create the Django User
        new_user, created = User.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
        )
        new_user.set_password(password)
        new_user.verified = True
        new_user.save()
    return new_user


def create_estate_user(user_type, user, user_category, created_by_user, estate, address, status, relationship,
                       designation):
    """

    :param relationship:
    :param designation:
    :param status:
    :param address:
    :param estate:
    :param created_by_user: The user create or inviting this user (EstateUser instance)
    :param user_type:  RESIDENT,EXTERNAL,ADMIN
    :param user:
    :param user_category: BOARD_MEMBER,OTHERS, STAFF,FAMILY_MEMBER
    :return: ESTATE_USER
    """
    from users.tasks import send_request_to_join_estate
    # Check if the estate exist first
    estate_user = EstateUser.objects.filter(user=user, estate=estate).first()
    if not estate_user:
        # To prevent creating an unexpected user
        estate_user, created = EstateUser.objects.get_or_create(
            user=user,
            user_type=user_type,
            estate=estate,
            relationship=relationship,
            designation=designation,
        )
        estate_user.created_by = created_by_user
        if user_category:
            estate_user.user_category = user_category
        estate_user.invited = True
        # if status is set means it was the admin that invited the person we dont need to set
        if status:
            estate_user.status = status
        estate_user.save()

        # Send the admin a message that someone wants to join the estate
        if status != "ACTIVE":
            send_request_to_join_estate.delay(
                admin_email=estate.owner.email,
                first_name=estate_user.user.first_name,
                last_name=estate_user.user.last_name,
                admin_first_name=estate.owner.first_name,
                estate_name=estate.name,
                estate_id=estate.estate_id)

        # get the estate user profile
        estate_user_profile = EstateUserProfile.objects.filter(estate_user=estate_user).first()
        if not estate_user_profile:
            # save the address
            estate_user_profile.address = address
            estate_user_profile.save()
        return estate_user
    return None


def convert_string(input_string):
    """
    this is used to convert string an return a string without space or capital letter
    :param input_string: 
    :return: 
    """
    if not input_string or input_string == "":
        return None
    if type(input_string) != str:
        return input_string

    lowercase_string = input_string.lower()
    cleaned_string = re.sub('[^a-z0-9]', '', lowercase_string)
    return cleaned_string


def read_csv_file_return_data(csv_file):
    """
    This function is used to read a CSV file and return the data.
    The first column is considered as "First Name" and the second column is considered as "Last Name".

    :param csv_file: The CSV file object.
    :return: A list of dictionaries representing the data.
    """
    data = []
    errors = []

    reader = csv.reader(TextIOWrapper(csv_file, encoding='utf-8'))
    # Skip the header row
    next(reader)
    row_number = 0
    for row in reader:

        if len(row) >= 2:  # Make sure there are at least two columns
            row_number += 1
            first_name = row[0].strip()  # Get the value of the first column (index 0) as first name
            last_name = row[1].strip()  # Get the value of the second column (index 1) as last name
            email = row[2].strip()  # Get the value of the second column (index 1) as last name
            phone = row[3].strip()  # Get the value of the second column (index 1) as last name
            street_name = row[4].strip()  # Get the value of the second column (index 1) as last name
            house_plot_number = row[5].strip()  # Get the value of the second column (index 1) as last name
            user_exist = User.objects.filter(email=email).first()
            # check user
            if user_exist:
                errors.append(f"Row {row_number}: User already exist with this email {email}")
                continue
            row_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "street_name": street_name,
                "house_plot_number": house_plot_number,
            }
            data.append(row_data)

    return data, errors


def generate_random_digit():
    # Generate two random uppercase letters

    # Generate five random digits
    digits = ''.join(random.choices(string.digits, k=4))

    return digits


def create_estate_unique_user_id(instance, estate_acronym):
    """
    :param estate_acronym:
    :param instance: the access log object
    :return:
    """
    random_id = generate_random_digit()
    random_id = f"{estate_acronym}{random_id}"
    if instance.objects.filter(estate_user_id=random_id).exists():
        # it calls the function again to try creating it
        return create_estate_unique_user_id(instance, estate_acronym)
    # it returns the access
    return random_id
