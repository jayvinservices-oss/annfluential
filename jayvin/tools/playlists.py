import time, yaml
from googleapiclient.errors import HttpError
from pipeline.youtube import data_api
yt=data_api()
vids={v["id"]:v for v in yaml.safe_load(open("metadata/channel/videos-2026-11-04.yaml"))}
P=[("Gum Club: Gum Chewing & Popping ASMR","Gum chewing, bubble gum popping and crackling ASMR, up close. Start with the 30-minute ones for sleep. #asmr #gumchewingasmr",
    ["-RTD9GAQDvE","8Ucoiaa8txU","E8cQEbd75pw","mapU9Ef_pIw","Alnk7CONm-I","1G89iMMOI5g"]),
   ("Long ASMR for Sleep (20+ Minutes)","Every Annie ASMR video that runs 20 minutes or longer: gum, mouth sounds, crinkles and tapping for falling asleep. #asmrforsleep",
    ["-RTD9GAQDvE","8Ucoiaa8txU","E8cQEbd75pw","QjHH9mTDgqo","muykmkDccbc","jCEzkFZkeDM","NNcY2h2XoDQ","xluqlBVdh_I"]),
   ("Mouth Sounds & Crunchy ASMR","Mouth sounds, lollipops and crunchy eating sounds on a close mic. #mouthsoundsasmr #crunchyasmr",
    ["F6rNa32CDAs","P_cJZtYVsZc","lIwULG0Sv6E","Y3uRqQsTbqg","QjHH9mTDgqo","LfOA7bxygUQ","wtpjipJfYwU","UGamQ5bkBx8","EFl7zX3vx9Y"]),
   ("Nail Studio: Nail Tapping & Scratching ASMR","Long nails tapping and scratching on bottles, glass, tools and the mic. #nailtappingasmr #longnailsasmr",
    ["K5Brx7TxbH8","Alnk7CONm-I","4bUAtEp60xg","9O8R-z3zLlc","cWQiRnjzkgI","7ya0JSlcdfI","j3bq7TMxtyU","MtcKJhoKkww","H84T4QFhgzA"]),
   ("Gloss Lab: Lip Gloss & Makeup ASMR","Lip gloss pumping, application and gentle makeup ASMR. More coming. #lipglossasmr",
    ["OamJVKdG1c8","ON_XjWGapbQ"]),
   ("Craft Corner: Paper, Scissors & Crinkles ASMR","Paper tearing, scissors, bubble wrap and crafting sounds. Christmas crafts coming in December. #craftasmr",
    ["jCEzkFZkeDM","tYHrGYJu914","kAR89YgOpwM"])]
def call(req):
    for i in range(6):
        try: return req.execute()
        except HttpError as e:
            if e.resp.status in (409,500,503) and i<5: time.sleep(3*(i+1)); continue
            raise
mine={}
tok=None
while True:
    r=call(yt.playlists().list(part="snippet",mine=True,maxResults=50,pageToken=tok))
    for p in r["items"]: mine.setdefault(p["snippet"]["title"],p["id"])
    tok=r.get("nextPageToken")
    if not tok: break
made=[]
for title,desc,ids in P:
    pid=mine.get(title) or call(yt.playlists().insert(part="snippet,status",body={"snippet":{"title":title,"description":desc},"status":{"privacyStatus":"public"}}))["id"]
    have=set();tok=None
    try:
        while True:
            r=yt.playlistItems().list(part="contentDetails",playlistId=pid,maxResults=50,pageToken=tok).execute()
            have|={i["contentDetails"]["videoId"] for i in r["items"]}; tok=r.get("nextPageToken")
            if not tok: break
    except HttpError as e:
        if e.resp.status != 404: raise   # brand-new empty playlists answer 404 here; treat as empty
    for vid in ids:
        if vid in have or vid not in vids or vids[vid]["privacy"]!="public": continue
        call(yt.playlistItems().insert(part="snippet",body={"snippet":{"playlistId":pid,"resourceId":{"kind":"youtube#video","videoId":vid}}})); have.add(vid); time.sleep(0.5)
    made.append({"title":title,"id":pid,"videos":len(have)}); print(f"{len(have):2d} videos  {title}  ({pid})")
yaml.safe_dump(made,open("metadata/channel/playlists.yaml","w"),sort_keys=False,allow_unicode=True)
