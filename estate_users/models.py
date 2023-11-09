import uuid

from django.db import models
from django.db.models.signals import post_save

from estates.models import Estate, EstateStreet, EstateZone
from users.models import User

ESTATE_USER_TYPE = (
    ("ADMIN", "ADMIN"),
    ("RESIDENT", "RESIDENT"),
    ("EXTERNAL", "EXTERNAL"),
)

STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("INACTIVE", "INACTIVE"),
)

ESTATE_USER_CATEGORY = (
    ("OTHERS", "OTHERS"),
    ("FAMILY_MEMBER", "FAMILY_MEMBER"),
    ("DOMESTIC_STAFF", "DOMESTIC_STAFF"),
    ("VENDOR", "VENDOR"),
    ("SECURITY", "SECURITY"),
    ("HEAD_OF_SECURITY", "HEAD_OF_SECURITY"),
    ("FINANCIAL_SECURITY", "FINANCIAL_SECURITY"),
    ("PRESIDENT", "PRESIDENT"),
    ("VICE_PRESIDENT", "VICE_PRESIDENT"),
    # added new
    ("CHIEF_SECURITY_OFFICER", "CHIEF_SECURITY_OFFICER"),
    ("FINANCIAL_SECRETARY", "FINANCIAL_SECRETARY"),
    ("ESTATE_MANAGER", "ESTATE_MANAGER"),
    ("EXCOS", "EXCOS"),

)
ROLE_CHOICES = (
    ("FACILITY_MANAGER", "FACILITY_MANAGER"),
    ("PROPERTY_MANAGER", "PROPERTY_MANAGER"),
    ("RESIDENT", "RESIDENT"),
    ("COMMUNITY_ASSOCIATION_EXCO", "COMMUNITY_ASSOCIATION_EXCO"),
    ("PROPERTY_DEVELOPER", "PROPERTY_DEVELOPER"),
    ("PROPERTY_DEVELOPER", "PROPERTY_DEVELOPER"),
    ("OTHERS", "OTHERS"),
)
RELATIONSHIP_CHOICES = (
    ("CHILD", "CHILD"),
    ("SIBLING", "SIBLING"),
    ("PARENT", "PARENT"),
    ("RELATIVE", "RELATIVE"),
    ("OTHERS", "OTHERS"),
)

DESIGNATION_CHOICES = (
    ("SECURITY", "SECURITY"),
    ("HOUSE_KEEPER", "HOUSE_KEEPER"),
    ("LESSON_TEACHER", "LESSON_TEACHER"),
    ("DRIVER", "DRIVER"),
    ("GARDENER", "GARDENER"),
    ("NURSE", "NURSE"),
    ("CHEF", "CHEF"),
    ("OTHERS", "OTHERS"),
)


class EstateUser(models.Model):
    """
    this is an estate user which is created once the user signs up
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    estate_zone = models.ForeignKey(EstateZone, on_delete=models.SET_NULL, blank=True, null=True)
    estate_street = models.ForeignKey(EstateStreet, on_delete=models.SET_NULL, blank=True,
                                      null=True)
    estate_user_id = models.CharField(max_length=250, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    user_type = models.CharField(max_length=50, choices=ESTATE_USER_TYPE, blank=True, null=True)
    user_category = models.CharField(max_length=50, default="OTHERS", choices=ESTATE_USER_CATEGORY)
    status = models.CharField(choices=STATUS, max_length=250)
    # I ADDED THIS NEW
    role = models.CharField(max_length=250, blank=True, null=True, choices=ROLE_CHOICES, default="OTHERS")
    created_by = models.ForeignKey("self",
                                   on_delete=models.SET_NULL,
                                   blank=True, null=True, related_name="created_by_user")

    invited = models.BooleanField(default=False)

    # list of services granted to the user
    on_to_one_message = models.BooleanField(default=True)
    utility_portal = models.BooleanField(default=True)
    emergency_service = models.BooleanField(default=True)
    gate_pass = models.BooleanField(default=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    # I ADDED THIS NEW
    relationship = models.CharField(max_length=250, blank=True, null=True,
                                    choices=RELATIONSHIP_CHOICES)  # this is for family members
    designation = models.CharField(max_length=250, blank=True, null=True,
                                   choices=DESIGNATION_CHOICES)  # this is for domestic staffs

    def save(self, *args, **kwargs):
        if not self.estate_user_id:
            from estate_users.utils import create_estate_unique_user_id

            estate_acronym = f"{self.estate.name}".replace(" ", "")[:2].upper()
            # Generate a unique estate_user_id if it's not provided
            self.estate_user_id = create_estate_unique_user_id(
                EstateUser, estate_acronym)  # You can modify the generation logic if needed
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-timestamp',)


def post_save_create_owner_estate_user(sender, instance: Estate, *args, **kwargs):
    """
    This creates the owner as part of the estate user and as an admin
    :return:
    """
    if instance:
        # If the admin is not part of the estate user then we create one
        estate_user = EstateUser.objects.filter(user=instance.owner, estate=instance).first()
        if not estate_user:
            # Create the estate user
            estate_user, created = EstateUser.objects.get_or_create(
                estate=instance,
                user=instance.owner,
                status="ACTIVE",
                user_type="ADMIN")
        if not estate_user.estate_user_id:
            from estate_users.utils import create_estate_unique_user_id
            estate_user.estate_user_id = create_estate_unique_user_id(EstateUser)
            # Save it
            estate_user.save()


post_save.connect(post_save_create_owner_estate_user, sender=Estate)


class EstateUserProfileManager(models.Manager):
    pass


GENDER_CHOICES = (
    ("MALE", "MALE"),
    ("FEMALE", "FEMALE")
)

REMINDERS = (
    ("ALL_REMINDERS", "ALL_REMINDERS"),
    ("IMPORTANT_REMINDERS", "IMPORTANT_REMINDERS"),
    ("NO_REMINDERS", "NO_REMINDERS"),
)

MENTIONS = (
    ("ALL_MENTIONS", "ALL_MENTIONS"),
    ("IMPORTANT_MENTIONS", "IMPORTANT_MENTIONS"),
    ("NO_MENTIONS", "NO_MENTIONS"),
)


class EstateUserProfile(models.Model):
    """
    The user profile is a model that is connected to the user and if the user model is deleted then
    the user profile will also be deleted
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate_user = models.OneToOneField(EstateUser, on_delete=models.CASCADE, related_name="estate_user_profile")
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_image", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    nationality = models.CharField(max_length=250, blank=True, null=True)
    news_update = models.BooleanField(default=False)
    tips_and_tutorial = models.BooleanField(default=False)
    user_search = models.BooleanField(default=False)
    reminders = models.CharField(choices=REMINDERS, max_length=250, default="ALL_REMINDERS")
    mentions = models.CharField(choices=MENTIONS, max_length=250, default="ALL_MENTIONS")
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = EstateUserProfileManager()

    class Meta:
        ordering = ('-timestamp',)

    @property
    def profile_image_url(self):
        #  adding this function to prevent issues when accessing the profile image if it doesn't exist
        try:
            image = self.profile_image.url
        except:
            image = None
        return image


def post_save_create_estate_user_profile(sender, instance, *args, **kwargs):
    """
    This creates a  estate user profile once a user is being created
    :param instance:  the user created or updated
    """
    if instance:
        estate_user_profile, created = EstateUserProfile.objects.get_or_create(estate_user=instance)


post_save.connect(post_save_create_estate_user_profile, sender=EstateUser)
