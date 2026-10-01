import subprocess, json
def gh(*args, input=None, method=None):
    cmd=["gh","api"]+list(args)
    if method: cmd+=["-X",method]
    if input is not None: cmd+=["--input","-"]
    p=subprocess.run(cmd,input=input,capture_output=True,text=True,encoding="utf-8")
    return p.returncode,p.stdout,p.stderr

rc,out,err=gh("/repos/SZhang0314/ucas-physics-faculty/git/blobs", input=json.dumps({"content":"aGVsbG8=","encoding":"base64"}), method="POST")
print("blob rc",rc); print("out",out[:200]); print("err",err[:300])

rc,out,err=gh("/repos/SZhang0314/ucas-physics-faculty/git/trees", input=json.dumps({"tree":[]}), method="POST")
print("empty-tree rc",rc); print("out",out[:200]); print("err",err[:300])
