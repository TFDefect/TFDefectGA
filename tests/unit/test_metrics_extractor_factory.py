from core.parsers.code_metrics_extractor import CodeMetricsExtractor
from core.parsers.delta_metrics_extractor import DeltaMetricsExtractor
from core.parsers.metrics_extractor_factory import MetricsExtractorFactory
from core.parsers.process_metrics_extractor import ProcessMetricsExtractor


def test_factory_returns_correct_extractor():
    """
    Teste la méthode `get_extractor` de la classe MetricsExtractorFactory pour vérifier
    qu'elle retourne les instances correctes des extracteurs de métriques.

    Scénario :
        - La méthode `get_extractor` est appelée avec différents types d'extracteurs :
          `codemetrics`, `delta`, et `process`.
        - Un chemin fictif pour le fichier JAR est fourni.

    Assertions :
        - Vérifie que l'extracteur retourné pour `codemetrics` est une instance de `CodeMetricsExtractor`.
        - Vérifie que l'extracteur retourné pour `delta` est une instance de `DeltaMetricsExtractor`.
        - Vérifie que l'extracteur retourné pour `process` est une instance de `ProcessMetricsExtractor`.

    Returns:
        None
    """
    jar = "libs/terraform_metrics-1.0.jar"

    code = MetricsExtractorFactory.get_extractor("codemetrics", jar)
    delta = MetricsExtractorFactory.get_extractor("delta", jar)
    process = MetricsExtractorFactory.get_extractor("process", jar)

    assert isinstance(code, CodeMetricsExtractor)
    assert isinstance(delta, DeltaMetricsExtractor)
    assert isinstance(process, ProcessMetricsExtractor)
