from core.parsers.code_metrics_extractor import CodeMetricsExtractor
from core.parsers.delta_metrics_extractor import DeltaMetricsExtractor
from core.parsers.metrics_extractor_factory import MetricsExtractorFactory
from core.parsers.process_metrics_extractor import ProcessMetricsExtractor


def test_factory_returns_correct_extractor():
    jar = "libs/terraform_metrics-1.0.jar"

    code = MetricsExtractorFactory.get_extractor("codemetrics", jar)
    delta = MetricsExtractorFactory.get_extractor("delta", jar)
    process = MetricsExtractorFactory.get_extractor("process", jar)

    assert isinstance(code, CodeMetricsExtractor)
    assert isinstance(delta, DeltaMetricsExtractor)
    assert isinstance(process, ProcessMetricsExtractor)
