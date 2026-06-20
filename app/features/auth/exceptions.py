# features/auth/exceptions.py
class AuthError(Exception):
    """Excepción base para todos los errores del feature auth."""
    pass

class InvalidRefreshTokenError(AuthError):
    """El hash no coincide con ningún token en BD."""
    pass

class InvalidAccessokenException(AuthError):
    """El hash no coincide con ningún token en BD."""
    pass

class RevokedAccessokenException(AuthError):
    """No ha sido proporcionado un access token para ser revocado"""
    pass

class RevokedRefreshTokenException(AuthError):
    """No ha sido proporcionado un refresh token para ser revocado"""
    pass

class ExpiredRefreshTokenError(AuthError):
    """El token expiró por tiempo (expires_at)."""
    pass

class RefreshTokenReuseDetectedError(AuthError):
    """El token ya había sido revocado previamente."""
    pass

class InvalidAccessTokenError(AuthError):
    """JWT inválido o expirado."""
    pass

class UserNotFoundError(AuthError):
    """El usuario no existe en la base de datos."""
    pass

class UserAlreadyExistsError(AuthError):
    """El usuario ya existe en la base de datos."""
    pass

class InsufficientPermissionsError(AuthError):
    """El usuario no tiene permisos para realizar la acción."""
    pass
