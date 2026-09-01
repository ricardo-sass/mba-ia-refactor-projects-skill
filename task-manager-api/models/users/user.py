from __future__ import annotations

import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from shared.database import db
from shared.time import utc_now


LEGACY_MD5_PATTERN = re.compile(r"^[a-f0-9]{32}$")
VALID_ROLES = ("user", "admin", "manager")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    tasks = db.relationship("Task", back_populates="user")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, raw_password: str) -> None:
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        if self.has_legacy_password:
            legacy_hash = hashlib.md5(raw_password.encode()).hexdigest()
            return hmac.compare_digest(self.password, legacy_hash)
        return check_password_hash(self.password, raw_password)

    @property
    def has_legacy_password(self) -> bool:
        return bool(LEGACY_MD5_PATTERN.fullmatch(self.password or ""))

    def is_admin(self) -> bool:
        return self.role == "admin"
