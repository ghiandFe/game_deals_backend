import graphene
import graphql_jwt

from deals import schema as dealsSchema
from users import schema as usersSchema


class Query(usersSchema.Query, dealsSchema.Query, graphene.ObjectType):
    pass


class Mutation(usersSchema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)