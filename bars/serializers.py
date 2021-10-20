#  serializers.py
#  BelgianGamersBars
#
#  Created by Anton Romanova
#  Copyright © 2021 Belgian Gamers Bars. All rights reserved

from rest_framework import serializers
from .models import Bar


class BarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bar
        fields = "__all__"
        extra_fields = ['schedule']
        excluded_fields = ['']
        depth = 1

    def get_field_names(self, declared_fields, info):
        # Allows the usage of extra_fields in Meta
        expanded_fields = super(BarSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            expanded_fields += self.Meta.extra_fields

        return expanded_fields
