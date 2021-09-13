from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    @login_required
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('User not logged in!')
        return user


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(self, info, username, password, password2):
        if password == password2:
            user = get_user_model()(
                username=username
            )
            user.set_password(password)
            user.save()
            token = get_token(user=user)
            return CreateUser(user=user, token=token)
        raise Exception('Passwords do not match')


class Mutation(graphene.ObjectType):
    sign_up = CreateUser.Field()