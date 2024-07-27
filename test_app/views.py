from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth.models import User
from .models import Account
from .serializers import UserSerializer, AccountSerializer, UserRegistrationSerializer
from decimal import Decimal


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action == 'destroy':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return self.serializer_class

    def list(self, request):
        queryset = self.queryset
        username = request.query_params.get('username', None)
        is_verified = request.query_params.get('is_verified', None)

        if (username := username):
            queryset = queryset.filter(username__icontains=username)
        if (is_verified := is_verified) is not None:
            queryset = queryset.filter(account__is_verified=is_verified)


        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        user = self.get_object()
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        user.account.is_verified = True
        user.account.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def change_balance(self, request, pk=None):
        user = self.get_object()
        account = user.account

        if not account.is_verified:
            return Response({'error': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        amount = request.data.get('amount')
        if amount is None:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except (ValueError, TypeError, InvalidOperation):
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        account.balance += amount
        account.save()

        return Response({'new_balance': str(account.balance)})
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)