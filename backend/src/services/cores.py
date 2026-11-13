def core_labels(specimens):
 return [(specimen.get('core') or '').strip() for specimen in specimens]

def groups_from_rows(rows):
 labels=core_labels(rows)
 if not any(labels):return []
 if not all(labels) or len(set(labels))<2:raise ValueError('岩芯分组无效：须全部试样有岩芯编号且至少两组')
 ordered=[];lookup={}
 for index,label in enumerate(labels):
  if label not in lookup:lookup[label]=[];ordered.append(label)
  lookup[label].append(index)
 return [{'core':label,'specimen_indices':lookup[label],'specimen_count':len(lookup[label])} for label in ordered]

def grouping_summary(rows,groups):
 sizes=[group['specimen_count'] for group in groups]
 return {'resampling_unit':'core_cluster' if groups else 'specimen','core_count':len(groups),'specimen_count':len(rows),'core_groups':[{'core':g['core'],'specimen_count':g['specimen_count'],'specimen_references':[rows[i]['reference'] for i in g['specimen_indices']]} for g in groups],'group_sizes':sizes,'distinct_group_sizes':sorted(set(sizes)),'unequal_group_sizes':len(set(sizes))>1,'min_group_size':min(sizes) if sizes else None,'max_group_size':max(sizes) if sizes else None,'point_estimate_weighting':'每个原始试样行等权；点估计始终使用原逐票全部试样，与组大小无关','legacy_without_core':not groups}
