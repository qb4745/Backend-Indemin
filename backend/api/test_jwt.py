import jwt
import datetime

# Clave secreta para firmar el token
JWT_SECRET_KEY = '06500650a'

# Crear el token
try:
    token = jwt.encode({
        'id_usuario': 1,
        'email': 'afenero@indemin.cl',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, JWT_SECRET_KEY, algorithm='HS256')
    print(token)
except Exception as e:
    print('Excepción atrapada:', str(e))
