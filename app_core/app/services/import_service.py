import csv
import io
from typing import Dict, List, Optional, Tuple

from app.models.asset import Asset


class ImportResult:
    def __init__(self):
        self.imported: List[Dict] = []
        self.errors: List[Dict] = []

    def to_dict(self) -> Dict:
        return {
            "imported_count": len(self.imported),
            "errors_count": len(self.errors),
            "imported": self.imported,
            "errors": self.errors,
        }


class ImportService:
    REQUIRED_FIELDS = ["name", "asset_type", "confidentiality", "integrity", "availability"]
    VALID_TYPES = ["hardware", "software", "datos", "personas", "procesos", "otro"]

    @classmethod
    def validate_csv_headers(cls, headers: List[str]) -> Tuple[bool, str]:
        missing = [f for f in cls.REQUIRED_FIELDS if f not in headers]
        if missing:
            return False, f"Campos requeridos faltantes: {', '.join(missing)}"
        return True, ""

    @classmethod
    def validate_asset_data(cls, row: Dict, row_num: int) -> Optional[str]:
        name = row.get("name", "").strip()
        if not name:
            return f"Fila {row_num}: El nombre es requerido"

        asset_type = row.get("asset_type", "").strip().lower()
        if asset_type not in cls.VALID_TYPES:
            return f"Fila {row_num}: Tipo de activo inválido '{asset_type}'. Valores válidos: {', '.join(cls.VALID_TYPES)}"

        try:
            c = int(row.get("confidentiality", 1))
            i = int(row.get("integrity", 1))
            a = int(row.get("availability", 1))
            if not (1 <= c <= 5):
                return f"Fila {row_num}: Confidencialidad debe estar entre 1 y 5"
            if not (1 <= i <= 5):
                return f"Fila {row_num}: Integridad debe estar entre 1 y 5"
            if not (1 <= a <= 5):
                return f"Fila {row_num}: Disponibilidad debe estar entre 1 y 5"
        except ValueError:
            return f"Fila {row_num}: Los valores CID deben ser numéricos"

        return None

    @classmethod
    def import_csv(cls, csv_content: str, assessment_id: Optional[str] = None) -> ImportResult:
        result = ImportResult()

        try:
            reader = csv.DictReader(io.StringIO(csv_content))
        except Exception as e:
            result.errors.append({"row": 0, "error": f"Error al leer CSV: {str(e)}"})
            return result

        headers = reader.fieldnames or []
        valid, error_msg = cls.validate_csv_headers(headers)
        if not valid:
            result.errors.append({"row": 0, "error": error_msg})
            return result

        for row_num, row in enumerate(reader, start=2):
            error = cls.validate_asset_data(row, row_num)
            if error:
                result.errors.append({"row": row_num, "data": row, "error": error})
                continue

            try:
                asset = Asset.create(
                    name=row["name"].strip(),
                    asset_type=row["asset_type"].strip().lower(),
                    description=row.get("description", "").strip(),
                    confidentiality=int(row["confidentiality"]),
                    integrity=int(row["integrity"]),
                    availability=int(row["availability"]),
                    assessment_id=assessment_id,
                )
                result.imported.append(asset.to_dict())
            except Exception as e:
                result.errors.append({"row": row_num, "data": row, "error": str(e)})

        return result

    @classmethod
    def get_csv_template(cls) -> str:
        fields = cls.REQUIRED_FIELDS + ["description"]
        return ",".join(fields) + "\n" + "Servidor de base de datos,datos,3,4,4,Servidor que contiene la BD de producción\n"

    @classmethod
    def get_required_fields(cls) -> List[str]:
        return cls.REQUIRED_FIELDS.copy()


