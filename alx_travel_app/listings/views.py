from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .tasks import send_payment_confirmation_email

# Create your views here.
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        
        # Automatically initiate payment
        transaction_id = f"{self.request.user.id}-{booking.id}-{int(booking.created_at.timestamp())}"
        amount = booking.listing.price  # Assuming price exists on Listing model

        payment = Payment.objects.create(
            user=self.request.user,
            booking=booking,
            transaction_id=transaction_id,
            amount=amount,
            status="Pending",
        )

        return payment.transaction_id


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def initiate_payment(self, request):
        user = request.user
        booking_id = request.data.get("booking_id")
        amount = request.data.get("amount")

        booking = get_object_or_404(Booking, id=booking_id, user=user)

        # Create a unique transaction ID
        transaction_id = f"{user.id}-{booking.id}-{int(booking.created_at.timestamp())}"

        data = {
            "amount": amount,
            "currency": "ETB",
            "email": user.email,
            "tx_ref": transaction_id,
            "return_url": "http://yourfrontend.com/payment-success",
            "callback_url": "http://yourbackend.com/api/payments/verify/",
            "customization[title]": "Booking Payment",
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(f"{settings.CHAPA_BASE_URL}/transaction/initialize", json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            payment = Payment.objects.create(
                user=user, booking=booking, transaction_id=transaction_id, amount=amount, status="Pending"
            )
            return Response({"checkout_url": response_data["data"]["checkout_url"]}, status=status.HTTP_200_OK)
        
        return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"])
    def verify_payment(self, request):
        transaction_id = request.query_params.get("transaction_id")
        payment = get_object_or_404(Payment, transaction_id=transaction_id)

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.get(f"{settings.CHAPA_BASE_URL}/transaction/verify/{transaction_id}", headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            status_code = response_data["data"]["status"]

            if status_code == "success":
                payment.status = "Completed"
                payment.save()

                send_payment_confirmation_email.delay(payment.user.email, transaction_id)

                return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)

        payment.status = "Failed"
        payment.save()
        return Response({"message": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
