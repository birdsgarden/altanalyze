# Instructions for Obtaining RNASeq Input Files #

**_Please Note:_** We are actively working on ways to better integrate existing RNA-seq alignment strategies into AltAnalyze. Recommendations to our [support desk](ContactUs.md) are always welcome.

### Downloading Sample FASTQ Data ###

You are welcome to try with your own FASTQ data, as this is typically easiest for most users rather than downloading large datasets. For optimal junction analysis results, we recommend >50nt reads, however, we have achieved acceptable results from 35nt reads. If you currently do not have your own data, example files and download instructions can be found [here](DownloadFASTQ.md).

### Using TopHat and Bowtie ###

Currently, we recommend two pipelines for producing input data for AltAnalyze: 1) TopHat and 2) BioScope. TopHat should work with most all RNA-seq datasets, while BioScope is compatible with ABI SOLiD data. As TopHat is open-source and runs on typical hardware configurations, this solution will be more appropriate for most users.

For TopHat, junction BED files can be easily obtained using simple command-line arguments to TopHat, once Bowtie and indexed genome files have been downloaded. In addition to aligning junctions, exon read counts can be obtained from the resulting accepted\_hits.bam file written to the same folder as the junction BED results, using [BEDTools](BEDTools.md). For example Instructions on obtaining exon and junction expression files (BED format), click [here](BAMtoBED.md).

### Using BioScope ###

Details on BioScope usage can be found [here](http://www3.appliedbiosystems.com/cms/groups/global_marketing_group/documents/generaldocuments/cms_074971.pdf). Once result files are produced, AltAnalyze will accept the junction and exon reads files produced from this pipeline as input. Prior to import, the extension of these two files must be changed to .tab in order for AltAnalyze to recognize these from other text files. To ensure the exon and junction files for each sample are properly matched, make sure that the exon and junction file have the same name, followed by a double underscore, followed by a distinguishing annotation. For example:

|`Cancer_s1__canonical-junction.tab`|
|:----------------------------------|
|`Cancer_s1__noncanonical-junction.tab`|
|`Cancer_s1__exon.tab`|
|`Wt_s1__canonical-junction.tab`|
|`Wt_s1__noncanonical-junction.tab`|
|`Wt_s1__exon.tab`|