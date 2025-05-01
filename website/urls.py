# website/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth.views import LogoutView

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'support-tickets', views.SupportTicketViewSet)
router.register(r'records', views.RecordViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('sign-in/', views.signIN, name='signIN'),
    path('sign-up/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account, name='account'),
    path('netflix/', views.netflix_page, name='netflix_page'),
    path('spotify/', views.spotify_page, name='spotify_page'),
    path('disney/', views.disney_page, name='disney_page'),
    path('crunchyroll/', views.crunchyroll_page, name='crunchyroll_page'),
    path('about/', views.about, name='about'),
    path('offer/', views.offer, name='offer'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('test-images/', views.test_images, name='test_images'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('api/', include(router.urls)),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('products/', views.product_list, name='product_list'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('support/', views.support_ticket_list, name='support_ticket_list'),
    path('support/create/', views.create_support_ticket, name='create_support_ticket'),
    path('support/ticket/<uuid:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    # Streaming Video
    path('hbomax/', views.hbomax_page, name='hbomax_page'),
    path('prime/', views.prime_page, name='prime_page'),
    path('hulu/', views.hulu_page, name='hulu_page'),
    path('appletv/', views.appletv_page, name='appletv_page'),
    path('paramount/', views.paramount_page, name='paramount_page'),
    path('peacock/', views.peacock_page, name='peacock_page'),
    # Music
    path('applemusic/', views.applemusic_page, name='applemusic_page'),
    path('youtubemusic/', views.youtubemusic_page, name='youtubemusic_page'),
    path('deezer/', views.deezer_page, name='deezer_page'),
    # Gaming
    path('xbox/', views.xbox_page, name='xbox_page'),
    path('playstation/', views.playstation_page, name='playstation_page'),
    path('eaplay/', views.eaplay_page, name='eaplay_page'),
    path('ubisoft/', views.ubisoft_page, name='ubisoft_page'),
]
