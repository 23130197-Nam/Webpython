from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PercentageDiscountViewSet, BuyXGetYDiscountViewSet, ApplyPromotionAPIView, PromotionAvailableAPIView
 
router = DefaultRouter()
router.register(r'percentage', PercentageDiscountViewSet, basename='percentage-discount')
router.register(r'buyxgety', BuyXGetYDiscountViewSet, basename='buyxgety-discount')

urlpatterns = [path('admin/', include(router.urls)), path('apply/', ApplyPromotionAPIView.as_view(), name='apply-promotion'),]
urlpatterns += [
    path("available/", PromotionAvailableAPIView.as_view(),
         name="promotion-available"),
]