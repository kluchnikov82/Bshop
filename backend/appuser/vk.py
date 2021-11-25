"""
VK authentification class
"""
from social_core.backends.oauth import BaseOAuth2
from social_core.backends.vk import vk_api
from social_core.exceptions import AuthException, AuthTokenRevoked


class MyVKOAuth2(BaseOAuth2):  # pylint: disable=abstract-method
    """
    VKOAuth2 authentication backend
    """
    name = 'vk-oauth2'
    ID_KEY = 'id'
    AUTHORIZATION_URL = 'http://oauth.vk.com/authorize'
    ACCESS_TOKEN_URL = 'https://oauth.vk.com/access_token'
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [('id', 'id'), ('expires_in', 'expires')]

    def get_user_details(self, response):
        """Return user details from VK.com account"""
        fullname, first_name, last_name = self.get_user_names(
            first_name=response.get('first_name'),
            last_name=response.get('last_name'))
        return {
            'username': response.get('screen_name'),
            'email': response.get('email', ''),
            'fullname': fullname,
            'first_name': first_name,
            'last_name': last_name
        }

    def user_data(self, access_token, *args, **kwargs):
        """
        Loads user data from service
        """
        request_data = [
            'first_name', 'last_name', 'screen_name', 'nickname', 'photo'
        ] + self.setting('EXTRA_DATA', [])

        fields = ','.join(set(request_data))
        data = vk_api(self, 'users.get', {
            'access_token': access_token,
            'fields': fields,
        })

        if data and data.get('error'):
            error = data['error']
            msg = error.get('error_msg', 'Unknown error')
            if error.get('error_code') == 5:
                raise AuthTokenRevoked(self, msg)
            raise AuthException(self, msg)

        if data:
            data = data.get('response')[0]
            data['user_photo'] = data.get('photo')  # Backward compatibility
        return data or {}

    def do_auth(self, access_token, response=None, *args, **kwargs):  # pylint: disable=arguments-differ,keyword-arg-before-vararg
        """
        Аутентификация по токену
        """
        response = response or {}
        data = self.user_data(access_token)
        data['access_token'] = access_token
        if 'expires_in' in response:
            data['expires'] = response['expires_in']
        kwargs.update({'backend': self, 'response': data})
        return self.strategy.authenticate(*args, **kwargs)
