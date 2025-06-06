from rest_framework.routers import DefaultRouter

from .views import LoanViewSet

router = DefaultRouter()
router.register(r"loans", LoanViewSet, basename="loans")

urlpatterns = router.urls
