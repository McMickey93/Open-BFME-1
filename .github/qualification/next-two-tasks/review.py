"""Read-only staged pre-commit review; creates no commit and publishes no lease values."""
import hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
key='b1';payload=Path(__file__).resolve().parent;cfg=json.loads((payload/'b1.json').read_text());root=Path.cwd();out=root.parent/'evidence-b1';out.mkdir(exist_ok=True)
bash=os.environ['BFME_NATIVE_BASH'];os.environ['PATH']=str(Path(bash).parent)+os.pathsep+os.environ['PATH'];os.environ['BFME_CLAIM_NS']='refs/heads/claims/'
expected='github:'+os.environ['GITHUB_ACTOR']+':bfme1:'+cfg['task_tag'];os.environ['BFME_CLAIM_OWNER']=expected

def run(label,cmd):
 print('>>> '+label,flush=True);p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/(label+'.log')).write_bytes(p.stdout);sys.stdout.buffer.write(p.stdout);sys.stdout.flush();assert p.returncode==0,label

def git(*args):return subprocess.check_output(['git',*args])
try:
 assert sys.platform=='win32' and git('rev-parse','HEAD').decode().strip()==cfg['base']
 run('requirements',[sys.executable,'-m','pip','install','--quiet','-r','tools/requirements.txt'])
 run('setup-hooks',[bash,'tools/setup_hooks.sh'])
 sys.path.insert(0,str(root/'tools'));import claims
 for i,c in enumerate(cfg['claims']):
  run('read-public-claim-'+str(i),['git','-c','submodule.recurse=false','fetch','--depth=1','--no-tags','origin','refs/heads/'+c['ref']])
  token=git('rev-parse','FETCH_HEAD').decode().strip();info=json.loads(git('show','-s','--format=%B',token));assert info['owner']==expected and info['expires']>time.time();assert claims.holds(int(c['rva'],16),token)
 for path in cfg['review_paths']:
  if path=='inputs/reference/open-bfme-2':
   run('stage-donor',['git','update-index','--add','--cacheinfo','160000,'+cfg['donor_revision']+','+path]);continue
  raw=(payload/'files'/'b1'/path).read_bytes();target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 run('stage-files',['git','add','--',*[p for p in cfg['review_paths'] if p!='inputs/reference/open-bfme-2']])
 run('donor-init',['git','-c','submodule.recurse=false','submodule','update','--init','--depth=1','inputs/reference/open-bfme-2'])
 assert git('-C','inputs/reference/open-bfme-2','rev-parse','HEAD').decode().strip()==cfg['donor_revision']
 assert git('write-tree').decode().strip()==cfg['review_tree']
 run('normal-pre-commit',[bash,'.githooks/pre-commit'])
 assert git('write-tree').decode().strip()==cfg['review_tree']
 (out/'review.patch').write_bytes(git('diff','--cached','--binary','--full-index'))
 (out/'review-result.json').write_text(json.dumps({'base':cfg['base'],'tree':cfg['review_tree'],'normal_pre_commit_passed':True,'commit_created':False,'lease_values_published':False},indent=2)+'\n')
except BaseException:
 (out/'failure.txt').write_text(traceback.format_exc());raise
