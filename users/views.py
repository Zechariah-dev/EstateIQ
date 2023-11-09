from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from estate_users.models import EstateUser
from estates.models import Estate
from users.models import User
from users.permissions import NotLoggedInPermission, LoggedInPermission, LoggedInStaffPermission
from users.serializers import UserUpdateSerializer, ChangePasswordSerializer, \
    ForgotPasswordOTPSerializer, SocialAuthSerializer, TokenSerializer, UserDetailSerializer
from .utils import validate_facebook_token, validate_google_token
from users.tasks import send_welcome_message


class EstateIQFacebookLoginAPIView(APIView):
    throttle_scope = 'monitor'
    permission_classes = [NotLoggedInPermission]

    def post(self, request):
        serializer = SocialAuthSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        auth_token = serializer.validated_data.get("auth_token")

        # this is used to validate the google auth token
        email = validate_facebook_token(auth_token)

        if not email:
            return Response({"error": "Auth token provided is not valid"}, status=400)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exists"}, status=400)
        if not user.verified:
            # Send verification mail to the user
            user.send_email_verify()
            return Response(
                {"error": "Your email address has not been verified. Check your inbox for the verification link."},
                status=status.HTTP_400_BAD_REQUEST, )
        token = Token.objects.filter(user=user).first()
        if not token:
            token = Token.objects.create(user=user)
        serializer = TokenSerializer(token)
        return Response(serializer.data, status=200)


class EstateIQGoogleLoginAPIView(APIView):
    throttle_scope = 'monitor'
    permission_classes = [NotLoggedInPermission]

    def post(self, request):
        serializer = SocialAuthSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        auth_token = serializer.validated_data.get("auth_token")
        email = validate_google_token(auth_token)

        if not email:
            return Response({"error": "Token expired or Auth token provided is not valid"}, status=400)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exists"}, status=400)
        if not user.verified:
            # Send verification mail to the user
            user.send_email_verify()
            return Response(
                {"error": "Your email address has not been verified. Check your inbox for the verification link."},
                status=status.HTTP_400_BAD_REQUEST, )
        token = Token.objects.filter(user=user).first()
        if not token:
            token = Token.objects.create(user=user)
        serializer = TokenSerializer(token)
        return Response(serializer.data, status=200)


class EstateIQLoginAPIView(LoginView):
    """
    Login view which contains throttle and can be access three times in a minute
    """
    throttle_scope = 'monitor'
    permission_classes = [NotLoggedInPermission]

    def post(self, request, *args, **kwargs):
        """
        :param args: 
        :param kwargs: 
        :return: it returns response using TokenSerializer serializer it checks if the user is not verified and
        if the user
        is not then it uses the default response from the  TokenSerializer
        """
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        self.login()
        if not self.request.user.verified:
            # Send verification mail to the user
            self.request.user.send_email_verify()
            return Response(
                {"error": "Your email address has not been verified. Check your inbox for the verification link."},
                status=status.HTTP_400_BAD_REQUEST, )
        return self.get_response()


class EstateIQRegisterAPIView(RegisterView):
    """
    Register view which contains throttle and can be access three times in a minute
    """
    throttle_scope = 'monitor'
    permission_classes = [NotLoggedInPermission]

    def create(self, request, *args, **kwargs):
        #  using the default serializer which was set
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #  create a user
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        #  means the user was created if the data exist, but we need to
        #  check if the user is verified
        if data:
            if not user.verified:
                # Send verification mail to the user
                user.send_email_verify()
                response = Response({
                    "message": "A verification link has been sent to your email. Please check your inbox and follow the instructions to complete the verification process."
                }, status=status.HTTP_200_OK, )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        return response


class RequestEmailLinkAPIView(APIView):
    """ This is used to request otp via email and if requested via email then we must verify via email
     with this function VerifyEmailAddressAPIView"""
    permission_classes = [NotLoggedInPermission]
    throttle_scope = 'monitor'

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            #  sends an otp to the user email
            if user.send_email_verify():
                return Response({'message': 'Successfully sent verification '}, status=200)
        elif not user:
            return Response({'error': 'Please make sure you send the right mail address '}, status=400)
        return Response({'error': 'There was an error performing your request please try again later '}, status=400)


class VerifyEmailAPIView(APIView):
    """
    This is used to verify an email using the otp passed and also it uses cache which was set to expire after 10 min
    """
    permission_classes = [NotLoggedInPermission]
    throttle_scope = 'monitor'

    def get(self, request):
        try:
            user_id = self.request.query_params.get("user_id")
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({'error': 'Please pass in the correct data'}, status=400)
            user.verified = True
            user.save()
            #
            estate_user = EstateUser.objects.filter(user=user).first()
            if estate_user:
                # Send the user a welcome message
                send_welcome_message.delay(
                    email=user.email,
                    first_name=user.first_name,
                    user_type=estate_user.user_type,
                    estate_id=estate_user.estate.estate_id)
            return Response({'message': 'Successfully verify your mail'}, status=200)
        except Exception as a:
            print("error-----", a)
            return Response({'error': 'There was an error performing your request.Email Not Verified'}, status=400)


class UserChangePasword(APIView):
    """
    This is used for a user when changing pasword
    """
    permission_classes = [LoggedInPermission]
    throttle_scope = 'monitor'

    def post(self, request):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get("password")
        user.set_password(password)
        user.save()
        return Response({"message": "Password Successfully Updated"}, status=200)


class UserUpdateAPIView(APIView):
    """
    This view is responsible for updating a user  models in which if he wants to switch profile
     to being a freelancer or the other
    """
    permission_classes = [LoggedInPermission]

    def put(self, request):
        """
        Update a user which already exit,
         and also I am passing context={'request': request} on the UserProfileUpdateSerializer to enable access of other
        params on other serializer during verification
        """
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, context={'request': request},
                                          partial=True)
        #  check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Successfully updated user', 'data': UserUpdateSerializer(request.user).data},
                        status=200)


class RequestEmailOTPAPIView(APIView):
    """ This is used to request otp via email and if requested via email then we must verify via email
     with this function VerifyEmailAddressAPIView"""
    permission_classes = [NotLoggedInPermission]
    throttle_scope = 'monitor'

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            #  sends an otp to the user email
            if user.send_email_otp():
                return Response({'message': 'Successfully sent OTP'}, status=200)
        elif not user:
            return Response({'error': 'Please make sure you send the right mail address '}, status=400)
        return Response({'error': 'There was an error performing your request please try again later '}, status=400)


class ForgotPasswordWithOTPAPIView(APIView):
    """
    Used when forgot password
    """
    permission_classes = [NotLoggedInPermission]
    throttle_scope = 'monitor'

    def post(self, request):
        serializer = ForgotPasswordOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        otp = serializer.data.get('otp')
        user = User.objects.filter(email__icontains=email).first()
        if not user:
            return Response({'error': 'User Does Not Exist. Please Pass in the correct data.'},
                            status=400)
        if user.validate_email_otp(otp):
            if user.check_password(password):
                return Response({'error': 'New password cannot be same as current password'},
                                status=400)
            user.set_password(password)
            user.save()
            return Response({'message': ' You have successfully changed your password'}, status=200)
        return Response({'error': 'OTP not valid or expired '}, status=400)


class SuperAdminGetUserListAPIView(ListAPIView):
    """
    this is used by the super admin to get detail of a user

    """
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    permission_classes = [LoggedInStaffPermission]


class SuperAdminGetUserDetailAPIView(RetrieveAPIView):
    """
    this is used by the super admin to get detail of a user

    """
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    permission_classes = [LoggedInStaffPermission]
    lookup_field = "id"


class UserDetailView(APIView):
    """
    this is use to get the user detal
    """
    permission_classes = [LoggedInStaffPermission]

    def get(self, request):
        data = UserDetailSerializer(instance=self.request.user).data
        return Response(data, status=200)

