from typing import Any
from tagginator.tags import TAG_REFERENCE
from pythorhead.types import SortType
from datetime import datetime, timedelta
from loguru import logger
from pythorhead import Lemmy

class Tagginator:
    def __init__(self, _base_lemmy, base_mastodon):
        self.lemmy = _base_lemmy.lemmy
        self.mastodon = base_mastodon.mastodon
        self.parsed_communities = []
        for community,tags in TAG_REFERENCE.items():
            cdict = {
                "community": community,
                "origin_domain": f"https://{community.split('@')[1]}",
                "community_id": self.lemmy.discover_community(community),
                "tags": tags,
            }
            self.parsed_communities.append(cdict)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        for cdict in self.parsed_communities:
            # We only search for 1 new posts per community, to avoid looking like a spam account
            # This will allow us to spread our tagging to 1 per minute per community
            new_threads = self.lemmy.post.list(
                community_id=cdict["community_id"], sort=SortType.New, limit=1
            )
            found_post = False
            for t in new_threads:
                dt = t['post']['published'].split('.')[0]
                d = datetime.strptime(dt,"%Y-%m-%dT%H:%M:%S")
                if d > datetime.utcnow() - timedelta(hours=6) and not t['read']:
                    found_matching = True
                    post_url = t['post']['ap_id']
                    post_id = t['post']['id']
                    post_name = t['post']['name']
                    logger.info(f"Processing: {post_name} ({post_url})")
                    s = self.mastodon.search(post_url,result_type="statuses")
                    if not len(s['statuses']) > 0:
                        continue
                    mastodon_status = s['statuses'][0]
                    community_post_url = f"{self.lemmy.get_base_url()}/post/{post_id}"
                    if cdict["origin_domain"] != self.lemmy.get_base_url():
                        temp_lemmy = Lemmy(cdict["origin_domain"])
                        s = temp_lemmy.resolve_object(post_url)
                        if s is not None:
                            community_post_url = f"{cdict['origin_domain']}/post/{s['post']['id']}"
                    logger.debug(community_post_url)
                    self.mastodon.status_reply(
                        to_status=mastodon_status,
                        status=f"Tagging Lemmy Post '{post_name}' ({community_post_url}): #{' #'.join(cdict['tags'])}",
                    )
                    self.lemmy.post.mark_as_read(post_id, True)
            if not found_post:
                logger.debug(f"No new posts in community ID {cdict['community']}")
