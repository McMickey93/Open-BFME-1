import csv,hashlib,json,os,shutil,subprocess,sys,time,traceback
from pathlib import Path
payload=Path(__file__).resolve().parent
cfg=json.loads((payload/(sys.argv[1]+'.json')).read_text())
root=Path.cwd(); evidence=root.parent/('evidence-'+sys.argv[1]);evidence.mkdir(exist_ok=True)
bash=os.environ['BFME_NATIVE_BASH'];os.environ['PATH']=str(Path(bash).parent)+os.pathsep+os.environ['PATH']
os.environ['PYTHONUNBUFFERED']='1';os.environ['BFME_CLAIM_OWNER']=cfg['owner']
results=[]
def run(label,args,required=True,stdin=None):
 print('\n>>>',label,flush=True)
 t=time.time();p=subprocess.run(args,input=stdin,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (evidence/(label+'.log')).write_bytes(p.stdout);sys.stdout.buffer.write(p.stdout);sys.stdout.flush()
 results.append({'label':label,'command':args,'exit':p.returncode,'seconds':round(time.time()-t,2)})
 (evidence/'results.json').write_text(json.dumps(results,indent=2))
 if required and p.returncode: raise RuntimeError(label+' failed')
 return p
try:
 assert sys.platform=='win32'
 assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==cfg['base']
 if cfg['project']=='bfme2':
  run('reference-init',['git','-c','submodule.recurse=false','submodule','update','--init','--depth=1','reference/open-bfme-1'])
 run('requirements',[sys.executable,'-m','pip','install','--quiet','-r','tools/requirements.txt'])
 run('setup-hooks',[bash,'tools/setup_hooks.sh'])
 run('check-ledger',[sys.executable,'tools/check_csv.py'])
 sys.path.insert(0,str(root/'tools'))
 import claims
 assert claims.fetch(), 'Cannot verify current upstream claims'
 current=claims._read_local()
 for c in cfg['claims']:
  key=int(c['rva'],16) if 'rva' in c else claims.key_of('file:'+c['source'])
  token,info=current[key]
  assert token==c['token'] and info['owner']==cfg['owner'] and info['expires']>time.time(), 'Claim changed'
 sources=cfg['sources'];provider=cfg['provider'];scope=sources+[provider]
 run('baseline-build',[bash,'build.sh',*scope])
 if cfg['project']=='bfme1':
  run('fetch-index',[sys.executable,'tools/link_check.py','fetch-index'],False)
  run('before-link',[sys.executable,'tools/link_check.py',*scope],False)
 for path in sources:
  target=root/path
  assert hashlib.sha256(target.read_bytes()).hexdigest()==cfg['before'][path]
  raw=(payload/'files'/sys.argv[1]/path).read_bytes()
  assert hashlib.sha256(raw).hexdigest()==cfg['after'][path]
  target.write_bytes(raw)
 run('stage-source',['git','add','--',*sources])
 run('candidate-build',[bash,'build.sh',*scope])
 for path in sources:
  run('declared-'+str(sources.index(path)),[sys.executable,'tools/find_declared_unmatched.py',path])
 if cfg['project']=='bfme2':
  run('retire-data',[sys.executable,'tools/repair_queue.py','retire','data',sources[0]])
  run('stage-debt',['git','add','--','reverse/data_check_baseline.txt'])
 else:
  run('after-link',[sys.executable,'tools/link_check.py',*scope],False)
 run('progress',[sys.executable,'tools/progress.py','origin/master'])
 run('candidate-diff',['git','diff','HEAD','--binary','--',*sources,*cfg.get('registers',[])])
 for path in sources+cfg.get('registers',[]):
  dest=evidence/'files'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/path,dest)
 # Preserve only scoped compiler evidence, never retail images/toolchains.
 build=root/'build'/'match'
 for pat in ['*.obj','*.deps.json','*.log']:
  for path in build.glob(pat):
   dest=evidence/'objects'/path.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(path,dest)
 (evidence/'status.txt').write_text('VERIFIED SOURCE EXPERIMENT; NOT COMMITTED OR PUBLISHED\n')
except BaseException:
 (evidence/'failure.txt').write_text(traceback.format_exc());raise
