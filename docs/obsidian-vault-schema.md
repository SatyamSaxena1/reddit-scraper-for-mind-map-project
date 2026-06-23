# Obsidian Vault Schema

Generated vault folders:

- `Posts/`
- `Subreddits/`
- `Authors/`
- `Topics/`
- `Media/`
- `Indexes/`

Post notes use frontmatter with:

- `type`
- `reddit_id`
- `title`
- `subreddit`
- `author`
- `score`
- `created_utc`
- `permalink`
- `url`
- `domain`
- `saved_source`
- `fetched_at`
- `tags`
- `topics`
- `media`
- `comment_count`

Wiki links connect posts to entity notes:

- `[[subreddit - MachineLearning]]`
- `[[reddit user - example_author]]`
- `[[topic - embeddings]]`

Entity-note filenames intentionally match their wiki-link titles so Obsidian can resolve backlinks without aliases.
