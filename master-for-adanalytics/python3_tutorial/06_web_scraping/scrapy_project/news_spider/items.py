# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    """뉴스 아이템"""
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    published_date = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    images = scrapy.Field()
    links = scrapy.Field()
    metadata = scrapy.Field()
    word_count = scrapy.Field()
    reading_time = scrapy.Field()
    language = scrapy.Field()
    crawled_at = scrapy.Field()


class CommentItem(scrapy.Item):
    """댓글 아이템"""
    article_url = scrapy.Field()
    comment_id = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    likes = scrapy.Field()
    replies = scrapy.Field()
    is_reply = scrapy.Field()
    parent_id = scrapy.Field()