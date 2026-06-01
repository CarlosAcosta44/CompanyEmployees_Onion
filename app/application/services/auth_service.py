"""
Servicio de aplicación: AuthService

Orquesta la autenticación, registro y generación de tokens JWT.
Garantiza el aislamiento de la lógica de seguridad bajo los puertos del dominio.
"""

from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt

from app.application.dtos.auth_dto import UsuarioRegisterDTO, UsuarioLoginDTO, TokenDTO, UsuarioDTO
from app.domain.entities.usuario import Usuario
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
        logger.info("[AuthService] Registrando nuevo usuario '%s'.", dto.username)
        async with self._uow as uow:
            # Validar unicidad de username
            if await uow.usuarios.get_by_username(dto.username):
                raise ConflictError(f"El nombre de usuario '{dto.username}' ya está en uso.")

            # Validar unicidad de correo
            if await uow.usuarios.get_by_correo(dto.correo):
                raise ConflictError(f"El correo electrónico '{dto.correo}' ya está registrado.")

            # Validar compañía si se provee
            if dto.compania_id:
                compania = await uow.companias.get_by_id(dto.compania_id)
                if not compania:
                    raise EntityNotFoundError(f"La compañía con ID '{dto.compania_id}' no existe.")

            # Hashing directo con bcrypt
            password_bytes = dto.password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

            usuario = Usuario(
                username=dto.username,
                correo=dto.correo,
                hashed_password=hashed_password,
                rol=dto.rol,
                compania_id=dto.compania_id,
            )

            creado = await uow.usuarios.create(usuario)
            await uow.commit()
            logger.info("[AuthService] Usuario registrado con ID '%s'.", creado.id)
            return UsuarioDTO.model_validate(creado)

    async def login(self, dto: UsuarioLoginDTO) -> TokenDTO:
        logger.info("[AuthService] Intento de login para '%s'.", dto.correo)
        async with self._uow as uow:
            usuario = await uow.usuarios.get_by_correo(dto.correo)
            
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
                logger.warning("[AuthService] Credenciales incorrectas para '%s'.", dto.correo)
                raise AuthenticationError("Credenciales de acceso incorrectas.")

            # Generar claims del token JWT
            expires_delta = timedelta(minutes=self._jwt_access_token_expire_minutes)
            expire = datetime.now(timezone.utc) + expires_delta

            claims = {
                "sub": str(usuario.id),
                "username": usuario.username,
                "rol": usuario.rol,
                "compania_id": str(usuario.compania_id) if usuario.compania_id else None,
                "exp": expire,
            }

            token = jwt.encode(
                claims,
                self._jwt_secret_key,
                algorithm=self._jwt_algorithm,
            )

            logger.info("[AuthService] Token de acceso generado para el usuario '%s'.", usuario.username)
            return TokenDTO(access_token=token, token_type="bearer")

    async def obtener_perfil(self, usuario_id: str) -> UsuarioDTO:
        from uuid import UUID
        async with self._uow as uow:
            usuario = await uow.usuarios.get_by_id(UUID(usuario_id))
            if not usuario:
                raise EntityNotFoundError("El usuario no existe.")
            return UsuarioDTO.model_validate(usuario)
