from django.core.mail import send_mail
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from main import settings
from users.filterset import UserFilter
from users.models import User
from users.serializers import UserSerializer, ChangePasswordSerializer,UserListSerializer
from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class UserListView(APIView):

    def get(self, request):
        user = request.user
        serializer = UserListSerializer(user, context={"request": request})
        return Response(serializer.data)


class UserView(ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = UserFilter
    search_fields = ('first_name', 'last_name', 'role')
    ordering = ['-pk']

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(User, id=pk)
        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(User, id=pk)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(User, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)


class ChangePasswordView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    http_method_names = ['put']

    def update(self, request):
        user = self.request.user
        serializer = self.serializer_class(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response({"message": "Your password has been changed successfully"}, status.HTTP_202_ACCEPTED)


class ForgetPasswordDesktopView(APIView):
    # permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        # employee = get_object_or_404(User, email=request.data['email'])
        try:
            employee = User.objects.filter(email=request.data['email']).first()
            if employee is not None:
                user = get_object_or_404(User, id=employee.user.id)
                user_name = user.username
                password = User.objects.make_random_password(length=8)
                user.set_password(password)
                user.password = user.password
                user.save()
                subject = 'Reset your ABIS password'
                message = f'''Hi, {user.first_name} {user.last_name}, we are sending you this email
                        because you requested a password reset. Your new password is {password}.'''

                html_message = f'''
                        <h3>Hi, {user.first_name} {user.last_name}!</h3> 
                        <p>We are sending you this email because you requested a password reset.</p> 
                        <p>Your username is: <b> {user_name}</b> <br> Your new password is: <b>{password}</b></p>.
                        '''

                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email, ]
                send_mail(subject, message, email_from, recipient_list, html_message=html_message)
                message = "sent"
            else:
                message = "error"
        except:
            message = "error"
        return Response({"message": message})

