from django.db.models.signals import ModelSignal

pre_clone_save = ModelSignal(use_caching=True)
post_clone_save = ModelSignal(use_caching=True)
