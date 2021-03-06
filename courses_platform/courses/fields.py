from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class OrderField(models.PositiveIntegerField):
    """
    Extend PositiveIntegerField to order modules in courses, items in modules etc.

    If value is not provided, last_item+1 will be used.
    """
    def __init__(self, for_fields=None, *args, **kwargs):
        """Extend with for_fields order will be calculated with respect to."""

        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Override to check if value already exist and update or start anew.

        I.e. if OrderField defined on module and for_field is ['course']
        than we'll get all modules with same course and try to get objects
        with same course values and then retrieve last order number if any.
        """
        if getattr(model_instance, self.attname) is None:
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # filter by objects with the same field values
                    # for the fields in for_fields
                    query = {
                        field: getattr(model_instance, field)
                        for field in self.for_fields
                    }
                    qs = qs.filter(**query)
                # raises ObjectDoesNotExist
                last_item = qs.latest(self.attname)
                # right_value = getattr(last_item, self.attname)
                # value = last_item.order + 1
                last_order = getattr(last_item, self.attname)
                value = last_order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            # if we provided value set it as if it's PositiveIntegerField
            return super(OrderField, self).pre_save(model_instance, add)
