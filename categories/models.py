from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    #parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    image = models.URLField(null=True, blank=True)
    icon = models.CharField(max_length=100, null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    # tìm kiếm google
    meta_title = models.CharField(max_length=200, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name