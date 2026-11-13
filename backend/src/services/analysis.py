from .validation import validate_config
from .counts import panel_counts
from .fleiss import fleiss
from .bootstrap import row_bootstrap
from .fingerprint import fingerprint
from .cores import groups_from_rows,grouping_summary

def analyze(study,specimens,votes,config):
 validate_config(config);rows=panel_counts(study,specimens,votes);matrix=[r['counts'] for r in rows];result=fleiss(matrix)
 for row,P in zip(rows,result['item_agreement']):row['agreement']=P
 groups=groups_from_rows(rows);summary=grouping_summary(rows,groups)
 bootstrap=row_bootstrap(matrix,config['bootstrap_repeats'],config['seed'],rows=rows)
 return {**result,'source_study':study,'categories':study['categories'],'raters':study['raters'],'items':rows,'grouping':summary,'bootstrap':bootstrap,'fingerprint':fingerprint(study,specimens,votes,config),'interpretation':'Agreement relative to empirical category marginals, not accuracy against a gold standard. Fixed complete three-person panel. Point estimate uses every original specimen row equally; bootstrap resamples whole cores (carrying all their specimens) when core fields exist, otherwise whole iid specimens; never single votes or new raters.'}
