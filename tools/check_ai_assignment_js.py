from pathlib import Path
from bs4 import BeautifulSoup
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1]
bad=[]
for ch in [10,11,12,13,14,15,16,17,20]:
    p=R/f"lectures/iscarb/Ch{ch}-FBR-Student-Assignment.html"
    soup=BeautifulSoup(p.read_text(encoding="utf-8"),"html.parser")
    scripts=[s.string or s.get_text() for s in soup.find_all("script") if (s.string or s.get_text()).strip()]
    for i,src in enumerate(scripts):
        f=Path(tempfile.gettempdir())/f"cpit455-ch{ch}-{i}.js"
        f.write_text(src,encoding="utf-8")
        q=subprocess.run(["node","--check",str(f)],capture_output=True,text=True)
        if q.returncode: bad.append((ch,i,q.stderr.strip()))
    text=p.read_text(encoding="utf-8")
    for token in ["cpit455-ai-v3","Download Blackboard JSON","22964248","AI-ONLY V3"]:
        if token.lower() not in text.lower(): bad.append((ch,"marker",token))
    print("PASS JS CH",ch)
if bad:
    print(bad);sys.exit(1)
print("PASS: all AI assignment scripts parse and required markers are present.")
