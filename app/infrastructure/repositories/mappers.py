"""Mapeadores entre entidades de dominio y modelos ORM."""

from __future__ import annotations

from app.domain.entities.compania import Compania
from app.domain.entities.empleado import Empleado
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.models import CompaniaModel, EmpleadoModel, UsuarioModel


def empleado_to_domain(model: EmpleadoModel) -> Empleado:
    return Empleado(
        id=model.id,
        nombre=model.nombre,
        apellido=model.apellido,
        correo=model.correo,
        cargo=model.cargo,
        salario=model.salario,
        compania_id=model.compania_id,
    )


def compania_to_domain(model: CompaniaModel, *, include_empleados: bool = False) -> Compania:
    empleados = [empleado_to_domain(empleado) for empleado in model.empleados] if include_empleados else []
    return Compania(
        id=model.id,
        nombre=model.nombre,
        direccion=model.direccion,
        telefono=model.telefono,
        fecha_creacion=model.fecha_creacion,
        empleados=empleados,
    )


def empleado_to_model(entity: Empleado) -> EmpleadoModel:
    return EmpleadoModel(
        id=entity.id,
        nombre=entity.nombre,
        apellido=entity.apellido,
        correo=entity.correo,
        cargo=entity.cargo,
        salario=entity.salario,
        compania_id=entity.compania_id,
    )


def compania_to_model(entity: Compania) -> CompaniaModel:
    return CompaniaModel(
        id=entity.id,
        nombre=entity.nombre,
        direccion=entity.direccion,
        telefono=entity.telefono,
        fecha_creacion=entity.fecha_creacion,
    )


def apply_empleado(entity: Empleado, model: EmpleadoModel) -> None:
    model.nombre = entity.nombre
    model.apellido = entity.apellido
    model.correo = entity.correo
    model.cargo = entity.cargo
    model.salario = entity.salario
    model.compania_id = entity.compania_id


def apply_compania(entity: Compania, model: CompaniaModel) -> None:
    model.nombre = entity.nombre
    model.direccion = entity.direccion
    model.telefono = entity.telefono
    model.fecha_creacion = entity.fecha_creacion


def usuario_to_domain(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.id,
        username=model.username,
        correo=model.correo,
        hashed_password=model.hashed_password,
        rol=model.rol,
        compania_id=model.compania_id,
    )


def usuario_to_model(entity: Usuario) -> UsuarioModel:
    return UsuarioModel(
        id=entity.id,
        username=entity.username,
        correo=entity.correo,
        hashed_password=entity.hashed_password,
        rol=entity.rol,
        compania_id=entity.compania_id,
    )

