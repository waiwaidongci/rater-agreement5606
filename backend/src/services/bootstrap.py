from collections import Counter
import numpy as np
from .fleiss import fleiss,UndefinedKappa
from .cores import groups_from_rows

def row_bootstrap(counts,repeats,seed,rows=None):
 matrix=np.asarray(counts,dtype=int);N=len(matrix);rng=np.random.default_rng(seed);records=[];values=[];failures=Counter();groups=groups_from_rows(rows) if rows is not None else []
 cluster=bool(groups);K=len(groups)
 for i in range(repeats):
  if cluster:
   group_indices=rng.integers(0,K,size=K);indices=np.concatenate([groups[int(g)]['specimen_indices'] for g in group_indices]);sampled_cores=[groups[int(g)]['core'] for g in group_indices];duplicates={}
   for g in group_indices:duplicates[groups[int(g)]['core']]=duplicates.get(groups[int(g)]['core'],0)+1
   record={'repeat':i,'sampled_cores':sampled_cores,'core_multiplicity':duplicates,'drawn_core_count':K,'distinct_core_count':len(set(sampled_cores)),'drawn_specimen_count':int(len(indices)),'sample_indices':indices.tolist()}
  else:
   indices=rng.integers(0,N,size=N);record={'repeat':i,'sample_indices':indices.tolist()}
  sample=matrix[indices]
  try:
   result=fleiss(sample);value=result['kappa'];values.append(value);record.update(kappa=value,valid=True,reason=None)
  except UndefinedKappa as error:
   reason=str(error);failures[reason]+=1;record.update(kappa=None,valid=False,reason=reason)
  records.append(record)
 edges=np.linspace(-1,1,21);histogram={'edges':edges.tolist(),'counts':np.histogram(values,bins=edges)[0].tolist()}
 valid=len(values);eligible=valid*10>=repeats*9;interval=np.quantile(values,[.025,.975],method='linear').tolist() if eligible else None
 return {'seed':seed,'requested_repeats':repeats,'valid_repeats':valid,'invalid_repeats':repeats-valid,'valid_fraction':valid/repeats,'invalid_reasons':dict(failures),'interval':interval,'confidence_level':.95,'interval_status':'reported' if eligible else 'insufficient_valid','interval_reason':'有效比例≥90%，有效重复的2.5%/97.5%线性percentile经验区间' if eligible else '有效重复少于90%，不报告经验区间','quantile_method':'numpy.quantile(method=linear)','histogram':histogram,'replicates':records,'resampling_unit':'core_cluster' if cluster else 'specimen','source_specimen_count':N,'source_core_count':K if cluster else None,'interpretation':'Percentile bootstrap conditional on the fixed rater panel. With core grouping, resamples whole cores (all their specimens) so non-independent specimens from one core are never split; without core fields it falls back to iid specimen resampling. Excludes uncertainty from drawing new raters and is not classification accuracy.'}
