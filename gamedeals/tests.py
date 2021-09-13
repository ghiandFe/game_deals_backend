from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from json import loads as jsonLoads


class TokenAuthTestCase(GraphQLTestCase):
    """
    Test to verify authentication functions
    """

    USER = get_user_model()

    def setUp(self):
        user = self.USER(
            username='federico'
        )
        user.set_password('sup3rSecret_password')
        user.save()
        return super().setUp()

    def test_login_and_verify_jwt_token(self):
        """
        This test send a login request via GraphQL (tokenAuth)
        and check the username returned by token verification
        """
        response = self.query(
            '''
            mutation TokenAuth(
                $username: String!
                $password: String!
            ) {
                tokenAuth(
                    username: $username
                    password: $password
                ) {
                    token
                }
            }
            ''',
            variables = {
                'username': 'federico',
                'password': 'sup3rSecret_password'
            }
        )
        token = jsonLoads(response.content)['data']['tokenAuth']['token']
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

        response = self.query(
            '''
            mutation VerifyToken(
                $token: String!
            ) {
                verifyToken(
                    token: $token
                ) {
                    payload
                }
            }
            ''',
            variables = {
                'token': token,
            }
        )
        data = jsonLoads(response.content)['data']
        username = data['verifyToken']['payload']['username']
        self.assertIsNotNone(username)
        self.assertEqual(username, 'federico')