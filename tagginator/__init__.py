from dotenv import load_dotenv
from .lemmy import BaseLemmy
from .mastoproxy import BaseMastodon
from .tagginator import Tagginator

load_dotenv()

base_lemmy = BaseLemmy()
base_mastodon = BaseMastodon()
tagginator = Tagginator(base_lemmy,base_mastodon)
