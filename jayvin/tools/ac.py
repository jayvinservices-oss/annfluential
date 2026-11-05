import json,urllib.request,urllib.parse,time,string
terms=["asmr","asmr gum","asmr gum chewing","asmr lip gloss","asmr nails","asmr christmas","christmas asmr","asmr sleep","ai asmr","asmr mouth sounds","asmr crunchy","asmr whisper","asmr tapping","asmr no talking","asmr 1 hour","asmr gum popping","asmr bubble gum","asmr long nails","asmr nail tapping","asmr lip","asmr for sleep","asmr glass","asmr winter","asmr holiday","asmr slime","asmr crafts","asmr makeup","asmr pov","asmr fall","asmr thanksgiving","asmr november","asmr gift wrapping","asmr ornament","asmr 2026","asmr 8 hours","asmr 3 hours"]+["asmr "+c for c in string.ascii_lowercase]
out={}
for t in terms:
  u="https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=en&q="+urllib.parse.quote(t)
  try: out[t]=json.loads(urllib.request.urlopen(u,timeout=15).read().decode('utf-8','replace'))[1]
  except Exception as e: out[t]=["ERR "+str(e)]
  time.sleep(0.3)
json.dump(out,open("ac.json","w"),indent=1)
for t,v in out.items(): print(t,"=>"," | ".join(v))
