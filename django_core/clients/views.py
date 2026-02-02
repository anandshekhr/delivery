from shared.jwt_utils import issue_jwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Client, ClientSecret
from django.shortcuts import get_object_or_404
import secrets

# Create your views here.
class RegisterClient(APIView):

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')

        if not name or not email:
            return Response({'error': 'Name and email are required.'}, status=400)

        client = Client.objects.create(name=name, email=email)
        secret_key = secrets.token_hex(32)
        ClientSecret.objects.create(client=client, secret_key=secret_key)

        return Response({
            'client_id': str(client.id),
            'secret_key': secret_key
        }, status=201)

class TokenView(APIView):

    def post(self, request):
        client_id = request.data.get('client_id')
        secret_key = request.data.get('secret_key')

        # Get client
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Invalid client ID.'}, status=404)

        # Verify secret
        if client.secret.secret_key != secret_key:
            return Response({'error': 'Invalid client credentials.'}, status=403)

        # Issue JWT manually
        token = issue_jwt({"client_id": str(client.id)})
        return Response({'access_token': token}, status=200)