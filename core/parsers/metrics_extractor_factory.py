from core.parsers.code_metrics_extractor import CodeMetricsExtractor
from core.parsers.delta_metrics_extractor import DeltaMetricsExtractor
from core.parsers.process_metrics_extractor import ProcessMetricsExtractor


class MetricsExtractorFactory:
    """
    Factory permettant de récupérer l'extracteur de métriques en fonction du type spécifié.
    """

    @staticmethod
    def get_extractor(extractor_type: str, jar_path: str):
        """
        Retourne l'instance d'extracteur de métriques correspondant au type demandé.

        Args:
            extractor_type (str): Type de l'extracteur à utiliser (codemetrics, delta, process).
            jar_path (str): Chemin vers le fichier JAR de TerraMetrics (ignoré pour process).

        Returns:
            Instance de l'extracteur de métriques.
        """
        if extractor_type == "codemetrics":
            return CodeMetricsExtractor(jar_path)
        elif extractor_type == "delta":
            return DeltaMetricsExtractor(jar_path)
        elif extractor_type == "process":
            return ProcessMetricsExtractor()
        else:
            raise ValueError(f"Type d'extracteur inconnu : {extractor_type}")
