from django.conf import settings

from storages.backends.s3boto3 import S3BotoStorage

class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION
    
    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_CLOUDFRONT_DOMAIN
        super().__init__(*args, **kwargs)
    
class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
    
    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_CLOUDFRONT_DOMAIN
        super().__init__(*args, **kwargs)