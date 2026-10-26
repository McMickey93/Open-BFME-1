import hashlib,json,os,re,subprocess,sys,tempfile,time,traceback
from pathlib import Path
payload=Path(__file__).resolve().parent
key=sys.argv[1];cfg=json.loads((payload/(key+'.json')).read_text());root=Path.cwd()
evidence=root.parent/('evidence-'+key);evidence.mkdir(exist_ok=True)
bash=os.environ['BFME_NATIVE_BASH'];os.environ['PATH']=str(Path(bash).parent)+os.pathsep+os.environ['PATH'];os.environ['BFME_CLAIM_NS']='refs/heads/claims/';expected_owner='github:'+os.environ['GITHUB_ACTOR']+':'+cfg['project']+':'+cfg['task_tag'];os.environ['BFME_CLAIM_OWNER']=expected_owner
results=[]
def run(label,args,stdin=None):
 print('\n>>>',label,flush=True);p=subprocess.run(args,input=stdin,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (evidence/(label+'.log')).write_bytes(p.stdout);sys.stdout.buffer.write(p.stdout);sys.stdout.flush();results.append({'label':label,'command':args,'exit':p.returncode});(evidence/'results.json').write_text(json.dumps(results,indent=2))
 if p.returncode:raise RuntimeError(label+' failed')
 return p.stdout
def git(*args):return subprocess.check_output(['git',*args])
try:
 assert sys.platform=='win32'
 assert git('rev-parse','HEAD').decode().strip()==cfg['base']
 if cfg['project']=='bfme2':run('reference-init',['git','-c','submodule.recurse=false','submodule','update','--init','--depth=1','reference/open-bfme-1'])
 req='tools/requirements.txt' if cfg['project']=='bfme1' else 'reference/open-bfme-1/tools/requirements.txt'
 run('requirements',[sys.executable,'-m','pip','install','--quiet','-r',req])
 run('fetch-base',['git','-c','submodule.recurse=false','fetch','--depth=128','origin','+refs/heads/master:refs/remotes/origin/master'])
 run('setup-hooks',[bash,'tools/setup_hooks.sh'])
 run('fetch-candidate',['git','-c','submodule.recurse=false','fetch','--depth=2','https://github.com/McMickey93/'+cfg['repository']+'.git',cfg['commit']])
 raw=git('cat-file','commit',cfg['commit']);headers,message=raw.split(b'\n\n',1);headers=headers.split(b'\n');assert len(headers)==4
 assert headers[1]==b'parent '+cfg['base'].encode()
 paths=git('diff','--name-only',cfg['base'],cfg['commit']).decode().splitlines();assert set(paths)==set(cfg['final_paths'])
 sys.path.insert(0,str(root/'tools'));import claims
 held={}
 def fence():
  for c in cfg['claims']:
   k=int(c['rva'],16) if 'rva' in c else claims.key_of('file:'+c['source'])
   run('claim-'+str(cfg['claims'].index(c)),['git','-c','submodule.recurse=false','fetch','--depth=1','--no-tags','origin','refs/heads/'+c['ref']])
   token=git('rev-parse','FETCH_HEAD').decode().strip();info=json.loads(git('show','-s','--format=%B',token))
   assert info['owner']==expected_owner and info['expires']>time.time()
   assert k not in held or held[k]==token, 'Claim generation changed'
   held[k]=token
   assert claims.holds(k,token);claims._mirror(k,token)
 fence()
 for path in paths:
  assert path.startswith(('game/','Code/','targets/game/reverse/identity_evidence/','reverse/attempt_support/')) or path=='reverse/data_check_baseline.txt'
  p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(git('show',cfg['commit']+':'+path))
 run('stage',['git','add','--',*paths])
 assert headers[0]==b'tree '+git('write-tree').strip()
 run('build',[bash,'build.sh',*cfg['sources'],cfg['provider']])
 env=os.environ.copy()
 for h,role in [(headers[2],'AUTHOR'),(headers[3],'COMMITTER')]:
  m=re.fullmatch(rb'(author|committer) (.*) <([^<>]*)> (\d+) ([+-]\d{4})',h);assert m
  env['GIT_'+role+'_NAME']=m[2].decode();env['GIT_'+role+'_EMAIL']=m[3].decode();env['GIT_'+role+'_DATE']=(m[4]+b' '+m[5]).decode()
 with tempfile.NamedTemporaryFile(delete=False) as f:f.write(message);msg=f.name
 try:
  p=subprocess.run(['git','commit','--cleanup=verbatim','--file',msg],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(evidence/'normal-commit.log').write_bytes(p.stdout);sys.stdout.buffer.write(p.stdout);sys.stdout.flush();assert p.returncode==0
 finally:os.unlink(msg)
 assert git('rev-parse','HEAD').decode().strip()==cfg['commit']
 ref='refs/heads/codex/20261026-'+cfg['branch_task']
 advertised=git('ls-remote','https://github.com/McMickey93/'+cfg['repository']+'.git',ref).decode().split()[0]
 assert advertised==cfg['base'], 'Review destination branch before publication'
 stdin=(ref+' '+cfg['commit']+' '+ref+' '+advertised+'\n').encode()
 run('normal-pre-push',[bash,'.githooks/pre-push','https://github.com/McMickey93/'+cfg['repository']+'.git','https://github.com/McMickey93/'+cfg['repository']+'.git'],stdin)
 fence();run('progress',[sys.executable,'tools/progress.py',cfg['base']])
 (evidence/'qualified.json').write_text(json.dumps({'commit':cfg['commit'],'base':cfg['base'],'normal_commit_passed':True,'normal_pre_push_passed':True,'paths':paths},indent=2)+'\n')
except BaseException:
 (evidence/'failure.txt').write_text(traceback.format_exc());raise
