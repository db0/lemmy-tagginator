import os
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
        tagginator_user = self.lemmy.user.get(username=f"tagginator@{os.environ['MASTODON_INSTANCE']}")
        self.tagginator_lemmy_id = tagginator_user["person_view"]["person"]['id']        
        for entry in TAG_REFERENCE:
            cdict = {
                "community": entry["community"],
                "origin_domain": f"https://{entry['community'].split('@')[1]}",
                "community_id": self.lemmy.discover_community(entry['community']),
                "tags": entry['tags'],
                "optional_tags": entry['optional_tags'],
                "auto_tagginate": entry["auto_tagginate"],
            }
            self.parsed_communities.append(cdict)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        for cdict in self.parsed_communities:
            # We only search for 1 new posts per community, to avoid looking like a spam account
            # This will allow us to spread our tagging to 1 per minute per community
            new_threads = self.lemmy.post.list(
                community_id=cdict["community_id"], sort=SortType.New, limit=5
            )
            found_matching = False
            for t in new_threads:
                dt = t['post']['published'].split('.')[0]
                if dt.endswith('Z'):
                    dt = dt[:-1]
                d = datetime.strptime(dt,"%Y-%m-%dT%H:%M:%S")
                if d > datetime.utcnow() - timedelta(hours=6) and not t['read']:
                    found_matching = True
                    post_url = t['post']['ap_id']
                    post_id = t['post']['id']
                    post_name = t['post']['name']
                    post_body = t['post'].get('body','')
                    tags = cdict['tags'].copy()
                    if "#SkipTagginator".lower() in post_body.lower():
                        logger.debug("Skipping '{post_name}' for having #SkipTagginator")
                        self.lemmy.post.mark_as_read(post_id, True)
                        continue
                    if not cdict["auto_tagginate"] and not "#UseTagginator".lower() in post_body.lower():
                        logger.debug("Avoiding '{post_name}' for not having #UseTagginator")
                        self.lemmy.post.mark_as_read(post_id, True)
                        continue
                    logger.info(f"Processing: {post_name} ({post_url}) in {cdict['community']}")
                    s = self.mastodon.search(post_url,result_type="statuses")
                    if not len(s['statuses']) > 0:
                        continue
                    mastodon_status = s['statuses'][0]
                    community_post_url = f"{self.lemmy.get_base_url()}/post/{post_id}"
                    if cdict["origin_domain"] != self.lemmy.get_base_url():
                        temp_lemmy = Lemmy(cdict["origin_domain"])
                        s = temp_lemmy.resolve_object(post_url)
                        if s is not None:
                            community_post_url = f"{cdict['origin_domain']}/post/{s['post']['post']['id']}"
                    for t in cdict['optional_tags']:
                        if f"#{t}".lower() in post_body.lower():
                            tags.append(t)
                    self.lemmy.post.mark_as_read(post_id, True)
                    self.mastodon.status_post(
                        in_reply_to_id=mastodon_status['id'],
                        status=f"New Lemmy Post: {post_name} ({community_post_url})"
                                f"\nTagging: #{' #'.join(tags)}"
                                "\n\n(Replying in the OP of this thread (NOT THIS BOT!) will appear as a comment in the lemmy discussion.)"
                                '\n\nI am a FOSS bot. Check my README: https://github.com/db0/lemmy-tagginator/blob/main/README.md',
                    )
                    # We break out of the loop so that we only consider the first unread post
                    break
            if not found_matching:
                pass
                # logger.debug(f"No new posts in community ID {cdict['community']}")

    def resolve_reports(self):
        rl = self.lemmy.comment.report_list(
            unresolved_only=True,
            limit=10
        )
        for report in rl:
            if report["comment"]["creator_id"] == self.tagginator_lemmy_id:
                reporter = self.lemmy.user.get(person_id=report["comment_report"]["creator_id"])
                lemmy_tagginator_text = "Lemmy Tagginator"
                try:
                    reporter_instance_url_base = reporter["person_view"]["person"]["actor_id"].split('/u/')
                    reporter_instance = reporter_instance_url_base[0].split('//')[1]
                    lemmy_tagginator_text = f"[Lemmy Tagginator]({reporter_instance_url_base[0]}/u/tagginator@utter.online)"
                except Exception as err:
                    logger.warning(f"Error trying to link tagginator: {err}")
                self.lemmy.private_message.create(
                    recipient_id=reporter["person_view"]["person"]["id"],
                    content=f"Please do not report the {lemmy_tagginator_text}. Simply block it and you won't ever see it again.\n\nThis is an automated response to your report from the lemmy.dbzer0.com admin team."
                )
                self.lemmy.comment.resolve_report(report["comment_report"]["id"])
                logger.info(f"Resolved Tagginator report from @{reporter['person_view']['person']['name']}@{reporter_instance}")        