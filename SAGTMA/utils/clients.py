import re
import datetime

from SAGTMA.models import Client, ProjectDetail, Vehicle, db
from SAGTMA.utils import events
from SAGTMA.utils.validations import validate_id, validate_name


class ClientError(ValueError):
    pass


# ========== Validaciones ==========
def validate_phone_number(phone_number: str) -> str:
    """
    Lanza una excepción si el número telefónico no es válido.

    El formato del un número de teléfono válido es cualquiera de los siguientes:
     - Comienza con 58, +58, 0058, 0 no tener comienzo.
     - Seguido de 10 dígitos.
     - Puede contener paréntesis, espacios, puntos o guiones como separadores.

    Retorna el número de teléfono transformado a un formato estándar:
     - Comienza con +58.
     - Seguido de 10 dígitos.
     - No contiene separadores.
    """
    # Remueve espacios, guiones, paréntesis y puntos del número
    table = str.maketrans("", "", ".- ()[]")
    phone_number = phone_number.translate(table)

    # Expresión regular para validar número telefónicos
    regex = r"((\+|00)?58|0)?\d{10}"
    if not re.fullmatch(regex, phone_number):
        raise ClientError("El número de teléfono ingresado no tiene un formato válido")

    # Regulariza el número para guardarlo en la base de datos
    if phone_number.startswith("00"):
        phone_number = phone_number.replace("00", "+")
    elif phone_number.startswith("0"):
        phone_number = phone_number.replace("0", "+58")
    elif phone_number.startswith("58"):
        phone_number = f"+{phone_number}"
    elif not phone_number.startswith("+58"):
        phone_number = f"+58{phone_number}"

    return phone_number


def validate_email(email: str):
    """Lanza una excepción si el correo electrónico no es válido"""
    # Expresión regular para validar correos electrónicos
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if not re.fullmatch(regex, email):
        raise ClientError("El correo electrónico ingresado es inválido")


def validate_birthdate(birthdate: datetime.date):
    """
    Lanza una excepción si la fecha de nacimiento no es válida

    La edad mínima es 18 años.
    La edad máxima es 100 años.
    """
    today = datetime.date.today()
    age = (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )

    if age < 18:
        raise ClientError("La edad mínima para registrarse es 18 años")
    elif age > 100:
        raise ClientError("La edad máxima para registrarse es 100 años")


# ========== Registro ==========
def register_client(
    id_number: str,
    names: str,
    surnames: str,
    birthdate: str,
    phone_number: str,
    email: str,
    address: str,
):
    """
    Crea y anade un cliente en la base de datos.

    Lanza una excepción ClientError si hubo algún error.
    """
    # Elimina espacios al comienzo y final del input del form
    names = names.strip()
    surnames = surnames.strip()
    phone_number = phone_number.strip()
    email = email.strip()
    address = address.strip()

    if not all([id_number, names, surnames, birthdate, phone_number, email, address]):
        raise ClientError("Todos los campos son obligatorios")

    # Chequea si los campos son válidos
    id_number = validate_id(id_number, ClientError)
    validate_name(names, ClientError)
    validate_name(surnames, ClientError)
    phone_number = validate_phone_number(phone_number)
    validate_email(email)

    if len(address) > 120:
        raise ClientError(
            "La descripción del problema no puede tener más de 120 caracteres"
        )

    # Verifica si ya existe un cliente con el mismo id_number
    stmt = db.select(Client).where(Client.id_number == id_number)
    if db.session.execute(stmt).first():
        raise ClientError("Ya existe un cliente con la misma cédula")

    # Convert birthdate a tipo Date usando la libreria datetime
    y, m, d = birthdate.split("-")
    y, m, d = int(y), int(m), int(d)
    birthdate_t = datetime.date(y, m, d)

    # Chequea si la fecha de nacimiento es válida
    validate_birthdate(birthdate_t)

    # Crea el cliente en la base de datos
    new_client = Client(
        id_number, names, surnames, birthdate_t, phone_number, email, address
    )

    db.session.add(new_client)

    # Registra el evento en la base de datos
    events.add_event(
        "Detalles de los Clientes", f"Agregar cliente '{new_client.id_number}'"
    )


# ========== Edicion de datos ==========
def edit_client(
    client_id: int,
    id_number: str,
    names: str,
    surnames: str,
    birthdate: str,
    phone_number: str,
    email: str,
    address: str,
):
    """
    Modifica los datos de un cliente en la base de datos

    Lanza una excepción ClientError si hubo algún error.
    """
    # Elimina espacios al comienzo y final del input del form
    names = names.strip()
    surnames = surnames.strip()
    phone_number = phone_number.strip()
    email = email.strip()
    address = address.strip()

    # Verifica que todos los campos estén llenos
    if not all([id_number, names, surnames, birthdate, phone_number, email, address]):
        raise ClientError("Todos los campos son obligatorios")

    # Chequea si los campos son válidos
    id_number = validate_id(id_number, ClientError)
    validate_name(names, ClientError)
    validate_name(surnames, ClientError)
    phone_number = validate_phone_number(phone_number)
    validate_email(email)

    if len(address) > 120:
        raise ClientError(
            "La descripción del problema no puede tener más de 120 caracteres"
        )

    # Verifica si ya existe un cliente con el mismo id_number
    stmt = (
        db.select(Client)
        .where(Client.id_number == id_number)
        .where(Client.id != client_id)
    )
    if db.session.execute(stmt).first():
        raise ClientError("Ya existe un cliente con la misma cédula")

    # Selecciona el cliente con el id indicado y verifica que exista
    stmt = db.select(Client).where(Client.id == client_id)
    client_query = db.session.execute(stmt).first()
    if not client_query:
        raise ClientError("El cliente indicado no existe")
    edited_client = client_query[0]

    # Convert birthdate a tipo Date usando la libreria datetime
    y, m, d = birthdate.split("-")
    y, m, d = int(y), int(m), int(d)
    birthdate_t = datetime.date(y, m, d)

    validate_birthdate(birthdate_t)

    # Actualiza los datos del cliente
    edited_client.id_number = id_number
    edited_client.names = names
    edited_client.surnames = surnames
    edited_client.birthdate = birthdate_t
    edited_client.phone_number = phone_number
    edited_client.email = email
    edited_client.address = address

    # Registra el evento en la base de datos
    events.add_event("Detalles de los Clientes", f"Modificar cliente '{id_number}'")


# ========== Eliminacion de clientes ==========
def delete_client(client_id: int):
    """
    Elimina un cliente de la base de datos

    Lanza una excepción ClientError si hubo algún error.
    """
    # Selecciona el cliente con el id indicado y verifica que exista
    stmt = db.select(Client).where(Client.id == client_id)
    client_query = db.session.execute(stmt).first()
    if not client_query:
        raise ClientError("El cliente indicado no existe")
    client = client_query[0]

    # Verifica que el cliente no tenga un vehículo asociado a un detalle de proyecto
    stmt = (
        db.select(ProjectDetail)
        .join(ProjectDetail.vehicle)
        .join(Vehicle.owner)
        .where(Client.id == client_id)
    )
    if db.session.execute(stmt).first():
        raise ClientError(
            "El cliente no puede ser eliminado porque tiene un vehículo asociado a un detalle de proyecto"
        )

    # Elimina el cliente de la base de datos
    db.session.delete(client)

    # Registra el evento en la base de datos
    events.add_event(
        "Detalles de los Clientes", f"Eliminar cliente '{client.id_number}'"
    )
