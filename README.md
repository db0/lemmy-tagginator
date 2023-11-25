# Lemmy Tagginator

This is a simple script that monitors specific [Lemmy](https://join-lemmy.org/) communities and attempts to #hashtag new posts so that they are discoverable in microblogging services like [mastodon](https://joinmastodon.org/).

## How does this work?

Any time a new post from one of the monitored communities appears on lemmy (see [tags.py](https://github.com/db0/lemmy-tagginator/blob/main/tagginator/tags.py)) a [mastodon account](https://utter.online/@tagginator) will reply to it with a comment providing the predefined tags for that community and a link to the main community in its source instance.

## Why is this necessary?

Even though Lemmy posts federate ([badly](https://github.com/LemmyNet/lemmy/issues/2972)) to microblogging service like mastodon, they do cannot be tagged. Even if you manually add tags, they are ignored. 

Lemmy is also suffering from a discoverability and engagement issue on niche communities, which creates a vicious cycle where a niche community doesn't get enough engagement so it doesn't attract new users, so it doesn't get enough engagement etc. 

By integrating hashtags, lemmy posts will be discoverable by those following those tags in microblogging which could lead them to reply, boost etc, something which will appear as new comments in lemmy. Since microblogging fediverse has an order of magnitude more users than lemmy does, the hope is that this will allow to kickstart a lot of more niche communities and deepen the interaction between the two mediums. 

My belief is that if we play to the advantages of Fediverse such as the seamless interaction between microblogging and threadiverse, we can not only become larger than our component parts, but it's also something that walled gardens like Reddit and Twitter cannot ever copy.

## Why not add this to lemmy itself

Currently Lemmy does not support tagging posts, and it [doesn't appear this might be added anytime soon](https://github.com/LemmyNet/lemmy/issues/317). As I'm not a Rust developer, I decided to take matters into my own hand in the only way I can, and created this python script to simulate the effect tags would have on lemmy post discoverability on microblogging.


## Adding your community to the tagginator

If you want your community monitored by this script, please either send a PR for `tags.py`, or contact me at @db0@lemmy.dbzer0.com or @db0@hachyderm.io. For each community, provide us with the tags that will be always added, and optionally a list of tags that will be used only is the post body contains them.

## Using the tagginator

Simply continue posting in that community as normal

If you want to use an optional tag in your post, simply add it somewhere in the post body, but ensure it exists in the tagginator's `tags.py`

If you want to avoid the tagginator tagging a specific post, then simply add the tag `#SkipTagginator` somewhere in the body.

## Running your own

To run this bot you need

* One lemmy bot account in your instance which we'll use to retrieve new posts and respond to reports against the bot
* One mastodon bot account which will tag the posts.

Put the details of both those accounts in `.env`. A sample `.env ` file has been put .env_template