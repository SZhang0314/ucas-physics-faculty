import base64, json, subprocess

OWNER="SZhang0314"; REPO="ucas-physics-faculty"; BRANCH="main"

def gh(*args, input=None, method=None):
    cmd=["gh","api"]+list(args)
    if method: cmd+=["-X",method]
    if input is not None: cmd+=["--input","-"]
    p=subprocess.run(cmd,input=input,capture_output=True,text=True,encoding="utf-8")
    return p.returncode,p.stdout,p.stderr

content=base64.b64encode(b"# ucas-physics-faculty\n\nInitializing repository.\n").decode()
payload=json.dumps({"message":"init","content":content,"branch":BRANCH})
rc,out,err=gh(f"/repos/{OWNER}/{REPO}/contents/README.md", input=payload, method="PUT")
print("rc",rc); print(out[:300]); print(err[:300])
