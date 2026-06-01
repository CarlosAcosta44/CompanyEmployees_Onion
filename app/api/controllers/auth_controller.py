"""
Controlador de Autenticación.
Expone los endpoints REST para registro, login y perfil de usuarios.
"""

from __future__ import annotations
import logging
from fastapi import APIRouter, Depends

from app.application.dtos.auth_dto import UsuarioRegisterDTO, UsuarioLoginDTO, TokenDTO, UsuarioDTO
from app.application.services.auth_service import AuthService
from app.api.dependencies import get_auth_service, get_current_user
from fastapi.security import OAuth2PasswordRequestForm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioDTO, status_code=201)
async def registro(dto: UsuarioRegisterDTO, service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] POST /api/auth/registro")
    return await service.registrar(dto)


@router.post("/login", response_model=TokenDTO)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] POST /api/auth/login")
    dto = UsuarioLoginDTO(correo=form_data.username, password=form_data.password)
    return await service.login(dto)


@router.get("/perfil", response_model=UsuarioDTO)
async def perfil(user: dict = Depends(get_current_user), service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] GET /api/auth/perfil")
    return await service.obtener_perfil(user["sub"])
