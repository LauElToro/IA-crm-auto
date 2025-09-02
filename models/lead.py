from pydantic import BaseModel
from typing import Optional

class LeadData(BaseModel):
    nombre: Optional[str]
    apellido: Optional[str]
    email: Optional[str]
    telefono: Optional[str]
    empresa: Optional[str]
    cargo: Optional[str]
    industria: Optional[str]
    bio: Optional[str]
