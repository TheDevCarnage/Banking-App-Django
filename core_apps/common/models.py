import uuid
from typing import Optional, Any
from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

User = get_user_model()


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContentView(TimeStampedModel):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("Content Type")
    )
    object_id = models.UUIDField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_views",
    )
    viewer_ip = models.GenericIPAddressField(
        verbose_name=_("Viewers IP Address"), null=True, blank=True
    )
    last_viewed = models.DateTimeField()

    class Mets:
        verbose_name = _("Content View")
        verbose_name_plural = _("Content Views")
        unique_together = ["content_type", "object_id", "user", "viewer_ip"]

    def __str__(self):
        return f"{self.content_type} viewed by {self.user.get_full_name if self.user else 'Anonymous'} from IP Address {self.viewer_ip}"

    @classmethod
    def record_view(
        cls, content_object: Any, user: Optional[User], viewer_ip: Optional
    ) -> None:
        content_type = ContentType.objects.get_for_model(content_object)
        try:
            view, created = cls.objects.get_or_create(
                content_type=content_type,
                object_id=content_object.id,
                defaults={
                    "user": user,
                    "viewer_ip": viewer_ip,
                    "last_viewed": timezone.now(),
                },
            )

            if not created:
                view.last_viewed = timezone.now()
                view.save()
        except IntegrityError:
            pass
