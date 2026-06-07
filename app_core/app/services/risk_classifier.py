class RiskClassifier:
    CRITICAL_THRESHOLD = 17
    HIGH_THRESHOLD = 10
    MEDIUM_THRESHOLD = 5

    ZONE_RED_THRESHOLD = 12

    @classmethod
    def classify_risk(cls, risk_value: float) -> str:
        if risk_value >= cls.CRITICAL_THRESHOLD:
            return "critical"
        elif risk_value >= cls.HIGH_THRESHOLD:
            return "high"
        elif risk_value >= cls.MEDIUM_THRESHOLD:
            return "medium"
        return "low"

    @classmethod
    def get_risk_zone(cls, risk_value: float) -> str:
        if risk_value >= cls.ZONE_RED_THRESHOLD:
            return "red"
        elif risk_value >= cls.MEDIUM_THRESHOLD:
            return "orange"
        return "green"

    @classmethod
    def is_unacceptable(cls, risk_value: float) -> bool:
        return risk_value >= cls.ZONE_RED_THRESHOLD

    @classmethod
    def get_zone_color(cls, zone: str) -> str:
        colors = {
            "red": "#f44336",
            "orange": "#ff9800",
            "green": "#4caf50"
        }
        return colors.get(zone, "#9e9e9e")

    @classmethod
    def get_risk_color(cls, risk_value: float) -> str:
        classification = cls.classify_risk(risk_value)
        colors = {
            "critical": "#f44336",
            "high": "#ff9800",
            "medium": "#ffc107",
            "low": "#4caf50"
        }
        return colors.get(classification, "#9e9e9e")

    @classmethod
    def get_risk_level_label(cls, risk_value: float) -> str:
        classification = cls.classify_risk(risk_value)
        labels = {
            "critical": "Crítico",
            "high": "Alto",
            "medium": "Medio",
            "low": "Bajo"
        }
        return labels.get(classification, "Desconocido")

    @classmethod
    def get_strategy_label(cls, strategy: str) -> str:
        labels = {
            "mitigate": "Mitigar",
            "accept": "Aceptar",
            "transfer": "Transferir"
        }
        return labels.get(strategy, strategy)

    @classmethod
    def get_strategy_color(cls, strategy: str) -> str:
        colors = {
            "mitigate": "#f44336",
            "accept": "#ff9800",
            "transfer": "#2196f3"
        }
        return colors.get(strategy, "#9e9e9e")