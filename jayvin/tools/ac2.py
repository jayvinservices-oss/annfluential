import json,urllib.request,urllib.parse,time
terms=["asmr","asmr gum","asmr lip gloss","asmr christmas","ai asmr","asmr nails"]
out={}
for gl in ["CA","GB"]:
  for t in terms:
    u=f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=en&gl={gl}&q="+urllib.parse.quote(t)
    try: out[gl+":"+t]=json.loads(urllib.request.urlopen(u,timeout=15).read().decode('utf-8','replace'))[1]
    except Exception as e: out[gl+":"+t]=["ERR "+str(e)]
    time.sleep(0.3)
json.dump(out,open("ac2.json","w"),indent=1)
for t,v in out.items(): print(t,"=>"," | ".join(v))
