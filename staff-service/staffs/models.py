from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class StaffManager(BaseUserManager):
    def create_user(self, email, name, password=None, role='STAFF'):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), name=name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(
            email=email,
            name=name,
            password=password,
            role=Staff.ROLE_MANAGER,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Staff(AbstractBaseUser):
    ROLE_STAFF = 'STAFF'
    ROLE_MANAGER = 'MANAGER'
    ROLE_CHOICES = [
        (ROLE_STAFF, 'Staff'),
        (ROLE_MANAGER, 'Manager'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = StaffManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'staffs'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

