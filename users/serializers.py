from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PhoneNumber
from django.utils.translation import gettext as _
from rest_framework.validators import UniqueValidator
from phonenumber_field.serializerfields import PhoneNumberField


User = get_user_model()


class UserRegistrationSerializer(RegisterSerializer):
    """
    Serializer for registrating new users using email or phone number.
    """
    
    username = None
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    phone_number = PhoneNumberField(
        required = False,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=PhoneNumber.objects.all(),
                message=_("A user is already registered with this phone number.")
            )
        ]
    )
    email = serializers.EmailField(required=False)
    
    def validate(self, validated_data):
        email = validated_data.get('email', None)
        phone_number = validated_data.get("phone_number", None)
        
        if not (email or phone_number):
            raise serializers.ValidationError(_("Enter an email or a phone number."))
        
        if validated_data["password1"] != validated_data["password2"]:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        
        return validated_data
    
    
    def get_cleaned_data_extra(self):
        """
        Returns a dictionary of extra cleaned data.
        """
        return {
            "phone_number": self.validated_data.get("phone_number", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }
        
    def create_extra(self, user, validated_data):
        user.first_name = validated_data.get("first_name")
        user.last_name = validated_data.get("last_name")
        user.save()
        
        phone_number = validated_data.get("phone_number")
        
        if phone_number:
            PhoneNumber.objects.create(user=user, phone_number=phone_number)
            user.phone.save()
            
    def custom_signup(self, request, user):
        self.create_extra(user, self.get_cleaned_data_extra())
        
        
        
    




