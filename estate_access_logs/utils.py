from estates.utils import generate_random_string


def create_unique_access_code(instance):
    """
    :param instance: the access log object
    :return:
    """
    random_id = generate_random_string()
    if instance.objects.filter(access_code=random_id).exists():
        # it calls the function again to try creating it
        return create_unique_access_code(instance)
    # it returns the access
    return random_id
