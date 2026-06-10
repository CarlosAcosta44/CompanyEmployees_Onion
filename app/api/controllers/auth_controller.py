"""
Controlador de Autenticación.
Expone los endpoints REST para registro, login y perfil de usuarios.
"""

from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, Response, Request
from uuid import UUID

from app.application.dtos.auth_dto import UsuarioRegisterDTO, UsuarioLoginDTO, TokenDTO, UsuarioDTO
from app.application.services.auth_service import AuthService
from app.api.dependencies import get_auth_service, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioDTO, status_code=201)
async def registro(dto: UsuarioRegisterDTO, service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] POST /api/auth/registro")
    return await service.registrar(dto)


@router.post("/login", response_model=TokenDTO)
async def login(dto: UsuarioLoginDTO, response: Response, service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] POST /api/auth/login")
    token = await service.login(dto)
    response.set_cookie(
        key="access_token",
        value=token.accessToken,
        httponly=True,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=token.refreshToken,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return token

@router.post("/refresh", response_model=TokenDTO)
async def refresh(request: Request, response: Response, service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] POST /api/auth/refresh")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Refresh token missing in cookies.")
        
    token = await service.refresh(refresh_token)
    response.set_cookie(
        key="access_token",
        value=token.accessToken,
        httponly=True,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=token.refreshToken,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return token


@router.post("/logout")
async def logout(request: Request, response: Response, service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] POST /api/auth/logout")
    
    user = getattr(request.state, "user", None)
    if user and "sub" in user:
        try:
            await service.logout(UUID(user["sub"]))
        except Exception:
            pass
        
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Sesión cerrada exitosamente."}


@router.get("/perfil", response_model=UsuarioDTO)
async def perfil(user: dict = Depends(get_current_user), service: AuthService = Depends(get_auth_service)):
    logger.info("[AuthController] GET /api/auth/perfil")
    return await service.obtener_perfil(user["sub"])

