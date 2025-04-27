from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import create_paystack_subaccount
from authentication.serializers import OrganizerPayoutSerializer
from rest_framework import generics
from .models import Transaction
from .serializers import TransactionSerializer

class CreateSubaccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.user_type != 'organizer':
            return Response({"error": "Only organizers can create subaccounts"}, status=403)

        serializer = OrganizerPayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        res = create_paystack_subaccount(
            bank_code=serializer.validated_data['bank_code'],
            account_number=serializer.validated_data['account_number'],
            business_name=serializer.validated_data['business_name'],
            email=user.email,
        )

        if not res.get("status"):
            return Response({"error": res.get("message", "Failed to create subaccount")}, status=400)

        user.subaccount_code = res["data"]["subaccount_code"]
        user.bank_code = serializer.validated_data['bank_code']
        user.bank_account_number = serializer.validated_data['account_number']
        user.save()

        return Response({
            "message": "Subaccount created",
            "subaccount_code": user.subaccount_code
        })


class MyTransactionsView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
