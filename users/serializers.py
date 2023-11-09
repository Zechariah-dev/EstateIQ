from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException, ParseError
from rest_framework_simplejwt.tokens import RefreshToken

from estate_users.models import EstateUser, ROLE_CHOICES, EstateUserProfile
from estates.models import Estate, EstateStreet
from users.models import User
from .tasks import send_request_to_join_estate, send_user_to_wait_till_active, send_super_admin_activate_estate

ESTATE_PROCESS = (
    ("JOIN", "JOIN"),
    ("CREATE", "CREATE"),
)


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration for the instasew user serializer
    this adds extra fields to the django default RegisterSerializer
    """

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    mobile = serializers.CharField(required=False)
    # the enables to choose either creating  an esate or joining the estate
    estate_choice = serializers.ChoiceField(choices=ESTATE_PROCESS)
    estate_id = serializers.CharField(max_length=100)
    user_estate_street_id = serializers.UUIDField(required=False)
    user_house_address = serializers.CharField(required=False)
    role = serializers.ChoiceField(required=False, choices=ROLE_CHOICES)

    # create estate
    estate_name = serializers.CharField(max_length=250, required=False)
    estate_country = serializers.CharField(max_length=250, required=False)
    estate_address = serializers.CharField(max_length=250, required=False)
    estate_state = serializers.CharField(max_length=250, required=False)
    estate_lga = serializers.CharField(max_length=250, required=False)
    # the password
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'mobile',
            'estate_choice',
            'estate_id',
            "estate_name",
            "estate_country",
            "estate_address",
            "estate_state",
            "estate_lga",
            'password1',
            'password2',
        )

    def get_cleaned_data(self):
        """
        the default RegisterSerializer uses password1 and password2
        so  just get the data from password and  confirm_password and add it to the field for verification
        and also this enables us to pass extra data
        """
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            'mobile': self.validated_data.get('mobile', ''),
            'estate_choice': self.validated_data.get('estate_choice', ''),
            'estate_id': self.validated_data.get('estate_id', ''),
            'estate_name': self.validated_data.get('estate_name', ''),
            'user_estate_street_id': self.validated_data.get('user_estate_street_id', ''),
            'user_house_address': self.validated_data.get('user_house_address', ''),
            'role': self.validated_data.get('role', ''),
            'estate_country': self.validated_data.get('estate_country', ''),
            'estate_address': self.validated_data.get('estate_address', ''),
            'estate_state': self.validated_data.get('estate_state', ''),
            'estate_lga': self.validated_data.get('estate_lga', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
        }

    def validate_first_name(self, value):
        if value:
            if any(char.isdigit() for char in value):
                raise serializers.ValidationError("First name cannot contain numbers.")
        return value

    def validate_last_name(self, value):
        if value:
            if any(char.isdigit() for char in value):
                raise serializers.ValidationError("Last name cannot contain numbers.")
        return value

    def validate(self, attrs):
        # validate joint fields
        if not attrs.get("user_house_address") or attrs.get("user_house_address") == "":
            raise serializers.ValidationError({"user_house_address": "Home Address Cannot Be Blank."})

        # Get an estate with the estate_id if it has been used before
        estate_exists = Estate.objects.filter(estate_id=attrs.get('estate_id')).first()
        estate_name_exists = Estate.objects.filter(name__icontains=attrs.get('estate_name')).first()
        if attrs.get('estate_choice') == "CREATE":
            # Check if the required fields is provided for creating an estate
            if not attrs.get("estate_name") or not \
                    attrs.get("estate_country") or not \
                    attrs.get("estate_address") or not \
                    attrs.get("estate_state") or not \
                    attrs.get("estate_lga"):
                raise serializers.ValidationError("The required values for creating an estate was not passed"
                                                  " please make sure the estate_name estate_country, "
                                                  "estate_address, estate_state, estate_lga.")
            # Check if the estate_id has been used before
            if estate_exists:
                raise serializers.ValidationError({"estate_id": "estate id has already been used please try another"})
            if estate_name_exists:
                raise serializers.ValidationError(
                    {"estate_name": "estate name has already been used please try another"})
        if attrs.get("estate_choice") == "JOIN":
            # check if the estate exist
            if not estate_exists:
                raise serializers.ValidationError({"estate_id": "Estate with this ID does not exist"})
        return attrs

    def save(self, request):
        """
        Due to adding extra fields to the user model we created an adapter
        in the users app to save the  user extra field
        """
        # using the custom adapter I created on the adapters.py in the users app
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        mobile = self.cleaned_data.get("mobile")
        if mobile:
            user.mobile = mobile
            user.save()
        ##############################
        estate_id = self.cleaned_data.get("estate_id")
        estate = Estate.objects.filter(estate_id=estate_id).first()
        # Join an estate if the user choose JOIN
        user_type = "RESIDENT"
        if self.cleaned_data.get("estate_choice") == "JOIN":
            if estate:
                # if the estate exists
                estate_user, created = EstateUser.objects.get_or_create(
                    user=user,
                    estate=estate,
                    user_type="RESIDENT",
                    user_category="OTHERS",
                    status="INACTIVE"
                )
                user_estate_street_id = self.cleaned_data.get("user_estate_street_id")
                user_house_address = self.cleaned_data.get("user_house_address")
                role = self.cleaned_data.get("role")
                # if this id exists
                if user_estate_street_id and user_estate_street_id != "":
                    # check if the street exist
                    street = EstateStreet.objects.filter(id=user_estate_street_id).first()
                    if street:
                        estate_user.estate_street = street
                        estate_user.save()
                # check if role was passed
                if role and role != "":
                    estate_user.role = role
                    estate_user.save()
                # add the profile
                if user_house_address and user_house_address != "":
                    estate_user_profile = EstateUserProfile.objects.filter(estate_user=estate_user).first()
                    if estate_user_profile:
                        estate_user_profile.address = user_house_address
                        estate_user_profile.save()

                # Send the admin a message that someone wants to join the estate
                send_request_to_join_estate.delay(
                    admin_email=estate.owner.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    admin_first_name=estate.owner.first_name,
                    estate_name=estate.name,
                    estate_id=estate.estate_id)
                # send the user to wait
                send_user_to_wait_till_active.delay(
                    estate_name=estate.name,
                    email=user.email,
                    first_name=user.first_name,
                )
        elif self.cleaned_data.get("estate_choice") == "CREATE":
            user_type = "ADMIN"
            # Create the estate First
            if not estate:
                estate = Estate.objects.create(
                    owner=user,
                    estate_id=estate_id,
                    name=self.cleaned_data.get("estate_name"),
                    country=self.cleaned_data.get("estate_country"),
                    address=self.cleaned_data.get("estate_address"),
                    state=self.cleaned_data.get("estate_state"),
                    lga=self.cleaned_data.get("estate_lga"),
                )
                send_super_admin_activate_estate.delay(estate.estate_id, estate.name)
            else:
                user.delete()
                raise ParseError({"error": "Estate with this Name Already exists"})

        return user


class TokenSerializer(serializers.ModelSerializer):
    """
    In here I am checking if the user email has been verified before
    sending him his details
    """
    user = serializers.SerializerMethodField(read_only=True)
    access_token = serializers.SerializerMethodField(read_only=True)
    refresh_token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Token
        fields = ('access_token', 'refresh_token', 'user',)

    def get_access_token(self, obj):
        """
        This access token is a jwt token that get expired after a particular time given which could either be 1 hour
        """
        refresh = RefreshToken.for_user(obj.user)
        return str(refresh.access_token)

    def get_refresh_token(self, obj):
        """
        The refresh token gotten from  rest_framework_simplejwt.tokens
        :param obj: instance
        """
        refresh = RefreshToken.for_user(obj.user)
        return str(refresh)

    def get_user(self, obj):
        """
        it uses the custom serializer i created for authentication only so i just need this
        serializer method field to pass extra datas
        """
        try:
            print("the obj", obj)
            return UserDetailSerializer(obj.user, read_only=True).data
        except Exception as a:
            # just for debugging purposes
            print('====================', a)
            return 'error'


class UserDetailSerializer(serializers.ModelSerializer):
    """
    This returns more detail about a user, and it is only used when the user
    logs in or register, and also in other serializers as user,freelancer and customer
    It is also used  when users login or register to get information
    """

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'verified',
            'mobile',
            'is_staff',
        ]
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 4}}


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to update a user which exists
    """
    first_name = serializers.CharField(max_length=250, required=False, allow_blank=False)
    last_name = serializers.CharField(max_length=250, required=False, allow_blank=False)
    email = serializers.EmailField(required=False, allow_blank=False)
    mobile = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'mobile',
        ]

    def validate_email(self, obj):
        """This checks if the email has been used before and if it already exists by another user it raises an error
        and also the request is passed from the view to access the current user
        """
        logged_in_user = self.context['request'].user
        user = User.objects.filter(email=obj).first()
        if user:
            if logged_in_user.email != user.email:
                raise serializers.ValidationError(
                    'Please use a valid email that has not been used before')
        return obj


class VerifyEmailSerializer(serializers.Serializer):
    """
    This is used to verify the email address with otp of a user
    """
    otp = serializers.CharField(max_length=4)
    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    """
    This returns little detail of the user which is currently used in blog post
    """

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'mobile',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    this is used to update the password of a user currently loggedin
    """
    password = serializers.CharField(max_length=250)
    verify_password = serializers.CharField(max_length=250)

    def validate(self, attrs):
        password = attrs.get("password")
        verify_password = attrs.get("verify_password")
        if password != verify_password:
            raise serializers.ValidationError("Password does not match")
        return attrs


class ForgotPasswordOTPSerializer(serializers.Serializer):
    """
    Changing user password with otp only when user is not logged in  this means the user has forgotten his/her password
    so he would have request otp to his mail before sending the otp his new password and hs email
    used when user forgot password
    """
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100)


class SocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
