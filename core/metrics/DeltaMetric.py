# Liste de toutes les métriques Terraform à traiter
TERRAFORM_METRICS = [
    "numComparisonOperators", "avgComparisonOperators", "maxComparisonOperators",
    "numConditions", "avgConditions", "maxConditions", "numLogiOpers", "avgLogiOpers",
    "maxLogiOpers", "numDynamicBlocks", "numNestedBlocks", "numFunctionCall",
    "avgFunctionCall", "maxFunctionCall", "numParams", "avgParams", "maxParams",
    "numHereDocs", "avgHereDocs", "numLinesHereDocs", "avgLinesHereDocs",
    "maxLinesHereDocs", "numIndexAccess", "avgIndexAccess", "maxIndexAccess",
    "numLiteralExpression", "numStringValues", "sumLengthStringValues",
    "avgLengthStringValues", "maxLengthStringValues", "numLoops", "avgLoops",
    "maxLoops", "numMathOperations", "avgMathOperations", "maxMathOperations",
    "avgMccabeCC", "sumMccabeCC", "maxMccabeCC", "numMetaArg", "numObjects",
    "avgObjects", "maxObjects", "numElemObjects", "avgElemObjects", "maxElemObjects",
    "numReferences", "avgReferences", "maxReferences", "numVars", "avgNumVars",
    "maxNumVars", "numSplatExpressions", "avgSplatExpressions", "maxSplatExpressions",
    "numTemplateExpression", "avgTemplateExpression", "textEntropyMeasure",
    "minAttrsTextEntropy", "maxAttrsTextEntropy", "avgAttrsTextEntropy", "numTokens",
    "minTokensPerAttr", "maxTokensPerAttr", "avgTokensPerAttr", "numTuples",
    "avgTuples", "maxTuples", "numElemTuples", "avgElemTuples", "maxElemTuples",
    "depthOfBlock", "loc", "nloc", "numAttrs", "numExplicitResourceDependency",
    "avgDepthNestedBlocks", "maxDepthNestedBlocks", "minDepthNestedBlocks",
    "numImplicitDependentResources", "numImplicitDependentData",
    "numImplicitDependentModules", "numImplicitDependentProviders",
    "numImplicitDependentLocals", "numImplicitDependentVars",
    "numImplicitDependentEach", "numEmptyString", "numWildCardSuffixString",
    "numStarString", "numDebuggingFunctions", "numDeprecatedFunctions"
]


class DeltaMetric:
    """
    Classe pour calculer les métriques delta entre la version actuelle d'un bloc
    et sa version précédente.
    """

    def __init__(self, current_block, previous_blocks=None):
        """
        Initialise l'objet DeltaMetric.
        
        Args:
            current_block (dict): Le bloc actuel avec ses métriques
            previous_blocks (list, optional): Liste des versions précédentes du bloc
        """
        self.current_block = current_block
        
        # Si les identifiants ne sont pas présents, utiliser block et block_name
        if "block_identifiers" not in self.current_block:
            block_id = f"{self.current_block.get('block', 'unknown')}-{self.current_block.get('block_name', '')}"
            self.current_block["block_identifiers"] = block_id
            
        self.block_before_change = None
        
        # Rechercher le bloc précédent correspondant
        if previous_blocks:
            matching_blocks = [
                block for block in previous_blocks 
                if block.get("block_identifiers") == self.current_block.get("block_identifiers")
            ]
            if matching_blocks:
                self.block_before_change = matching_blocks[-1]

    def diff_code_metrics(self):
        """
        Calcule les différences entre les métriques du bloc actuel et du bloc précédent.
        
        Returns:
            dict: Dictionnaire des métriques avec suffixe _delta
        """
        delta_code_metrics = {}
    
        for metric in TERRAFORM_METRICS:
            if metric in self.current_block:
                new_value = self.current_block.get(metric, 0)
                delta_code_metrics[metric] = new_value
                
                # Calculer delta différemment selon l'existence d'un bloc précédent
                if self.block_before_change:
                    old_value = self.block_before_change.get(metric, 0)
                    delta_code_metrics[f"{metric}_delta"] = new_value - old_value
                else:
                    delta_code_metrics[f"{metric}_delta"] = new_value
        
        # Conserver les identifiants
        for id_field in ["block", "block_name", "defect_prediction", "block_id", "block_identifiers"]:
            if id_field in self.current_block:
                delta_code_metrics[id_field] = self.current_block[id_field]
                
        return delta_code_metrics

    def resume_delta_metrics(self):
        """
        Calcule et renvoie toutes les métriques delta.
        
        Returns:
            dict: Dictionnaire combiné de toutes les métriques delta
        """
        return self.diff_code_metrics()