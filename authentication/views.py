from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer 
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from .serializers import OrganizerPayoutSerializer
from events.utils import create_paystack_subaccount


from .models import CustomUser


# Register view
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'username': user.username,
                'user_type': user.user_type,
            }
        }, status=status.HTTP_201_CREATED)


# Login views
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'username': user.username,
                'user_type': user.user_type,
            }
        })

# User profile view
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
# user profile view by only the admin
class UserListView(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser] 


# forgot password view
User = get_user_model()

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://127.0.0.1:8000/api/auth/reset-password/{uid}/{token}/"

            # Send email (replace with real email sending logic)
            email_body = render_to_string('reset_password_email.html', {
             'reset_link': reset_link,
             'user': user,
            })

            send_mail(
                "Password Reset Request",
                email_body,
                "oyewolebarnabas97@gmail.com",  # Your from email
                [email],
                fail_silently=False,
                html_message=email_body  # 👈 HTML version
            )
            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

# Reset Password view
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

            new_password = request.data.get("password")
            user.set_password(new_password)
            user.save()

            return Response({"message": "Password reset successful!"}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

# Testing reset password views
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def preview_reset_email(request):
    # Mock user and reset link for testing
    user = User.objects.first()  # or create a dummy user
    reset_link = "http://127.0.0.1:8000/api/auth/reset-password/UID/TOKEN/"

    email_html = render_to_string('reset_password_email.html', {
        'user': user,
        'reset_link': reset_link
    })

    return HttpResponse(email_html)


class SetupSubaccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.user_type != 'organizer':
            return Response({"error": "Only organizers can set up subaccounts"}, status=403)

        # ✅ Prevent multiple subaccounts
        if user.subaccount_code:
            return Response({"message": "Subaccount already created."}, status=400)

        serializer = OrganizerPayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bank_code = serializer.validated_data['bank_code']
        account_number = serializer.validated_data['account_number']
        business_name = serializer.validated_data['business_name']

        result = create_paystack_subaccount(bank_code, account_number, business_name, user.email)

        if not result.get("status"):
            return Response({"error": result.get("message", "Paystack error")}, status=400)

        user.subaccount_code = result["data"]["subaccount_code"]
        user.bank_code = bank_code
        user.bank_account_number = account_number
        user.save()

        return Response({
            "message": "Subaccount created successfully.",
            "subaccount_code": user.subaccount_code
        })
