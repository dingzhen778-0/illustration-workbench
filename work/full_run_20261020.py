from pathlib import Path
import json, subprocess, shutil, sys, os
import numpy as np
import cv2
from PIL import Image

R=Path(__file__).resolve().parents[1]
O=R/'outputs/baobhan-shoulder-full-run-20261020-v1'
A=O/'assembly-assets'; A.mkdir(exist_ok=True)
W=R/'work/full-run-20261020'; W.mkdir(exist_ok=True)
F=R/'outputs/baobhan-shoulder-restart-v1/foundation'
I=R/'outputs/baobhan-shoulder-restart-v1/grouped-hair-component-clothes-v3/inputs'
CLI=os.environ.get("PHOTOCRAFT_CLI", "photocraft-cli")
size=(1024,1280); current=None; count=0; ops=[]
read=lambda p:np.array(Image.open(p).convert('RGBA'))
gray=lambda a:cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2GRAY)
body=read(F/'人体素体_干净透明底.png')
yy,xx=np.indices((1280,1024))
def call(args):
 p=subprocess.run([CLI,*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
def info(f):return json.loads(call(['info',f,'--compact']))
def flat(ls):
 for l in ls:yield l;yield from flat(l.get('children',[]))
def getid(n):return next(l['id'] for l in flat(info(current)['layers']) if l['name']==n)
def step(commands,label):
 global current,count
 count+=1;out=W/(str(count)+'-'+label+'.psd');args=['run',str(current)]
 for c,p in commands:args+=['--cmd',c,'--params',json.dumps(p,ensure_ascii=False)]
 call(args+['--out',out]);current=out;ops.extend(commands)
def place(path,name,smart=True):
 step([('file.placeEmbedded',{'path':str(path),'scale':100,'fit':False,'smartObject':smart,'center':[512,640]}),('layer.setProps',{'name':name})],'place')
def masked(src,name,m):
 place(src,name);lid=getid(name)
 rgba=np.full((1280,1024,4),255,'uint8');rgba[:,:,3]=m
 mp=A/(name+'_mask.png');Image.fromarray(rgba).save(mp)
 place(mp,'TEMP_MASK',False);tid=getid('TEMP_MASK')
 step([('select.loadSelection',{'channel':'transparency','layer':tid}),('layer.delete',{'layer':tid}),('layer.select',{'layer':lid}),('layer.layerMask.revealSelection',{'layer':lid}),('select.deselect',{})],'mask')
def save(name):
 p=O/(name+'.psd');shutil.copy2(current,p);call(['convert',p,p.with_suffix('.png')]);return p
def fill(m,name,color,opacity=1):
 rgba=np.full((1280,1024,4),255,'uint8');rgba[:,:,3]=m;mp=A/(name+'_mask.png');Image.fromarray(rgba).save(mp)
 place(mp,'TEMP_MASK',False);tid=getid('TEMP_MASK')
 step([('select.loadSelection',{'channel':'transparency','layer':tid}),('layer.delete',{'layer':tid}),('layer.newFillLayer.solidColor',{'color':color}),('layer.setProps',{'name':name,'opacity':opacity}),('select.deselect',{})],'fill')
def register(raw,key):
 im=Image.open(raw).convert('RGBA');src=np.array(im.resize(size,Image.Resampling.LANCZOS))
 stable=np.zeros((1280,1024),'uint8');stable[430:790,225:805]=255
 if key=='eyes':
  stable[:]=0;stable[570:740,350:615]=255;stable[410:580,690:780]=255;stable[600:785,530:690]=255
 sift=cv2.SIFT_create();kt,dt=sift.detectAndCompute(gray(body),stable);ks,ds=sift.detectAndCompute(gray(src),None)
 good=[a for a,b in cv2.BFMatcher().knnMatch(ds,dt,k=2) if a.distance<.68*b.distance]
 sp=np.float32([ks[m.queryIdx].pt for m in good]);tp=np.float32([kt[m.trainIdx].pt for m in good])
 mat,ins=cv2.estimateAffinePartial2D(sp,tp,method=cv2.RANSAC,ransacReprojThreshold=3)
 if mat is None or ins.sum()<7:raise RuntimeError((key,'registration requires review',len(good)))
 residual=np.linalg.norm(cv2.transform(sp[None],mat)[0]-tp,axis=1)
 src=cv2.warpAffine(src,mat,size,flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
 Image.fromarray(src).save(A/(key+'_registered.png'))
 return src,{'input':str(raw),'raw_size':im.size,'matrix':mat.tolist(),'inliers':int(ins.sum()),'median_residual_px':float(np.median(residual[ins[:,0]>0]))}
def keep_components(seed,minarea=150):
 n,lab,st,_=cv2.connectedComponentsWithStats(seed.astype('uint8'))
 return np.isin(lab,[j for j in range(1,n) if st[j,cv2.CC_STAT_AREA]>=minarea]).astype('uint8')*255
def mask_garment(src,key):
 geo=np.array(Image.open(I/(key+'_geometry.png')).convert('L'))
 f=src[:,:,:3].astype(float);alpha=src[:,:,3]>100
 radius=151 if key in ['neck_ruff','jabot','cravat'] else 101
 near=cv2.dilate((geo>30).astype('uint8'),np.ones((radius,radius),'uint8'))>0
 colored=(f[:,:,0]-f[:,:,1]>6)
 if key in ['bow','stand_collar','bodice']:colored|=f.max(2)<115
 if key=='jabot':colored=(f[:,:,0]-f[:,:,2]>4)&(f[:,:,0]>140)&(f[:,:,0]-f[:,:,1]<45)
 if key=='cravat':colored|=(f[:,:,2]-f[:,:,1]>7)&(f[:,:,0]<160)
 seed=colored&near&alpha
 # Search around geometry, while pale and gray cloth planes remain opaque.
 inside=cv2.erode((seed&(geo>100)).astype('uint8'),np.ones((5,5),'uint8'))
 if inside.sum()<40:inside=cv2.erode(seed.astype('uint8'),np.ones((3,3),'uint8'))
 gc=np.full(geo.shape,cv2.GC_BGD,'uint8');gc[near&alpha]=cv2.GC_PR_BGD;gc[seed]=cv2.GC_PR_FGD;gc[inside>0]=cv2.GC_FGD
 cv2.setRNGSeed(7);cv2.grabCut(src[:,:,:3].copy(),gc,None,np.zeros((1,65)),np.zeros((1,65)),4,cv2.GC_INIT_WITH_MASK)
 m=keep_components((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD),180)
 if key=='jabot':m[(f[:,:,0]-f[:,:,1]>65)]=0
 m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3),'uint8'))
 m=cv2.GaussianBlur(m,(3,3),.4);m=np.minimum(m,src[:,:,3])
 if key=='stand_collar':
  mannequin=(np.abs(f[:,:,0]-f[:,:,1])<4)&(np.abs(f[:,:,2]-f[:,:,0])<10)&(f.max(2)>75)
  m[mannequin]=0
 return m
garments={'bodice':'10-bodice-transparent.png','sleeves':'11-sleeves-transparent.png','stand_collar':'12-collar-transparent.png','neck_ruff':'13-ruff-transparent.png','cravat':'14-cravat-only-transparent.png','bow':'15-bow-transparent.png','jabot':'16-jabot-transparent.png'}
def clothes():
 global current
 report={}
 for key,name in garments.items():
  src,reg=register(O/name,key);m=mask_garment(src,key)
  targets={'neck_ruff':[350,803,777,972],'cravat':[414,912,594,1090],'bow':[390,899,633,1074],'jabot':[332,986,599,1280]}
  if key in targets:
   ys,xs=np.where(m>128);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];t=targets[key]
   sx=(t[2]-t[0])/(box[2]-box[0]);sy=(t[3]-t[1])/(box[3]-box[1]);mat=np.float32([[sx,0,t[0]-sx*box[0]],[0,sy,t[1]-sy*box[1]]])
   src=cv2.warpAffine(src,mat,size,flags=cv2.INTER_CUBIC);m=cv2.warpAffine(m,mat,size,flags=cv2.INTER_CUBIC)
   Image.fromarray(src).save(A/(key+'_registered.png'));reg['component_fit']={'source_bbox':box,'target_bbox':t,'matrix':mat.tolist()}
  Image.fromarray(m).save(A/(key+'_mask.png'));reg['mask_area']=int((m>128).sum());report[key]=reg
  print(key,reg['inliers'],round(reg['median_residual_px'],3),reg['mask_area'],flush=True)
 (O/'clothing-registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 current=F/'巴万希_独立人体素体.psd'
 for key,label in [('sleeves','双袖'),('bodice','红黑衣身'),('stand_collar','黑金立领'),('neck_ruff','白颈褶红束带'),('jabot','白褶襟'),('cravat','灰领巾'),('bow','黑蝴蝶结')]:
  src=A/(key+'_registered.png');m=np.array(Image.open(A/(key+'_mask.png')))
  if key=='sleeves':
   for n,c in [('远袖',xx<512),('近袖',xx>=512)]:masked(src,'服装 '+n,np.where(c,m,0).astype('uint8'))
  else:masked(src,'服装 '+label,m)
 p=save('服装组件_组装检查');(O/'clothing-native-layers.json').write_text(json.dumps(info(p),ensure_ascii=False,indent=2),encoding='utf-8')
 print('SAVED',p,flush=True)
def hair_templates():
 global current
 report={}
 for key,name in [('front','01-front-template.png'),('middle','02-middle-template.png'),('rear','03-rear-template.png')]:
  src,reg=register(O/name,'hair_'+key);f=src[:,:,:3].astype(float)
  m=keep_components((f[:,:,0]-f[:,:,1]>8)&(f[:,:,2]-f[:,:,1]>6)&(src[:,:,3]>100),100)
  m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),'uint8'));m=cv2.GaussianBlur(m,(3,3),.4);m=np.minimum(m,src[:,:,3])
  if key=='rear':m=np.minimum(m,255-body[:,:,3])
  Image.fromarray(m).save(A/('hair_'+key+'_mask.png'));report[key]=reg
 current=F/'巴万希_独立人体素体.psd'
 for key in ['rear','middle','front']:
  m=np.array(Image.open(A/('hair_'+key+'_mask.png')));src=read(A/('hair_'+key+'_registered.png'));f=src[:,:,:3].astype(float)
  fill(m,'头发模板 '+key,{'rear':'#BA2F6C','middle':'#DE1B62','front':'#E82B70'}[key])
  inner=(f[:,:,2]-f[:,:,0]>-10)&(f[:,:,0]<160)&(f[:,:,1]<130)&(m>128)&(f[:,:,0]-f[:,:,1]>5)
  fill((inner*255).astype('uint8'),'头发内侧 '+key,'#66506F')
 p=save('头发_三组模板组装');(O/'hair-template-registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('SAVED',p)
def prepare_final_assets():
 report={}
 for key,name in [('hair_base','04-hair-base.png'),('hair_finish','05-hair-finish.png')]:
  src,reg=register(O/name,key);f=src[:,:,:3].astype(float)
  m=keep_components((f[:,:,0]-f[:,:,1]>9)&(f[:,:,2]-f[:,:,1]>6)&(src[:,:,3]>100),120)
  m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3),'uint8'))
  outline=(cv2.dilate((m>100).astype('uint8'),np.ones((5,5),'uint8'))>0)&(f.max(2)<95)&(src[:,:,3]>100)
  m[outline]=255;m=cv2.GaussianBlur(m,(3,3),.4);m=np.minimum(m,src[:,:,3])
  guides={k:np.array(Image.open(A/('hair_'+k+'_mask.png'))) for k in ['rear','middle','front']}
  # Source geometry supplies group identity, the new rendering supplies edges.
  dist=np.stack([cv2.distanceTransform((guides[k]<100).astype('uint8'),cv2.DIST_L2,5) for k in guides]);owner=dist.argmin(0)
  for j,k in enumerate(guides):owner[guides[k]>128]=j
  for j,k in enumerate(guides):Image.fromarray(np.where(owner==j,m,0).astype('uint8')).save(A/(key+'_'+k+'_mask.png'))
  Image.fromarray(m).save(A/(key+'_mask.png'));report[key]=reg
 src,reg=register(O/'21-eyes.png','eyes');report['eyes']=reg
 # The eyes are the edited object; alignment uses stable nose/mouth contours.
 skin=read(A/'skin_registered.png');eye_mask=np.zeros((1280,1024),'uint8')
 for pts in [[(235,500),(292,478),(392,502),(410,555),(362,596),(268,592)],[(450,425),(530,397),(648,419),(652,474),(586,524),(474,528)]]:
  cv2.fillPoly(eye_mask,[np.array(pts,np.int32)],255)
 eye_mask=cv2.GaussianBlur(eye_mask,(9,9),1.1);eye_mask=np.minimum(eye_mask,body[:,:,3]);Image.fromarray(eye_mask).save(A/'eyes_mask.png')
 (O/'final-registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False),flush=True)
def assemble_final():
 global current
 current=F/'巴万希_独立人体素体.psd';roots=[];finishes=[]
 def hair(k,label):
  for stage,suffix in [('hair_base','基础体面'),('hair_finish','集中完善')]:
   n=label+' '+suffix;masked(A/(stage+'_registered.png'),n,np.array(Image.open(A/(stage+'_'+k+'_mask.png'))));roots.append(n)
   if stage=='hair_finish':finishes.append(n)
 hair('rear','10 后发')
 masked(A/'skin_registered.png','20 肤色体面',body[:,:,3]);roots.append('20 肤色体面')
 masked(A/'eyes_registered.png','21 双眼',np.array(Image.open(A/'eyes_mask.png')));roots.append('21 双眼')
 for key,label in [('sleeves','双袖'),('bodice','红黑衣身'),('stand_collar','黑金立领'),('neck_ruff','白颈褶红束带'),('jabot','白褶襟'),('cravat','灰领巾'),('bow','黑蝴蝶结')]:
  src=A/(key+'_registered.png');m=np.array(Image.open(A/(key+'_mask.png')))
  if key=='sleeves':
   for n,c in [('远袖',xx<512),('近袖',xx>=512)]:
    name='30 '+n;masked(src,name,np.where(c,m,0).astype('uint8'));roots.append(name)
  else:
   name='30 '+label;masked(src,name,m);roots.append(name)
 hair('middle','40 中发');hair('front','50 前发')
 pretone=save('肩像_色光微调前')
 # Native controls: restrain rear mass and unify lower-lock color.
 rear=np.array(Image.open(A/'hair_finish_rear_mask.png'))
 tone=(rear.astype(float)*np.clip((yy-350)/650,0,1)*.65).astype('uint8')
 fill(tone,'60 后发主次','#50334F',.17);roots.append('60 后发主次')
 hm=np.array(Image.open(A/'hair_finish_mask.png'));tip=np.clip((yy-850)/400,0,1)
 tip=(hm*tip*.35).astype('uint8');fill(tip,'61 发梢统一','#B38AA8',.18);roots.append('61 发梢统一')
 final=save('巴万希_肩像_完整制作_v1')
 (O/'native-layers.json').write_text(json.dumps(info(final),ensure_ascii=False,indent=2),encoding='utf-8')
 (O/'native-operations.json').write_text(json.dumps(ops,ensure_ascii=False,indent=2),encoding='utf-8')
 (O/'control-groups.json').write_text(json.dumps({'roots':roots,'finishes':finishes},ensure_ascii=False,indent=2),encoding='utf-8')
 print('SAVED',final,flush=True)
def qa_delivery():
 global current
 final=O/'巴万希_肩像_完整制作_v1.psd';current=final
 before=read(final.with_suffix('.png'));groups=[]
 for prefix,label in [('10 ','10 后发'),('20 ','20 肤色体面'),('21 ','21 双眼'),('30 ','30 服装组件'),('40 ','40 中发'),('50 ','50 前发'),('60 ','60 后发主次'),('61 ','61 发梢统一')]:
  names=[l['name'] for l in flat(info(current)['layers']) if l['name'].startswith(prefix)]
  if len(names)>1:
   ids=[getid(n) for n in names]
   step([('layer.select',{'layer':lid,'mode':'replace' if j==0 else 'add'}) for j,lid in enumerate(ids)]+[('layer.groupLayers',{'name':label})],'group')
   groups.append(label)
  else:groups.extend(names)
 # Optional preview field is kept hidden in the transparent source document.
 fill(np.full((1280,1024),255,'uint8'),'00 可选浅灰背景','#DED8E0')
 step([('layer.moveTo',{'layer':getid('00 可选浅灰背景'),'target':getid('01 完整人体原素体_无发无衣_冻结'),'position':'below'}),('layer.setProps',{'layer':getid('00 可选浅灰背景'),'visible':False})],'optional-background')
 final=save('巴万希_肩像_完整制作_v1');after=read(final.with_suffix('.png'))
 groupingdiff=int(np.any(before!=after,axis=2).sum())
 current=final;step([('layer.setProps',{'layer':getid('00 可选浅灰背景'),'visible':True})],'preview-background');call(['convert',current,O/'预览_浅灰底.png'])
 current=final;step([('layer.setProps',{'layer':getid(n),'visible':False}) for n in groups],'restore-foundation');call(['convert',current,O/'核验_关闭全部绘制.png'])
 restore=int(np.any(read(O/'核验_关闭全部绘制.png')!=body,axis=2).sum())
 current=final;step([('layer.setProps',{'layer':getid('60 后发主次'),'visible':False}),('layer.setProps',{'layer':getid('61 发梢统一'),'visible':False})],'native-off');call(['convert',current,O/'核验_关闭原生色光.png'])
 off=read(O/'核验_关闭原生色光.png');pretone=read(O/'肩像_色光微调前.png');tone_restore=int(np.any(off!=pretone,axis=2).sum())
 current=final;step([('layer.setProps',{'layer':getid('21 双眼'),'visible':False})],'eyes-off');call(['convert',current,O/'核验_关闭双眼.png'])
 eo=read(O/'核验_关闭双眼.png');em=np.array(Image.open(A/'eyes_mask.png'));eye_outside=int(((np.any(after!=eo,axis=2))&(em==0)).sum())
 call(['convert',final,O/'核验_PSD重开.png']);reopen=int(np.any(read(O/'核验_PSD重开.png')!=after,axis=2).sum())
 for name,box in [('细节_脸眼',(205,365,500,440)),('细节_胸颈',(325,715,420,420))]:
  x,y,w,h=box;call(['run',final,'--cmd','image.crop','--params',json.dumps({'x':x,'y':y,'width':w,'height':h}),'--out',O/(name+'.png')])
 inf=info(final);layers=list(flat(inf['layers']))
 report={'canvas':size,'grouping_diff_px':groupingdiff,'all_drawing_off_restore_foundation_diff_px':restore,'native_off_restore_pretone_diff_px':tone_restore,'eye_outside_mask_diff_px':eye_outside,'psd_reopen_diff_px':reopen,'smart_objects':sum(l['kind']=='Smart Object' for l in layers),'native_masks':sum(l['hasMask'] for l in layers),'layer_count_including_groups':len(layers),'clothing_components':7,'clothing_control_layers':8,'hair_stages':['three native solid-color templates','whole-hair base','whole-hair finish'],'face_stages':['skin planes','eyes on registered skin'],'user_acceptance':'awaiting','lighting':'generated lighting merged inside sources, plus two native color/focus controls'}
 (O/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');(O/'native-layers.json').write_text(json.dumps(inf,ensure_ascii=False,indent=2),encoding='utf-8')
 assert restore==tone_restore==eye_outside==reopen==groupingdiff==0,report
 print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':
 {'clothes':clothes,'hair_templates':hair_templates,'prepare_final_assets':prepare_final_assets,'assemble_final':assemble_final,'qa_delivery':qa_delivery}[sys.argv[1]]()
