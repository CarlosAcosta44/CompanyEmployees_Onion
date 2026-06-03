"""
Servicio de aplicación: AuthService

Orquesta la autenticación, registro y generación de tokens JWT.
Garantiza el aislamiento de la lógica de seguridad bajo los puertos del dominio.
"""

from __future__ import annotations
import logging
import secrets
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt
from uuid import UUID

from app.application.dtos.auth_dto import UsuarioRegisterDTO, UsuarioLoginDTO, TokenDTO, UsuarioDTO
from app.domain.entities.usuario import Usuario
from app.domain.entities.refresh_token import RefreshToken
from app.domain.exceptions import ConflictError, EntityNotFoundError, AuthenticationError
from app.domain.interfaces.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class AuthService:
    """Caso de uso de gestión de usuarios y seguridad."""

    def __init__(
        self,
        uow: IUnitOfWork,
        jwt_secret_key: str,
        jwt_algorithm: str,
        jwt_access_token_expire_minutes: int,
    ) -> None:
        self._uow = uow
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm
        self._jwt_access_token_expire_minutes = jwt_access_token_expire_minutes

    async def registrar(self, dto: UsuarioRegisterDTO) -> UsuarioDTO:
        logger.info("[AuthService] Registrando nuevo usuario '%s'.", dto.userName)
        async with self._uow as uow:
            # Validar unicidad de username
            if await uow.usuarios.get_by_username(dto.userName):
                raise ConflictError(f"El nombre de usuario '{dto.userName}' ya está en uso.")

            # Validar unicidad de correo
            if await uow.usuarios.get_by_correo(dto.email):
                raise ConflictError(f"El correo electrónico '{dto.email}' ya está registrado.")

            # Validar compañía si se provee
            if dto.compania_id:
                compania = await uow.companias.get_by_id(dto.compania_id)
                if not compania:
                    raise EntityNotFoundError(f"La compañía con ID '{dto.compania_id}' no existe.")

            # Hashing con bcrypt
            password_bytes = dto.password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

            # Resolver rol (toma el primero de la lista, default USUARIO)
            rol = (dto.roles[0].upper() if dto.roles else "USUARIO")
            if rol not in ("ADMIN", "USUARIO"):
                rol = "USUARIO"

            usuario = Usuario(
                username=dto.userName,
                correo=dto.email,
                hashed_password=hashed_password,
                rol=rol,
                first_name=dto.firstName,
                last_name=dto.lastName,
                phone_number=dto.phoneNumber,
                ciudad=dto.ciudad,
                compania_id=dto.compania_id,
            )

            creado = await uow.usuarios.create(usuario)
            await uow.commit()
            logger.info("[AuthService] Usuario registrado con ID '%s'.", creado.id)
            return UsuarioDTO.model_validate(creado)

    async def login(self, dto: UsuarioLoginDTO) -> TokenDTO:
        logger.info("[AuthService] Intento de login para '%s'.", dto.userName)
        async with self._uow as uow:
            # Puede intentar por username o correo
            usuario = await uow.usuarios.get_by_username(dto.userName)
            if not usuario:
                usuario = await uow.usuarios.get_by_correo(dto.userName)

            # Verificación directa con bcrypt
            credenciales_validas = False
            if usuario:
                try:
                    password_bytes = dto.password.encode("utf-8")
                    hashed_bytes = usuario.hashed_password.encode("utf-8")
                    credenciales_validas = bcrypt.checkpw(password_bytes, hashed_bytes)
                except Exception:
                    credenciales_validas = False

            if not usuario or not credenciales_validas:
                logger.warning("[AuthService] Credenciales incorrectas para '%s'.", dto.userName)
                raise AuthenticationError("Credenciales de acceso incorrectas.")

            # Generar access token
            expires_delta = timedelta(minutes=self._jwt_access_token_expire_minutes)
            expire = datetime.now(timezone.utc) + expires_delta

            claims = {
                "sub": str(usuario.id),
                "username": usuario.username,
                "rol": usuario.rol,
                "ciudad": usuario.ciudad,
                "compania_id": str(usuario.compania_id) if usuario.compania_id else None,
                "exp": expire,
            }

            token = jwt.encode(
                claims,
                self._jwt_secret_key,
                algorithm=self._jwt_algorithm,
            )

            # Generar y almacenar refresh token
            rt_val = secrets.token_urlsafe(64)
            rt_expires = datetime.now(timezone.utc) + timedelta(days=7)
            
            rt = RefreshToken(token=rt_val, expires_at=rt_expires, usuario_id=usuario.id)
            await uow.refresh_tokens.create(rt)
            
            await uow.commit()

            logger.info("[AuthService] Tokens generados para el usuario '%s'.", usuario.username)
            return TokenDTO(accessToken=token, refreshToken=rt_val, token_type="bearer")

    async def refresh(self, refresh_token_str: str) -> TokenDTO:
        """Valida el refresh token y emite un nuevo par de tokens."""
        logger.info("[AuthService] Intento de refresh token.")
        async with self._uow as uow:
            rt = await uow.refresh_tokens.get_by_token(refresh_token_str)
            if not rt or not rt.is_valid:
                raise AuthenticationError("Token de refresco inválido o expirado.")
                
            usuario = await uow.usuarios.get_by_id(rt.usuario_id)
            if not usuario:
                raise EntityNotFoundError("El usuario asociado al token no existe.")
                
            # Revocar el token actual (rotación)
            rt.revocar()
            
            # Generar nuevo access token
            expires_delta = timedelta(minutes=self._jwt_access_token_expire_minutes)
            expire = datetime.now(timezone.utc) + expires_delta

            claims = {
                "sub": str(usuario.id),
                "username": usuario.username,
                "rol": usuario.rol,
                "ciudad": usuario.ciudad,
                "compania_id": str(usuario.compania_id) if usuario.compania_id else None,
                "exp": expire,
            }

            new_access_token = jwt.encode(
                claims,
                self._jwt_secret_key,
                algorithm=self._jwt_algorithm,
            )
            
            # Generar nuevo refresh token
            new_rt_val = secrets.token_urlsafe(64)
            new_rt_expires = datetime.now(timezone.utc) + timedelta(days=7)
            
            new_rt = RefreshToken(token=new_rt_val, expires_at=new_rt_expires, usuario_id=usuario.id)
            await uow.refresh_tokens.create(new_rt)
            
            await uow.commit()
            return TokenDTO(accessToken=new_access_token, refreshToken=new_rt_val, token_type="bearer")

    async def logout(self, usuario_id: UUID) -> None:
        """Cierra sesión revocando todos los refresh tokens activos."""
        async with self._uow as uow:
            await uow.refresh_tokens.revoke_by_usuario(usuario_id)
            await uow.commit()

    async def obtener_perfil(self, usuario_id: str) -> UsuarioDTO:
        async with self._uow as uow:
            usuario = await uow.usuarios.get_by_id(UUID(usuario_id))
            if not usuario:
                raise EntityNotFoundError("El usuario no existe.")
            return UsuarioDTO.model_validate(usuario)

    async def obtener_perfil(self, usuario_id: str) -> UsuarioDTO:
        from uuid import UUID
        async with self._uow as uow:
            usuario = await uow.usuarios.get_by_id(UUID(usuario_id))
            if not usuario:
                raise EntityNotFoundError("El usuario no existe.")
            return UsuarioDTO.model_validate(usuario)
