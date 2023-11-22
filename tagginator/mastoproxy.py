import os
from mastodon import Mastodon

class BaseMastodon:
    def __init__(self):
        self.mastodon = Mastodon(
            access_token = 'pytooter_usercred.secret',
            api_base_url = f"https://{os.environ['MASTODON_INSTANCE']}"
        )       
