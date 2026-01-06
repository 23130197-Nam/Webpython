from django.contrib import admin
from .models import BuyXGetYDiscount, PercentageDiscount, PromotionBase,PercentageDiscountProduct
# Register your models here.
admin.site.register(BuyXGetYDiscount)
admin.site.register(PercentageDiscount)
admin.site.register(PercentageDiscountProduct)
admin.site.register(PromotionBase)
