from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from cart.models import Cart, Order

User=get_user_model()

@receiver(post_save, sender=User)
def create_cart_for_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

# @receiver(post_save, sender=Order)
# def notify_vendors_on_order(sender,instance,created,**kwargs):
#     if created:
#         order=instance
#         cart = order.cart
#         vendor_notified=set()
#
#         for item in cart.items.select_related('product__vendor'):
#             vendor=item.product.vendor
#             if vendor.id not in vendor_notified:
#                 send_mail(
#                     subject='New Order Received',
#                     message=f'You have a new order containing your product: {item.product.name}.',
#                     from_email='EMAIL_HOST_USER',
#                     recipient_list=[vendor.email],
#                     fail_silently=True,
#                 )
#                 vendor_notified.add(vendor.id)