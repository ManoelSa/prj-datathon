import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
APP_USER = os.getenv("APP_USER")
APP_PASS = os.getenv("APP_PASS")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Modelo de dados para o token.
    """
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token de acesso JWT com um tempo de expiração.

    Args:
        data (dict): Dicionário contendo os dados a serem codificados no token.
        expires_delta (Optional[timedelta], optional): Tempo de expiração do token. 
            Se não fornecido, o padrão é 15 minutos.

    Returns:
        str: O token JWT codificado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str):
    """
    Autentica um usuário verificando as credenciais.

    Args:
        username (str): Nome de usuário.
        password (str): Senha do usuário.

    Returns:
        Union[dict, bool]: Retorna um dicionário com o nome de usuário se a autenticação for bem-sucedida,
            caso contrário, retorna False.
    """
    if username == APP_USER and password == APP_PASS:
        return {"username": username}
    return False

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Valida e decodifica o token JWT para obter o usuário atual.

    Args:
        token (str, optional): Token JWT fornecido via dependência OAuth2PasswordBearer.

    Raises:
        HTTPException: Se o token for inválido ou as credenciais não puderem ser validadas.

    Returns:
        TokenData: Um objeto contendo os dados do token (nome de usuário).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    return token_data
