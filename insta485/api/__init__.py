"""Insta485 REST API."""

from insta485.api.app import get_api_v1, get_api_v1_posts,\
    get_api_v1_detailed_posts, delete_like, post_new_like,\
    post_new_comment, delete_comment

from insta485.api.invalid_usage import handle_invalid_usage
