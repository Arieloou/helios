# features/user/exceptions.py

class AuthError(Exception):
    """Excepción base para todos los errores del feature auth."""
    pass

class UserNotFoundError(AuthError):
    """El usuario no existe en la base de datos."""
    pass

class UserAlreadyExistsError(AuthError):
    """El usuario ya existe en la base de datos."""
    pass

class EmailAlreadyExistsError(AuthError):
    """El email ya existe en la base de datos."""
    pass