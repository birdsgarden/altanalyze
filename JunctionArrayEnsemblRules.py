import sys, string
import os.path
import unique
import ExonArrayEnsemblRules
import EnsemblImport
import shutil
import JunctionArray
dirfile = unique
py2app_adj = '/AltAnalyze.app/Contents/Resources/Python/site-packages.zip'

def filepath(filename):
    dir=os.path.dirname(dirfile.__file__)       #directory file is input as a variable under the main            
    fn=os.path.join(dir,filename)
    fn = string.replace(fn,py2app_adj,'')
    fn = string.replace(fn,'\\library.zip','') ###py2exe on some systems, searches for all files in the library file, eroneously
    return fn
    
def read_directory(sub_dir):
    dir=os.path.dirname(dirfile.__file__)
    dir = string.replace(dir,py2app_adj,'')
    dir = string.replace(dir,'\\library.zip','')
    dir_list = os.listdir(dir + sub_dir)
    return dir_list
        
def cleanUpLine(line):
    line = string.replace(line,'\n','')
    line = string.replace(line,'\c','')
    data = string.replace(line,'\r','')
    data = string.replace(data,'"','')
    return data

def eliminate_redundant_dict_values(database):
    db1={}
    for key in database:
        list = unique.unique(database[key])
        list.sort()
        db1[key] = list
    return db1

def importCriticalExonLocations(species,array_type,ensembl_exon_db):
    ###ensembl_exon_db[(geneid,chr,strand)] = [[E5,exon_info]] #exon_info = (exon_start,exon_stop,exon_id,exon_annot)
    ###ensembl_probeset_db[geneid,chr,strand].append(probeset_data) #probeset_data = [start,stop,probeset_id,exon_class,transcript_cluster_id]
    gene_info_db = {}
    for (ens_geneid,chr,strand) in ensembl_exon_db: gene_info_db[ens_geneid] = chr,strand
    filename = 'AltDatabase/'+species+'/'+array_type+'/'+array_type+'_critical_exon_locations.txt'
    ensembl_probeset_db={}
    fn=filepath(filename); key_db = {}; x = 0
    for line in open(fn,'rU').xreadlines():
        data = cleanUpLine(line)
        if x == 0: x = 1
        else:
            k=0
            array_geneid,exonid,ens_geneid,start,stop,gene_start,gene_stop,exon_seq = string.split(data,'\t')
            probeset_id = array_geneid+':'+exonid
            if test == 'yes':
                if array_geneid in test_cluster: k=1
            else: k = 1
            if k==1:
                if ens_geneid in gene_info_db:
                    chr,strand = gene_info_db[ens_geneid]
                    probeset_data = [start,stop,probeset_id,'core',array_geneid]
                    try: ensembl_probeset_db[ens_geneid,'chr'+chr,strand].append(probeset_data)
                    except KeyError: ensembl_probeset_db[ens_geneid,'chr'+chr,strand] = [probeset_data]
    print len(ensembl_probeset_db), "Genes inlcuded in",array_type,"location database"
    return ensembl_probeset_db

def getAnnotations(Species,array_type):
    """Annotate Affymetrix exon array data using files Ensembl data (sync'ed to genome release)."""
    global species; species = Species; global test; global test_cluster
    test = 'yes'; test_cluster = ['G7022992']

    global ensembl_exon_db; global ensembl_exon_db; global exon_clusters; global exon_region_db
    ensembl_exon_db,ensembl_annot_db,exon_clusters,intron_clusters,exon_region_db,intron_retention_db,ucsc_splicing_annot_db = EnsemblImport.getEnsemblAssociations(species,test)
    ensembl_probeset_db = importCriticalExonLocations(species,array_type,ensembl_exon_db) ###Get Pre-computed genomic locations for critical exons
    ensembl_probeset_db = ExonArrayEnsemblRules.annotateExons(ensembl_probeset_db,exon_clusters,ensembl_exon_db,exon_region_db,intron_retention_db,intron_clusters,ucsc_splicing_annot_db); constitutive_gene_db={}
    ExonArrayEnsemblRules.exportEnsemblLinkedProbesets(ensembl_probeset_db,constitutive_gene_db,species)
    print "\nCritical exon data exported coordinates, exon associations and splicing annotations exported..."
    
    ### Change filenames to reflect junction array type
    export_filename = 'AltDatabase/'+species+'/exon/'+species+'_Ensembl_probesets.txt'; ef=filepath(export_filename)
    export_replacement = string.replace(export_filename,'_probe','_'+array_type+'_probe'); er=filepath(export_replacement); shutil.copyfile(ef,er); os.remove(ef) ### Copy file to a new name
    export_filename = 'AltDatabase/'+species+'/'+array_type+'/'+species+'_Ensembl_'+array_type+'_probesets.txt'

    ### Export full exon seqeunce for probesets/critical exons to replace the original incomplete sequence (used for miRNA analyses)
    #JunctionArray.reAnnotateCriticalExonSequences(species,array_type)
    
if __name__ == '__main__':
    dirfile = unique
    m = 'Mm'; h = 'Hs'
    Species = m
    array_type = 'AltMouse' ###In theory, could be another type of junciton or combination array

    getAnnotations(Species,array_type)
    
    