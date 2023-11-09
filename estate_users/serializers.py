from rest_framework import serializers

from estate_users.models import EstateUserProfile, EstateUser, RELATIONSHIP_CHOICES, DESIGNATION_CHOICES, GENDER_CHOICES
from estates.serializers import EstateZoneSerializer, EstateStreetSerializer, EstateSerializer
from users.serializers import UserSerializer
from estates.models import ESTATE_TYPE


class EstateUserLittleInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EstateUser
        fields = [
            "id",
            "estate",
            "user",
            "user_type",
            "profile_image",
            "user_category",
            "role",
            "estate_user_id",
            "status",
            "timestamp",
        ]

        read_only_fields = [
            "id",
            "estate",
            "profile_image",
            "user",
            "estate_user_id",
            "timestamp",
        ]

    def get_profile_image(self, obj: EstateUser):
        if obj.estate_user_profile:
            if obj.estate_user_profile.profile_image:
                return obj.estate_user_profile.profile_image.url
        return None


class EstateUserSerializer(serializers.ModelSerializer):
    """
    This is used to show the detail of an estate user
    """
    user = UserSerializer(read_only=True)
    created_by = EstateUserLittleInfoSerializer(read_only=True)
    estate_zone = EstateZoneSerializer(read_only=True)
    estate_street = EstateStreetSerializer(read_only=True)
    estate = EstateSerializer(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EstateUser
        fields = [
            "id",
            "estate",
            "estate_zone",
            "estate_street",
            "profile_image",
            "role",
            "user",
            "user_type",
            "user_category",
            "status",
            "created_by",
            "invited",
            "estate_user_id",
            "on_to_one_message",
            "utility_portal",
            "emergency_service",
            "gate_pass",
            "timestamp",
            #     added new
            "relationship",
            "designation",
        ]
        read_only_fields = [
            "id",
            "estate",
            "created_by",
            "estate_zone",
            "profile_image",
            "estate_street",
            "timestamp",
            "on_to_one_message",
            "utility_portal",
            "emergency_service",
            "gate_pass",
            "estate_user_id",
        ]

    def get_profile_image(self, obj: EstateUser):
        if obj.estate_user_profile:
            if obj.estate_user_profile.profile_image:
                return obj.estate_user_profile.profile_image.url
        return None


class EstateUserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Used to returning more details of a user profile , and also with the image of the
    profile image we are also able to return that
    """
    estate_user = EstateUserSerializer(read_only=True)

    class Meta:
        model = EstateUserProfile
        fields = [
            "id",
            "estate_user",
            "gender",
            "profile_image",
            "date_of_birth",
            "address",
            "description",
            "nationality",
            "news_update",
            "tips_and_tutorial",
            "user_search",
            "reminders",
            "mentions",
            "timestamp",
        ]
        read_only_fields = [
            "estate_user",
            "id",
        ]


class EstateUserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Used for updating a user profile
    """
    estate_type = serializers.ChoiceField(choices=ESTATE_TYPE, required=False)

    class Meta:
        model = EstateUserProfile
        fields = [
            "id",
            "gender",
            "profile_image",
            "date_of_birth",
            "address",
            "description",
            "nationality",
            "estate_type",
            "news_update",
            "tips_and_tutorial",
            "user_search",
            "reminders",
            "mentions",
        ]
        read_only_fields = [
            "id",
        ]


class EstateUserProfileUpdateProfileImageSerializer(serializers.ModelSerializer):
    """
    Used for updating a user profile
    """

    class Meta:
        model = EstateUserProfile
        fields = [
            "id",
            "profile_image",
        ]
        read_only_fields = [
            "id",
        ]


RESIDENT_INVITE_USER_CATEGORY = (
    ("FAMILY_MEMBER", "FAMILY_MEMBER"),
    ("DOMESTIC_STAFF", "DOMESTIC_STAFF"),
)


class ResidentInviteEstateUserSerializer(serializers.Serializer):
    """
    This is used to invite user, and it is only used by the resident to invite
    """
    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    mobile = serializers.CharField(max_length=250)
    email = serializers.EmailField(max_length=250)
    user_category = serializers.ChoiceField(choices=RESIDENT_INVITE_USER_CATEGORY)


class ResidentMobileInviteEstateUserSerializer(serializers.Serializer):
    """
    This is used to invite user, and it is only used by the resident to invite
    """
    profile_image = serializers.ImageField(required=False)
    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    designation = serializers.ChoiceField(choices=DESIGNATION_CHOICES, required=False)
    address = serializers.CharField(max_length=250, required=False)
    relationship = serializers.ChoiceField(choices=RELATIONSHIP_CHOICES, required=False)
    mobile = serializers.CharField(max_length=250)
    email = serializers.EmailField(max_length=250)
    user_category = serializers.ChoiceField(choices=RESIDENT_INVITE_USER_CATEGORY)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)

    def validate(self, attrs):
        """
        this is used to validate the datas required
        :param attrs:
        :return:
        """
        if attrs.get('user_category') == "DOMESTIC_STAFF":
            if not attrs.get("profile_image"):
                raise serializers.ValidationError({"profile_image": "profile image required "})
            if not attrs.get("gender"):
                raise serializers.ValidationError({"gender": "gender required "})
            if not attrs.get("address"):
                raise serializers.ValidationError({"address": "address required "})
            if not attrs.get("designation"):
                raise serializers.ValidationError({"designation": "designation required "})
        if attrs.get('user_category') == "FAMILY_MEMBER":
            if not attrs.get("relationship"):
                raise serializers.ValidationError({"relationship": "relationship required "})

        return attrs


ADMIN_INVITE_USER_TYPE = (
    ("ADMIN", "ADMIN"),
    ("RESIDENT", "RESIDENT"),
    ("EXTERNAL", "EXTERNAL"),
)

ADMIN_INVITE_USER_CATEGORY = (
    ("SECURITY", "SECURITY"),
    ("HEAD_OF_SECURITY", "HEAD_OF_SECURITY"),
    ("FINANCIAL_SECURITY", "FINANCIAL_SECURITY"),
    ("PRESIDENT", "PRESIDENT"),
    ("VICE_PRESIDENT", "VICE_PRESIDENT"),
    # ADD THIS
    # added new
    ("CHIEF_SECURITY_OFFICER", "CHIEF_SECURITY_OFFICER"),
    ("FINANCIAL_SECRETARY", "FINANCIAL_SECRETARY"),
    ("ESTATE_MANAGER", "ESTATE_MANAGER"),
    ("EXCOS", "EXCOS"),
)


class AdminInviteEstateUserSerializer(serializers.Serializer):
    """
    This is used by the estate admin to invite estate users
    """
    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    mobile = serializers.CharField(max_length=250)
    email = serializers.EmailField(max_length=250)
    user_type = serializers.ChoiceField(choices=ADMIN_INVITE_USER_TYPE)
    user_category = serializers.ChoiceField(choices=ADMIN_INVITE_USER_CATEGORY, required=False)

    def validate(self, attrs):
        user_type = attrs.get("user_type")
        user_category = attrs.get("user_category")
        if user_type == "EXTERNAL":
            if not user_category:
                raise serializers.ValidationError("user category required when inviting external")
            if user_category != "SECURITY":
                if user_category != "VENDOR":
                    raise serializers.ValidationError(f"An external cannot be {user_category}")
        return attrs


MODIFY_ESTATE_USER_STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("INACTIVE", "INACTIVE"),
)


class ModifyEstateUserSerializer(serializers.Serializer):
    estate_user_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=MODIFY_ESTATE_USER_STATUS)


class EstateUserBulkUploadSerializer(serializers.Serializer):
    """
    this is used to make bulk upload for  estate user
    """
    csv_file = serializers.FileField()
