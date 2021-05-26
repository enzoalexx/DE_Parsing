import scrapy
from scrapy.http import HtmlResponse
from instagramparser.items import UserFollowerItem
from urllib.parse import urlencode
from copy import deepcopy
import json
import re


class InstagramSpider(scrapy.Spider):

    # ��������� �����, �����������, ��������
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    users_for_parse = []
    login_link = 'https://www.instagram.com/accounts/login/ajax/'
    login = 'login'
    password = 'hash_password'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'  # hash ��� ��������� �����������
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'  # hash ��� ��������� ��������

    # �������� ����� ��� ����������� �� HTML
    @staticmethod
    def fetch_csrf_token(text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # �������� id ������������ �� HTML, ��� ������ ������� ����� ���������� username
    @staticmethod
    def fetch_user_id(text, username):
        matched = re.search(f'\"id\":\"(\\d+)\",\"username\":\"{username}\"', text)
        return int(matched.group(1))

    # �������� ������ ��� ������������ �� ��������� ����� ������
    @staticmethod
    def get_user_full_name(text):
        full_name = text.split('@')[0]
        if full_name.endswith('('):
            full_name = full_name[:-2]
        return full_name

    # ����� ����������� �������� ������ ������������� ��� ��������
    def __init__(self, users_list=None):
        if users_list:
            if isinstance(users_list, str):
                # ���� �������� ������ ������������ �������, �� ������ ������
                self.users_for_parse = [users_list]
            elif isinstance(users_list, list):
                # �������� ������ �������������
                self.users_for_parse = users_list

    # � ����� ������ ����������� ������� �������� ������
    def parse(self, response: HtmlResponse):
        # �� ������� �������� � HTML ���� csrf-token
        csrf_token = self.fetch_csrf_token(response.text)
        # ��������� ����� ��� �����������
        yield scrapy.FormRequest(
            self.login_link,
            method='POST',
            callback=self.auth_user_page,
            formdata={'username': self.login, 'enc_password': self.password},
            headers={'X-CSRFToken': csrf_token}
        )

    # ���� �������� ���� ����� ����������� (�������� ��������������� ������������)
    def auth_user_page(self, response: HtmlResponse):
        # ��������� ����� ����� �����������
        j_data = json.loads(response.text)
        if j_data['authenticated']:
            # ���� �� �������������, ������� ����� �������
            for user in self.users_for_parse:
                # ��������� �� �������� ������������
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'user_name': user}
                )

    # ���� �� �������� ������������, �������� ����� �������
    def user_data_parse(self, response: HtmlResponse, user_name):
        user_id = self.fetch_user_id(response.text, user_name)  # id ������������
        user_full_name = self.get_user_full_name(
            response.xpath('//meta[@property="og:title"]/@content').extract_first()  # ������ ��� ������������
        )
        user_photo_url = response.xpath('//meta[@property="og:image"]/@content').extract_first()  # ���� ������������
        # ������ �������� �����������
        variables = {
            'id': user_id,
            'include_reel': True,
            'fetch_mutual': True,
            'first': 24}
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'user_name': user_name,
                       'user_id': user_id,
                       'user_full_name': user_full_name,
                       'user_photo_url': user_photo_url,
                       'variables': deepcopy(variables)}
        )
        # ������ �������� ��������
        variables = {
            'id': user_id,
            'include_reel': True,
            'fetch_mutual': False,
            'first': 24}
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
            url_following,
            callback=self.user_following_parse,
            cb_kwargs={'user_name': user_name,
                       'user_id': user_id,
                       'user_full_name': user_full_name,
                       'user_photo_url': user_photo_url,
                       'variables': deepcopy(variables)}
        )

    # ������� ���� �����������
    def user_followers_parse(self, response: HtmlResponse, user_name, user_id, user_full_name, user_photo_url, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            # ���� ��������� �������� (������ �����������).
            # ����� ��������� ��� �������� ��������� ������
            variables['fetch_mutual'] = False
            variables['first'] = 12
            variables['after'] = page_info['end_cursor']
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'user_name': user_name,
                           'user_id': user_id,
                           'user_full_name': user_full_name,
                           'user_photo_url': user_photo_url,
                           'variables': deepcopy(variables)}
            )
        # ������� �����������
        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            follower_item = UserFollowerItem(
                user_id=user_id,
                user_name=user_name,
                user_full_name=user_full_name,
                user_photo_url=user_photo_url,
                follower_id=int(follower['node']['id']),
                follower_name=follower['node']['username'],
                follower_full_name=follower['node']['full_name'],
                follower_photo_url=follower['node']['profile_pic_url']
            )
            yield follower_item

    # ������� ���� ��������
    def user_following_parse(self, response: HtmlResponse, user_name, user_id, user_full_name, user_photo_url, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            # ���� ��������� �������� (������ ��������).
            # ����� ��������� ��� �������� ��������� ������
            variables['first'] = 12
            variables['after'] = page_info['end_cursor']
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_following,
                callback=self.user_following_parse,
                cb_kwargs={'user_name': user_name,
                           'user_id': user_id,
                           'user_full_name': user_full_name,
                           'user_photo_url': user_photo_url,
                           'variables': deepcopy(variables)}
            )
        # ������� ��������
        followings = j_data.get('data').get('user').get('edge_follow').get('edges')
        for follow in followings:
            follower_item = UserFollowerItem(
                user_id=int(follow['node']['id']),
                user_name=follow['node']['username'],
                user_full_name=follow['node']['full_name'],
                user_photo_url=follow['node']['profile_pic_url'],
                follower_id=user_id,
                follower_name=user_name,
                follower_full_name=user_full_name,
                follower_photo_url=user_photo_url
            )
            yield follower_item