from django.conf import settings
from hellosign_sdk import HSClient
from hellosign_sdk.resource import ResourceList, SignatureRequest
import hellosign_sdk
import logging
import time

logger = logging.getLogger(__name__)

RETRIES = 5
SLEEP = 10

class APIException(Exception):
    pass

class HelloSign():
    def __init__(self, *args, **kwargs):
        self.client = HSClient(api_key=settings.HELLOSIGN_API_KEY)

    def _save_ids(self, signature, signature_request):
        signature.signature_request_id = signature_request.signature_request_id
        signature.signature_id = signature_request.signatures[0].signature_id
        signature.save(update_fields=['signature_request_id', 'signature_id'])

    def _look_up_ids(self, signature):
        '''
        This lookup uses an endpoint that Hellosign only allows us a single concurrent request to be
        running on, so it's error-prone.
        '''
        signature_request_list = ResourceList(
            SignatureRequest,
            self.get_signature_request_list(
                query="metadata:%s" % signature.id,
                page=1,
                page_size=2,
            )
        )

        if len(signature_request_list) != 1:
            raise APIException(
                "%d objects returned from HelloSign for signature id=%s" % (len(signature_request_list), signature.id)
            )

        self._save_ids(signature, signature_request_list[0])

    def request_signature(self, signature):
        req = self.client.send_signature_request_with_template(
            test_mode=not settings.HELLOSIGN_PRODUCTION_MODE,
            template_id=signature.template_id,
            custom_fields=[signature.get_custom_fields()],
            signers=signature.get_signers(),
            subject=signature.get_subject(),
            message=signature.get_message(),
            metadata=signature.get_metadata(),
        )
        self._save_ids(signature, req)

    def update_email(self, signature):
        if not signature.signature_request_id or not signature.signature_id:
            logger.warn('Attempting id lookup for signature %s' % signature.id)
            self._look_up_ids(signature)

        self.client._get_request().post(
            self.client.SIGNATURE_REQUEST_INFO_URL + 'update/' + signature.signature_request_id,
            data={
                "signature_id": signature.signature_id,
                "email_address": signature.user.email,
            }
        )

    def get_signature_request_list(self, query, page=1, page_size=100):
        for attempt in range(RETRIES):
            try:
                # the sdk get_signature_request_list method takes no query parameters, bypass it a bit
                return self.client._get_request().get(
                    self.client.SIGNATURE_REQUEST_LIST_URL,
                    parameters={
                        "query": query,
                        "page": page,
                        "page_size": page_size,
                    }
                )
            except hellosign_sdk.utils.exception.Conflict:
                logger.warning("API request attempt %d failed:" % attempt, exc_info=True)
                time.sleep(SLEEP)  # collided with active call, wait and retry
        else:
            raise hellosign_sdk.utils.exception.Conflict("API conflict encountered on %d retries" % RETRIES)

    def completed_signature_requests(self, cutoff_date, current_date, page_size=100):
        query = "complete:true AND created:{%s TO %s}" % (
            cutoff_date,
            current_date
        )
        page = 1
        num_pages = 1
        while page <= num_pages:
            signature_request_list = self.get_signature_request_list(
                query=query,
                page=page,
                page_size=page_size,
            )
            num_pages = signature_request_list["list_info"]["num_pages"]
            yield signature_request_list["signature_requests"]
            page += 1
