from datetime import datetime

from dateutil.relativedelta import relativedelta

SECRET = "secret:"


class AuthenticationProvider:
    def __init__(self, jwt_token: str):
        self.jwt_token = jwt_token.replace(SECRET, "")
        self.expiry = datetime.now() - relativedelta(years=1)

    @classmethod
    def create(cls, jwt_token: str):
        return cls(jwt_token)

    def get_access_token(self):
        return self.jwt_token, self.expiry
