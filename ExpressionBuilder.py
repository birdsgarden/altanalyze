import sys, string
import os.path
import unique
import statistics
import math
import reorder_arrays
import ExonArray
import export
import time
import BuildAffymetrixAssociations; reload(BuildAffymetrixAssociations)
dirfile = unique
py2app_adj = '/AltAnalyze.app/Contents/Resources/Python/site-packages.zip'

def filepath(filename):
    dir=os.path.dirname(dirfile.__file__)       #directory file is input as a variable under the main            
    fn=os.path.join(dir,filename)
    fn = string.replace(fn,py2app_adj,'')
    fn = string.replace(fn,'\\library.zip','') ###py2exe on some systems, searches for all files in the library file, eroneously
    return fn

def read_directory(sub_dir):
    dirfile = unique
    dir=os.path.dirname(dirfile.__file__)
    dir = string.replace(dir,py2app_adj,'')
    dir = string.replace(dir,'\\library.zip','')
    dir_list = os.listdir(dir + sub_dir); dir_list2 = []
    ###Code to prevent folder names from being included
    for entry in dir_list:
        if entry[-4:] == ".txt" or entry[-4:] == ".csv": dir_list2.append(entry)
    return dir_list2

################# Begin Analysis from parsing files

def calculate_expression_measures(expr_input_dir,expr_group_dir,expr_group,experiment_name,comp_group_dir,comp_group,probeset_db,annotate_db):
    print "Processing the expression file:",expr_input_dir
    fn1=filepath(expr_input_dir)
    x = 0; y = 0; d = 0
    global array_folds; array_folds={}
    for line in open(fn1,'rU').xreadlines():             
      data = cleanUpLine(line)
      if data[0] != '#':
        fold_data = string.split(data,'\t')
        arrayid = fold_data[0]
        ### differentiate data from column headers
        if x == 1:
            fold_data = fold_data[1:]; fold_data2=[]
            for fold in fold_data:
                if len(fold)>0:
                    try: fold = float(fold); fold_data2.append(fold)
                    except ValueError:
                        try:
                            null1, fold, null2 = string.split(fold,'"'); fold = float(fold); fold_data2.append(fold)
                        except ValueError: fold_data2.append(fold)
                else:
                    try: fold_data2.append(float(fold))
                    except ValueError: print fold, arrayid; kill #fold_data2.append(float(0))
            if expression_data_format == 'non-log':
                fold_data3=[] ###Convert numeric expression to log fold (need to add 1)
                for fold in fold_data2:
                    try: log_fold = math.log((float(fold)+1),2); fold_data3.append(log_fold)
                    except ValueError:  ###Not an ideal situation: Value is negative - Convert to zero
                        if float(fold)<0: math.log(1,2); fold_data3.append(log_fold)
                fold_data2 = fold_data3
            if (array_type == "AltMouse"):
                if arrayid in probeset_db: array_folds[arrayid] = fold_data2; y = y+1
            else: array_folds[arrayid] = fold_data2; y = y+1
        else: #only grab headers if it's the first row
            array_names = []; array_linker_db = {}; z = 0
            #array_names.append("Probesets")
            for entry in fold_data:
                try:
                    null1, headers, null2 = string.split(entry,'"')
                    if len(entry) > 0 and z != 0: array_names.append(headers)
                except ValueError:
                    if z != 0: array_names.append(entry)
                z += 1
            for array in array_names: #use this to have an orignal index order of arrays
                array = string.replace(array,'\r','') ###This occured once... not sure why
                array_linker_db[array] = d; d +=1
                #add this aftwards since these will also be used as index values
                #add this aftwards since these will also be used as index values
            x = 1
    print len(array_folds),"Array IDs imported...begining to calculate statistics for all group comparisons"
    expr_group_list,expr_group_db = importArrayGroups(expr_group_dir,array_linker_db)
    comp_group_list, comp_group_list2 = importComparisonGroups(comp_group_dir)

    #print array_names,expr_group_list,comp_group_list, dog
    global array_fold_headers; global statistics_summary_db; global stat_summary_names; global summary_filtering_stats; global raw_data_comp_headers; global raw_data_comps
    array_folds, array_fold_headers, statistics_summary_db, stat_summary_names, summary_filtering_stats,raw_data_comp_headers, raw_data_comps = reorder_arrays.reorder(array_folds,array_names,expr_group_list,comp_group_list,probeset_db,include_raw_data)
    #print array_fold_headers,dog
    return exportAnalyzedData(comp_group_list2,expr_group_db)

def importArrayGroups(expr_group_dir,array_linker_db):
    new_index_order = 0    
    expr_group_list=[]
    expr_group_db = {} #use when writing out data
    fn=filepath(expr_group_dir)
    for line in open(fn,'rU').xreadlines():             
        data = cleanUpLine(line)
        array_header,group,group_name = string.split(data,'\t')
        group = int(group)
        #compare new to original index order of arrays
        try: original_index_order = array_linker_db[array_header]
        except KeyError: print array_header, array_linker_db; kill
        entry = new_index_order, original_index_order, group, group_name
        expr_group_list.append(entry)
        new_index_order += 1 #add this aftwards since these will also be used as index values
        expr_group_db[str(group)] = group_name
    expr_group_list.sort() #sorting put's this in the original array order
    #print expr_group_list
    return expr_group_list,expr_group_db

def importComparisonGroups(comp_group_dir):
    comp_group_list=[]
    comp_group_list2=[]
    fn=filepath(comp_group_dir)
    for line in open(fn,'rU').xreadlines():            
        data = cleanUpLine(line)
        groups = string.split(data,'\t')
        groups2 = groups[0],groups[1] #as a list these would be unhashable
        comp_group_list.append(groups)
        comp_group_list2.append(groups2)
    return comp_group_list, comp_group_list2

def exportAnalyzedData(comp_group_list2,expr_group_db):
    if data_type == 'expression':
        new_file = expression_dataset_output_dir + 'DATASET-'+experiment_name+'.txt'
        data = export.createExportFile(new_file,expression_dataset_output_dir[:-1])
        x=0;y=0;z=0
        for arrayid in array_folds:
            if arrayid in annotate_db and arrayid in probeset_db: x = 1
            if arrayid in annotate_db: y = 1
            if arrayid in conventional_array_db: z = 1
            break
        if array_type == "exon":
            #annotate_db[gene] = symbol, definition,rna_processing
            #probeset_db[gene] = transcluster_string, exon_id_string
            title = "Ensembl_gene" +'\t'+ 'Definition' +'\t'+ 'Symbol' +'\t'+ 'Transcript_cluster_ids' +'\t'+ 'Constitutive_exons' +'\t'+ 'Constitutive_probesets' +'\t'+ 'RNA_processing/binding'
        elif x == 1:
            title = "Probesets" +'\t'+ 'Symbol' +'\t'+ 'Definition' +'\t'+ 'affygene' +'\t'+ 'exons' +'\t'+ 'probe_type_call' +'\t'+ 'ensembl' '\t'+ 'RNA_processing/binding'
        elif y==1:
             title = "Probesets" +'\t'+ 'Symbol' +'\t'+ 'Definition'
        elif array_type == "3'array":
             title = ['Probesets','Symbol','Definition','Ensembl_id','Entrez_id','Unigene_id','GO-Process','GO-Function','GO-Component','Pathway_info']
             title = string.join(title,'\t')
        else:
            title = "Probesets"
        for entry in array_fold_headers:
            title = title + '\t' + entry
        title = title +'\t'+ 'smallest-p' +'\t'+ 'largest fold' +'\t'+ '\n'
        data.write(title)
        for arrayid in array_folds:
            if array_type == "exon":
                try:
                    try: definition = annotate_db[arrayid][0]; symbol = annotate_db[arrayid][1]; rna_processing = annotate_db[arrayid][2]
                    except TypeError: print arrayid, annotate_db[arrayid]; kill
                except KeyError: definition=''; symbol=''; rna_processing=''
                trans_cluster = probeset_db[arrayid][0]
                exon_ids = probeset_db[arrayid][1]
                probesets = probeset_db[arrayid][2]
                data_val = arrayid +'\t'+ symbol +'\t'+ definition +'\t'+ trans_cluster +'\t'+ exon_ids +'\t'+ probesets +'\t'+ rna_processing
            elif arrayid in annotate_db and arrayid in probeset_db:
                symbol = annotate_db[arrayid][0]
                definition = annotate_db[arrayid][1]
                affygene = probeset_db[arrayid][0][0:-1]     #probeset_db[probeset] = affygene,exons,probe_type_call,ensembl
                exons = probeset_db[arrayid][1]
                probe_type_call = probeset_db[arrayid][2]
                ensembl = probeset_db[arrayid][3]
                rna_processing = annotate_db[arrayid][2]
                data_val = arrayid +'\t'+ definition +'\t'+ symbol +'\t'+ affygene +'\t'+ exons +'\t'+ probe_type_call +'\t'+ ensembl +'\t'+ rna_processing
            elif arrayid in annotate_db:
                definition = annotate_db[arrayid][0]
                symbol = annotate_db[arrayid][1]
                data_val = arrayid +'\t'+ definition +'\t'+ symbol
            elif array_type == "3'array":
                try:
                    ca = conventional_array_db[arrayid]
                    definition = ca.Description()
                    symbol = ca.Symbol()
                    ens = ca.EnsemblString()
                    entrez = ca.EntrezString()
                    unigene = ca.UnigeneString()
                    pathway_info = ca.PathwayInfo()
                    component = ca.GOComponentNames(); process = ca.GOProcessNames(); function = ca.GOFunctionNames()
                except KeyError: definition=''; symbol=''; ens=''; entrez=''; unigene=''; pathway_info=''; process=''; function=''; component=''
                data_val = [arrayid,symbol,definition,ens,entrez,unigene,process,function,component,pathway_info]
                data_val = string.join(data_val,'\t')
            else:
                data_val = arrayid
            for value in array_folds[arrayid]:
                data_val = data_val + '\t' + str(value)
            smallest_p = summary_filtering_stats[arrayid][0]
            largest_fold = summary_filtering_stats[arrayid][1]
            data_val = data_val +'\t'+ str(smallest_p) +'\t'+ str(largest_fold) +'\n'
            data.write(data_val)
        data.close()
        print "Full Dataset with statistics:",'DATASET-'+experiment_name+'.txt', 'written'
        
    if array_type == "AltMouse" or process_custom == 'yes':
        export_summary_stats = 'no'
        exportSplicingInput(species,array_type,expr_group_db,raw_data_comp_headers,comp_group_list2,raw_data_comps,export_summary_stats,data_type)
    return array_folds

def cleanUpLine(line):
    line = string.replace(line,'\n','')
    line = string.replace(line,'\c','')
    data = string.replace(line,'\r','')
    data = string.replace(data,'"','')
    return data

def exportSplicingInput(species,array_type,expr_group_db,raw_data_comp_headers,comp_group_list2,raw_data_comps,export_summary_stats,data_type):
    print "Writing AltAnalyze input...."
    ###Write individual comparison files out for AltAnalyze analysis
    AltAnalzye_input_dir = "AltExpression/pre-filtered/"+data_type+'/'
    array_type_name = 'Exon'
    if array_type == "AltMouse": array_type_name = "AltMouse"
    for comparison in comp_group_list2: #loop throught the list of comparisons
        group1 = comparison[0]
        group2 = comparison[1]
        group1_name = expr_group_db[group1]
        group2_name = expr_group_db[group2]
        
        if export_summary_stats == 'yes':
            file_name = species+'_'+array_type_name+'_'+ group1_name + '_vs_' + group2_name + '-ttest.txt'
            new_file = AltAnalzye_input_dir + file_name
            fn=filepath(new_file)
            data = open(fn,'w')
            try: avg_baseline_name = stat_summary_names[comparison][0]
            except TypeError: print stat_summary_names, comparison;dog
            ttest_name = stat_summary_names[comparison][3]
            exp_log_fold_name = stat_summary_names[comparison][1]
            title = "Probesets" +'\t'+ avg_baseline_name +'\t'+ ttest_name +'\t'+ 'null' +'\t'+ 'baseline_fold' +'\t'+ exp_log_fold_name + '\n'
            data.write(title)
            for key in statistics_summary_db:
                array_id = key[0]; comp = key[1]; comp =  str(comp[0]),str(comp[1])
                if comp == comparison: #if this is the comparison file we wish to generate
                    avg_baseline = statistics_summary_db[key][0]  #[avg1,log_fold,fold,ttest]
                    ttest = statistics_summary_db[key][3]
                    exp_log_fold = statistics_summary_db[key][1]
                    data_val = array_id +'\t'+ str(avg_baseline) +'\t'+ str(ttest) +'\t'+ '1' +'\t'+ '0' +'\t'+ str(exp_log_fold) + '\n'
                    data.write(data_val)
            data.close()
            print "Comparison statistics for",array_type_name,":",file_name, 'written'
            
        file_name2 = species+'_'+array_type_name+'_'+ group1_name + '_vs_' + group2_name + '.txt'
        new_file2 = AltAnalzye_input_dir + file_name2; altanalyze_files.append(file_name2)
        data2 = export.createExportFile(new_file2,AltAnalzye_input_dir[:-1])
        
        try: array_names = raw_data_comp_headers[comparison]
        except KeyError: print raw_data_comp_headers,dog
        title = 'Probesets'
        for array_name in array_names: title = title +'\t'+ array_name
        title = title + '\n'
        data2.write(title)
        for key in raw_data_comps:    
            array_id = key[0]
            comp = key[1]
            comp =  str(comp[0]),str(comp[1])
            data_val = array_id
            if comp == comparison: #if this is the comparison file we wish to generate
                for val in raw_data_comps[key]:
                    data_val = data_val +'\t'+ str(val)
                data_val = data_val + '\n'
                data2.write(data_val)
        data2.close()

def eliminate_redundant_dict_values(database):
    db1={}
    for key in database:
        list = unique.unique(database[key])
        list.sort()
        db1[key] = list
    return db1

def convert_to_list(database):
    db1=[]; db2=[]; temp_list=[]
    for key in database:
        list = database[key]
        #print key,list,dog  #32 [(2, 1.1480585565447154), (3, 0.72959188370731742), (0, 0.0), (1, -0.60729064216260165)]
        list.sort()
        temp_list=[]
        temp_list.append(key)
        for entry in list:
            avg_fold = entry[1]
            temp_list.append(avg_fold)
        #print temp_list, dog  #[32, 0.0, -0.60729064216260165, 1.1480585565447154, 0.72959188370731742]
        db1.append(temp_list)
    db1.sort()
    return db1

def avg(array):
    denominator = len(array)
    total = float(sum(array))
    average = total/denominator
    return average

def import_annotations(filename):
    fn=filepath(filename)
    annotation_dbase = {}
    for line in open(fn,'rU').xreadlines():
        try:
            data = cleanUpLine(line)
            try: probeset,definition,symbol,rna_processing = string.split(data,'\t')
            except ValueError:
                probeset,definition,symbol = string.split(data,'\t')
                rna_processing  = ''
            annotation_dbase[probeset] = definition, symbol,rna_processing
        except ValueError:
            continue
    return annotation_dbase

def import_altmerge(filename):
    probeset_db = {}
    constitutive_db = {}
    fn=filepath(filename)
    for line in open(fn,'rU').xreadlines():             
        probeset_data = cleanUpLine(line)
        probeset,affygene,exons,transcript_num,transcripts,probe_type_call,ensembl,block_exon_ids,block_structure,comparison_info = string.split(probeset_data,'\t')
        if probeset == "Probeset":
            continue
        else:
            probeset_db[probeset] = affygene,exons,probe_type_call,ensembl
            if probe_type_call == 'gene':
                try: constitutive_db[affygene].append(probeset)
                except KeyError: constitutive_db[affygene] = [probeset]
    return probeset_db, constitutive_db

def parse_custom_annotations(filename):
    custom_array_db = {}
    x=0
    fn=filepath(filename)
    for line in open(fn,'rU').xreadlines():
        data = cleanUpLine(line)
        array_data = data
        array_id,probeset,other = string.split(array_data,'\t')  #remove endline
        custom_array_db[array_id] = probeset,other
    print len(custom_array_db), "custom array entries process"
    return custom_array_db

def remoteExpressionBuilder(Species,Array_type,dabg_p,expression_threshold,avg_all_for_ss,Expression_data_format,manufacturer,constitutive_source,data_source,Include_raw_data):
  start_time = time.time()

  #def remoteExpressionBuilder():
  global species; global array_type ; species = Species; array_type = Array_type; global altanalyze_files
  global filter_by_dabg; filter_by_dabg = 'yes' ### shouldn't matter, since the program should just continue on without it
  global expression_data_format; global expression_dataset_output_dir; global AltAnalzye_input_dir; global data_type
  global conventional_array_db; global custom_array_db; global constitutive_db; global include_raw_data; global experiment_name
  global annotate_db; global probeset_db; global process_custom
  include_raw_data = Include_raw_data; expression_data_format = Expression_data_format
  data_type = 'expression' ###Default, otherwise is 'dabg'
  d = "core"; e = "extendend"; f = "full"; exons_to_grab = d ### Currently, not used by the program... intended as an option for ExonArrayAffymetrixRules full annotation (deprecated)
  
  ### Original options and defaults
  """
  dabg_p = 0.75; data_type = 'expression' ###used for expression analysis when dealing with AltMouse arrays
  a = "3'array"; b = "exon"; c = "AltMouse"; e = "custom"; array_type = c
  l = 'log'; n = 'non-log'; expression_data_format = l
  w = 'Agilent'; x = 'Affymetrix'; y = 'Ensembl'; z = 'default'; data_source = y; constitutive_source = z; manufacturer = x
  hs = 'Hs'; mm = 'Mm'; dr = 'Dr'; rn = 'Rn'; species = mm
  include_raw_data = 'yes'  
  expression_threshold = 70 ### Based on suggestion from BMC Genomics. 2006 Dec 27;7:325. PMID: 17192196, for hu-exon 1.0 st array
  avg_all_for_ss = 'no'  ###Default is 'no' since we don't want all probes averaged for the exon arrays
  """

  ct = 'count'; avg = 'average'; filter_method = avg
  filter_by_dabg = 'yes'

  print "Begining to Process the",species,array_type, 'dataset'
  expression_dataset_output_dir = "ExpressionOutput/"; AltAnalzye_input_dir = "pre-filtered/"
  
  process_custom = 'no'  
  if array_type == "custom": ### Keep this code for now, even though not currently used
      import_dir = '/AltDatabase/affymetrix/custom'
      dir_list = read_directory(import_dir)  #send a sub_directory to a function to identify all files in a directory
      for affy_data in dir_list:    #loop through each file in the directory to output results
          affy_data_dir = 'AltDatabase/affymetrix/custom/'+affy_data
          custom_array_db = parse_custom_annotations(affy_data_dir)
          array_type = a; process_custom = 'yes'
  if array_type == "AltMouse":
      print "Processing AltMouse splicing data"
      altmerge_db = "AltDatabase/"+species+'/'+array_type+'/'+ "MASTER-probeset-transcript.txt"
      probeset_db,constitutive_db = import_altmerge(altmerge_db)
      probe_annotation_file = "AltDatabase/"+species+'/'+ array_type+'/'+array_type+"_annotations.txt"
      annotate_db = import_annotations(probe_annotation_file)
      conventional_array_db = ""
  elif array_type == "3'array":
      process_go='yes';extract_go_names='yes';extract_pathway_names='yes'
      probeset_db = ""; annotate_db = ""
      constitutive_db = ""; conventional_array_db = {}
      affy_data_dir = 'AltDatabase/affymetrix'
      conventional_array_db = BuildAffymetrixAssociations.importAffymetrixAnnotations(affy_data_dir,species,process_go,extract_go_names,extract_pathway_names)
      print len(conventional_array_db), "Array IDs with annotations from Affymetrix annotation files imported."
  elif array_type == "exon":
      probeset_db = ""; annotate_db = ""; constitutive_db = ""; conventional_array_db = ""

  altanalyze_files = []; datasets_with_all_necessary_files=0
  #"""
  import_dir = '/ExpressionInput/'+array_type
  dir_list = read_directory(import_dir)  #send a sub_directory to a function to identify all files in a directory
  for expr_input in dir_list:    #loop through each file in the directory to output results
    if expr_input[0:4] == "exp.": # could be - "exp.", "grou", "comps" 
        experimental_input = expr_input[4:] # "rma-AltMouse.txt"
        experiment_name = expr_input[4:-4]
        expr_input_dir = "ExpressionInput/"+array_type+'/'+expr_input
        for expr_group in dir_list:
            if expr_group == "groups."+experimental_input: #hopach.out  + "put.es-complex.txt"
                expr_group_dir = "ExpressionInput/"+array_type+'/'+expr_group
                for comp_group in dir_list:
                    if comp_group == "comps."+experimental_input:
                        comp_group_dir = "ExpressionInput/"+array_type+'/'+comp_group
                        datasets_with_all_necessary_files +=1
                        if array_type == "exon":
                            probeset_db,annotate_db,comparison_filename_list = ExonArray.getAnnotations(expr_input_dir,dabg_p,exons_to_grab,data_source,manufacturer,constitutive_source,species,avg_all_for_ss,filter_by_dabg)
                            expr_input_dir = expr_input_dir[:-4]+'-steady-state.txt'
                            for file in comparison_filename_list: altanalyze_files.append(file)
                        """"if array_type == "AltMouse" and filter_by_dabg == 'yes':
                            import JunctionArray; analysis_method = 'rma'
                            JunctionArray.getAnnotations(expr_input_dir,dabg_p,species,analysis_method,constitutive_db)
                            if analysis_method == 'plier': expr_input_dir = string.replace(expr_input_dir,'plier','plier-filtered')
                            else: expr_input_dir = string.replace(expr_input_dir,'rma','rma-filtered')"""                             
                        array_fold_db = calculate_expression_measures(expr_input_dir,expr_group_dir,expr_group,experiment_name,comp_group_dir,comp_group,probeset_db,annotate_db)
                        if array_type == 'AltMouse':  ###For AltMouse, we specifically need to generate a dabg file with all data (similiar to what is done for the exon arrays specifically in the ExonArray module
                            stats_input = string.replace(expr_input,'exp.','stats.')
                            if stats_input in dir_list:
                                expr_input_dir = string.replace(expr_input_dir,'exp.','stats.')
                                data_type = 'dabg' ### when data_type is not expression, not 'DATASET' file is exported, but the same analysis is performed (exported to 'dabg' folder instead of expression)
                                null = calculate_expression_measures(expr_input_dir,expr_group_dir,expr_group,experiment_name,comp_group_dir,comp_group,probeset_db,annotate_db)

  annotate_db={}; probeset_db={}; constitutive_db={}; array_fold_db={}; array_folds={}; statistics_summary_db={}; raw_data_comps={}
  if datasets_with_all_necessary_files == 0:
      ###Thus no files were found with valid inputs for all file types
      print 'WARNING....No propperly named datasets were found. ExpressionBuilder requires that there are at least 3 files with the prefixes "exp.", "groups." and "comps.", with the following dataset name being identical with all three files.'
      print "...check these file names before running again."
      inp = sys.stdin.readline(); sys.exit()
  altanalyze_files = unique.unique(altanalyze_files) ###currently not used, since declaring altanalyze_files a global is problematic (not available from ExonArray... could add though)
  if array_type != "3'array":
      import FilterDabg
      FilterDabg.remoteRun(species,array_type,expression_threshold,filter_method,dabg_p,expression_data_format,altanalyze_files)
  else:
      end_time = time.time(); time_diff = int(end_time-start_time)
      print "Analyses finished in %d seconds" % time_diff
      print "Hit Enter/Return to exit AltAnalyze"
      inp = sys.stdin.readline(); sys.exit()

if __name__ == '__main__':
  """
  dabg_p = 0.75
  a = "3'array"; b = "exon"; c = "AltMouse"; e = "custom"; Array_type = c
  l = 'log'; n = 'non-log'; Expression_data_format = l
  w = 'Agilent'; x = 'Affymetrix'; y = 'Ensembl'; z = 'default'; data_source = y; constitutive_source = z; manufacturer = x
  hs = 'Hs'; mm = 'Mm'; dr = 'Dr'; rn = 'Rn'; Species = mm
  Include_raw_data = 'yes'  
  expression_threshold = 0 ### Based on suggestion from BMC Genomics. 2006 Dec 27;7:325. PMID: 17192196, for hu-exon 1.0 st array
  avg_all_for_ss = 'no'  ###Default is 'no' since we don't want all probes averaged for the exon arrays
  
  remoteExpressionBuilder(Species,Array_type,dabg_p,expression_threshold,avg_all_for_ss,Expression_data_format,manufacturer,constitutive_source,data_source,Include_raw_data)
  """