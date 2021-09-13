from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from json import loads as jsonLoads


class UserAPITestCase(GraphQLTestCase):
    """
    Tests for user registration and 'me' query
    """

    USER = get_user_model()

    def setUp(self) -> None:
        user = self.USER(
            username='federico'
        )
        user.set_password('sup3rSecret_password')
        user.save()
        return super().setUp()

    def test_me_query(self):
        "Returns the username of logged user"
        user = self.USER.objects.get(id=1)
        token = get_token(user)
        headers = {
            'HTTP_AUTHORIZATION': f'GDjwt {token}'
        }
        query = '''
                query {
                    me {
                        username
                    }
                }
                '''

        response = self.query(query, headers=headers)
        self.assertResponseNoErrors(response)
        me = jsonLoads(response.content)['data']['me']['username']
        self.assertEqual(me, user.username)

    def test_create_user_mutation(self):
        query = '''
                mutation signUp(
                    $username: String!
                    $password: String!
                    $password2: String!
                ) {
                    signUp(
                        username: $username
                        password: $password
                        password2: $password2
                    ) {
                        user {
                            id
                            username
                        }
                        token
                    }
                }
                '''
        variables = {
            'username': 'new_user',
            'password': 'new_password123',
            'password2': 'new_password123'
        }
        response = self.query(query, variables=variables)
        data = jsonLoads(response.content)['data']['signUp']
        user = data['user']
        token = data['token']
        self.assertEqual(user['username'], 'new_user')
        self.assertEqual(int(user['id']), 2)
        self.assertIsNotNone(token)