from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from .models import Staff
from .serializers import StaffSerializer, RegisterSerializer, LoginSerializer


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        staff = serializer.save()
        return Response({
            'id': staff.id,
            'name': staff.name,
            'email': staff.email,
            'role': staff.role,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            staff = Staff.objects.get(email=email)
            if check_password(password, staff.password):
                return Response({
                    'id': staff.id,
                    'name': staff.name,
                    'email': staff.email,
                    'role': staff.role,
                    'token': f'staff_{staff.id}',
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Staff.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        serializer = StaffSerializer(staff)
        return Response(serializer.data)
    except Staff.DoesNotExist:
        return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_staff(request):
    staffs = Staff.objects.all()
    serializer = StaffSerializer(staffs, many=True)
    return Response(serializer.data)

