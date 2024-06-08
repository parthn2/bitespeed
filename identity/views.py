from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class IdentifyView(APIView):
    def post(self, request):

        return Response(status=status.HTTP_200_OK)
