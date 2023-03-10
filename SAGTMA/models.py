import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Role(db.Model):
    """Modelo de rol."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    users = db.relationship("User", backref="role")

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Role<{self.name}>"


user_project = db.Table(
    "user_project",
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), nullable=False),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), nullable=False),
    db.UniqueConstraint("user_id", "project_id"),
)


class User(db.Model):
    """Modelo de usuario."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    names = db.Column(db.String(50), nullable=False)
    surnames = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)

    # Relación n:n entre usuarios y proyectos
    projects = db.relationship(
        "Project", secondary=user_project, backref=db.backref("assigned_to")
    )

    # Relación 1:n entre usuarios y eventos
    events = db.relationship("Event", backref="user", cascade="all, delete-orphan")

    def __init__(
        self, username: str, names: str, surnames: str, password: str, role: Role
    ):
        self.username = username
        self.names = names
        self.surnames = surnames
        self.password = password
        self.role = role

    def __repr__(self) -> str:
        return f"User<{self.username}: {self.names} {self.surnames}, {self.role.name}>"


class Project(db.Model):
    """Modelo de proyecto."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def __init__(self, description: str, start_date, end_date):
        self.description = description
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self) -> str:
        return f'Project<{self.description}: {self.start_date} - {self.end_date}, {"Activo" if self.active else "Inactivo"}>'


class Event(db.Model):
    """Modelo de evento."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    module = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    time = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)

    def __init__(self, user: User, module: str, description: str):
        self.user = user
        self.module = module
        self.description = (
            description if len(description) <= 80 else f"{description[:77]}..."
        )

    def __repr__(self) -> str:
        return f"Event<{self.user.username}: {self.module} - {self.type}>"


class Client(db.Model):
    """Modelo de cliente."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_number = db.Column(db.String(10), unique=True, nullable=False)
    names = db.Column(db.String(50), nullable=False)
    surnames = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    vehicles = db.relationship("Vehicle", backref="owner", cascade="all, delete-orphan")

    def __init__(
        self,
        id_number: str,
        names: str,
        surnames: str,
        birthdate,
        phone_number: str,
        email: str,
        address: str,
    ):
        self.id_number = id_number
        self.names = names
        self.surnames = surnames
        self.birthdate = birthdate
        self.phone_number = phone_number
        self.email = email
        self.address = address

    def __repr__(self) -> str:
        return f"Client<{self.id_number}: {self.names} {self.surnames}>"


class Vehicle(db.Model):
    """Modelo de vehículo."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    license_plate = db.Column(db.String(10), unique=True, nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    body_number = db.Column(db.String(20), nullable=False)
    engine_number = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    problem = db.Column(db.String(120), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)

    def __init__(
        self,
        license_plate: str,
        brand: str,
        model: str,
        year: int,
        body_number: str,
        engine_number: str,
        color: str,
        problem: str,
    ):
        self.license_plate = license_plate
        self.brand = brand
        self.model = model
        self.year = year
        self.body_number = body_number
        self.engine_number = engine_number
        self.color = color
        self.problem = problem

    def __repr__(self) -> str:
        return f"Vehicle<{self.license_plate}: {self.brand} {self.model}>"
