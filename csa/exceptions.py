
class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class CartIsEmptyError(UserError):
    pass


class NoMoreOrdersError(UserError):
    pass
