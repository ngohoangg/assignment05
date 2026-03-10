from django.db import models
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CustomerManager(BaseUserManager):
    def create_user(self, email, name=None, password=None, fullname=None, address=None):
        if not email:
            raise ValueError('Email is required')

        with transaction.atomic():
            full_name_text = fullname or name or ''
            full_name_obj = FullName.objects.create(full_name=full_name_text)
            user = self.model(email=self.normalize_email(email), fullname=full_name_obj)

            if address:
                address_obj = Address.objects.create(**address)
                user.address = address_obj

            user.set_password(password)
            user.save(using=self._db)
            return user


class FullName(models.Model):
    full_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'fullnames'

    def __str__(self):
        return self.full_name


class Address(models.Model):
    line1 = models.CharField(max_length=255, blank=True, default='')
    line2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=120, blank=True, default='')
    state = models.CharField(max_length=120, blank=True, default='')
    postal_code = models.CharField(max_length=30, blank=True, default='')
    country = models.CharField(max_length=120, blank=True, default='')

    class Meta:
        db_table = 'addresses'

    def __str__(self):
        parts = [self.line1, self.city, self.country]
        return ', '.join([part for part in parts if part])


class Customer(AbstractBaseUser):
    fullname = models.OneToOneField(
        FullName,
        on_delete=models.CASCADE,
        related_name='customer',
        null=True,
        blank=True,
    )
    address = models.OneToOneField(
        Address,
        on_delete=models.SET_NULL,
        related_name='customer',
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomerManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'customers'

    @property
    def name(self):
        if self.fullname:
            return self.fullname.full_name
        return ''

    def delete(self, *args, **kwargs):
        fullname = self.fullname
        address = self.address
        super().delete(*args, **kwargs)
        if fullname:
            fullname.delete()
        if address:
            address.delete()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

