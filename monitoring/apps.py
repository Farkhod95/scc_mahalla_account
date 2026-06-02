from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        import monitoring.signals  # noqa: F401

        # Startup da barcha kameralarni go2rtc ga sinxronlaymiz
        # (delayed import — circular import oldini olish uchun)
        try:
            from monitoring.services import go2rtc_service
            synced = go2rtc_service.sync_all()
            if synced:
                import logging
                logging.getLogger(__name__).info(
                    "go2rtc: %d ShopCamera sinxronlandi.", synced
                )
        except Exception:
            pass  # go2rtc hali ishlamayotgan bo'lishi mumkin (startup order)
