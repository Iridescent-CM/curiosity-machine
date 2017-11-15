from allauth.account.adapter import DefaultAccountAdapter

class AllAuthAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template,
            message_context=None, extra_tags=''):
        # allauth stahp
        pass