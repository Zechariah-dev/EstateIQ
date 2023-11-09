def convert_plan_type_to_date(frequency):
    if frequency == "MONTHLY":
        due_date = timedelta(days=30) + timezone.now()
    elif frequency == "QUARTERLY":
        due_date = timedelta(days=30 * 3) + timezone.now()
    elif frequency == "HALF_YEARLY":
        due_date = timedelta(days=30 * 6) + timezone.now()
    elif frequency == "YEARLY":
        due_date = timedelta(days=365) + timezone.now()
    return due_date
