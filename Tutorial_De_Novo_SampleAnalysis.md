# Tutorial 4 - De Novo Identification of Sample Groups #

A challenging bioinformatics challenge is the unbiased identification of both major and sub-populations of bulk or single-cell transcriptomes where no obvious reference gene or splice signatures exist. In addition, while transcriptome samples are often annotated as belonging to one or more groups, miss-classified samples or other unexpected covariants may also result in atypical variation that is difficult to characterize. A new set of algorithms have been implemented in AltAnalyze to identify the most coherent gene and sample expression signatures, prior to group comparison analyses. These new methods become particularly important when considering unknown single-cell RNA-Seq profiles and tumor subtype classification. In addition to gene expression, the software allows for the highly accurate and unbiased identification of highly similar alternative splicing signatures.

## Algorithms ##

There are currently two major methods implemented in the de novo sample discovery workflow:
  * Unsupervised: Correlation-based and expression filtering with outlier-removal
  * Supervised: Gene or gene-set (e.g., pathway) correlation-based

Both workflows initially exclude genes with low overall expression, low differential expression and ncRNAs. The expression thresholds are used defined. Differential expression is carried out between a set of the lowest and highest expressed measurements for a gene across samples (user defined cut point). The unsupervised workflow allows for the additional removal of cell-cycle associated gene-signatures. The unsupervised workflow only retains genes that are highly correlated to 10 or more genes, where the correlations in the gene-set are not driven exclusively by a single sample (unless single sample differences are examined). The supervised workflow accepts a single gene, multiple genes, or gene sets available from GO-Elite (e.g., disease ontologies, gene ontology, pathways, cell-type specific genes). When used, all genes in the supplied gene set are queried against the above described filter set, then correlated against all other genes to identify coherent signatures in the data. This analysis uses the user supplied correlation cutoffs and can be driven by outlier effects.

When supervised or unsupervised gene sets are identified, hierarchical clustering is performed to identify the major groups. A heatmap is returned by the software to evalute which grouping should be selected for group pairwise comparisons. The clustering algorithm to use can be selected from the main De Novo Sample Prediction Analysis interface.

## Input Data Formats ##

These analyses are compatible with all regular supported file formats in AltAnalyze (e.g., RNA-Seq bed, Affymetrix CEL, Agilent feature extraction, non-zero FPKM txt files). For RNA-Seq we recommend using either junction.bed files directly (TopHat, SpliceMap), TCGA junction\_expression.txt files and/or BedTools produced exon.bed files. For more information on these inputs, go http://code.google.com/p/altanalyze/wiki/Tutorial_AltExpression_RNASeq here].

## Running the De Novo Analysis ##

The instructions for running the de novo analysis are identical to all other workflow analyses in AltAnalyze (see [tutorials](https://code.google.com/p/altanalyze/wiki/Tutorials)), however, an additional step allows the user to discover groups by clustering.

  * Open the AltAnalyze program folder and open the file “AltAnalyze". In Windows, this file has the extension “.exe”. If you are working on a Linux machine or are having problems starting AltAnalyze, you can also start the program directly from the [code](source.md).
  * Follow the steps in Tutorials 1, 2 or 3, until you arrive at the [AltAnalyze: Assign CEL files to a Group](http://altanalyze.org/image/AssignCELGroups.jpg) interface. Select the option at the top of the menu named: Predict Groups from Unknown Sample Types.
  * Accept the default parameters listed or modify to customize. For supervised analyses, input space delimited (or Excel pasted lists) of standard accepted gene symbols for the species analyzed in the field "(optional) Enter genes to build clusters from". To display these genes in the larger cluster heatmap, enter these or other genes into the field "(optional) Display selected gene IDs in results". Alternatively, you can select a GeneSet to perform your supervised analysis upon.
  * If you wish to remove genes clusters that are driven by cell-cycle dependent changes, select the option: "(optional) Eliminate cell cycle effects". Please note, if the changes in your samples in your set are primarily distinct due to a major cell cycle effect (e.g., cancer), you may not want to add this option. However, you can try this and then simply re-run when prompted to see both possible outcomes.
  * Re-run the analysis when prompted using different gene sets,  different filtering parameters or different clustering options (e.g., HOPACH) to select the most informative sample groupings.

Note: For HOPACH clustering analyses, you must have the R programming environment installed. On Windows, R must also be registered in your system path. Once R is registered by your system, AltAnalyze can install any necessary packages locally in the AltAnalyze Config directory automatically.