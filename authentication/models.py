import uuid
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
          email=self.normalize_email(email),
          phone_number=phone_number           
        )

        if password:
            user.set_password(password)
            user.save(using=self._db)
        else:
            user.set_unusable_password()

        return user

    def create_superuser(self, email, phone_number ,password=None):

        user = self.create_user(
        email=self.normalize_email(email), phone_number=phone_number, password=password,
      )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
	uuid = models.UUIDField(editable=False, default=uuid.uuid4)
	password = models.CharField(max_length=128)
	phone_number = models.CharField(max_length=11, validators=[RegexValidator(r'^0\d{10}$', 'Mobile number should be 11 digits starting with 0.')], unique=True)
	email = models.EmailField(max_length=100 ,unique=True)
      
	email_verified = models.BooleanField(default=False)
	phone_number_verified = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	# required fields
	date_joined = models.DateTimeField(auto_now_add=True)
	last_login = models.DateTimeField(auto_now=True)
	is_admin = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_superuser = models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['phone_number']
	objects = UserManager()

	class Meta:
		ordering = ["date_joined"]

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True


