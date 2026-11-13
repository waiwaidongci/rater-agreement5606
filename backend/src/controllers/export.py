from fastapi import HTTPException
from src.models import ReviewMemo
from src.services.audit import record
from src.utils.csv_export import csv_response

def grouping_fields(result):
 grouping=result.get('grouping') or {};unit=grouping.get('resampling_unit','specimen')
 if unit=='core_cluster':return grouping.get('core_count'),'×'.join(str(v) for v in sorted(set(grouping.get('group_sizes') or []))) or '—','按岩芯成组；整芯携带全部试样，重复抽中保留倍数'
 return '—','—','无岩芯字段；每次有放回抽整试样计数行'

def repeat_digest(bootstrap,limit=8):
 records=bootstrap.get('replicates') or []
 parts=[]
 for record in records[:limit]:
  cores=record.get('sampled_cores')
  if cores is None:parts.append(f"#{record.get('repeat')} 抽整试样行 {len(record.get('sample_indices',[]))} 个（示例索引 {','.join(str(v) for v in record.get('sample_indices',[])[:8])}{'…' if len(record.get('sample_indices',[]))>8 else ''}）")
  else:
   counts=record.get('core_multiplicity') or {};label='、'.join(f'{core}×{counts.get(core,1)}' for core in dict.fromkeys(cores));parts.append(f"#{record.get('repeat')} {label}→{record.get('drawn_specimen_count',len(record.get('sample_indices',[])))}试样")
 if len(records)>limit:parts.append(f'…共{len(records)}次，完整抽取记录见冻结结果')
 return '；'.join(parts)

def export_memo(db,id,actor):
 memo=db.get(ReviewMemo,id)
 if not memo:raise HTTPException(404,'说明不存在')
 if memo.status!='approved':raise HTTPException(409,'仅批准说明可导出')
 r=memo.result_snapshot;b=r['bootstrap'];ci=b.get('interval');core_count,group_sizes,unit_note=grouping_fields(r);digest=repeat_digest(b)
 rows=[[memo.name,r['source_study']['name'],r['fingerprint'],r['kappa'],r['pbar'],r['pe'],b.get('resampling_unit','specimen'),core_count,group_sizes,unit_note,digest if index==0 else '',b['valid_repeats'],b['invalid_repeats'],ci[0] if ci else '',ci[1] if ci else '',item['reference'],item.get('core') or '—',(r.get('grouping') or {}).get('point_estimate_weighting',''),item['agreement'],str(item['counts']),memo.interpretation,memo.next_step,memo.review_note] for index,item in enumerate(r['items'])]
 record(db,actor,'memo.exported',{'memo_id':id});return csv_response(f'rater-review-{id}.csv',rows,['复核说明','研究','指纹','Fleissκ','Pbar','Pe','重采样单位','岩芯组数','组大小','抽样口径','前8次抽取核对（抽中岩芯×倍数→试样总数）','有效重复','退化重复','经验区间下限','经验区间上限','试样','岩芯','点估计口径','逐项P','类别计数','人工解释','下一步','审核意见'])
