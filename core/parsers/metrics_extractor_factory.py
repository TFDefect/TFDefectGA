from core.parsers.DeltaMetricsExtractor import DeltaMetricsExtractor
from infrastructure.adapters.external_tools.terra_metrics import TerraMetricsAdapter

class MetricsExtractorFactory:
    @staticmethod
    def get_extractor(extractor_type: str, output_path: str):
        if extractor_type == "delta":
            return DeltaMetricsExtractor(output_path)
        elif extractor_type == "terrametrics":
            return TerraMetricsAdapter(output_path)
        #elif extractor_type == "process":
            #return ProcessMetricsExtractor(output_path)
        else:
            raise ValueError(f"Type d'extracteur inconnu : {extractor_type}")