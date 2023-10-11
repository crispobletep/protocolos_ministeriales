from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from core.models import Empresas


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)  # Agrega el campo username
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_company = models.BooleanField(default=False)
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"  # Cambia el campo de nombre de usuario a "username"
    REQUIRED_FIELDS = ["email", "nombre", "correo"]

    def __str__(self):
        return self.username
