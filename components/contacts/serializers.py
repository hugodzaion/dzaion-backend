from rest_framework import serializers

from contacts.models import ChannelContacts

class ChannelContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelContacts
        fields = ['id', 'name', 'icon']