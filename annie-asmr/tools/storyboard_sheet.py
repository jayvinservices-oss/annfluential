from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import textwrap, os
R='/home/user/annfluential/annie-asmr/prompts/reference/'
F='/usr/share/fonts/truetype/dejavu/'
def f(n,s): return ImageFont.truetype(F+n,s)
SB,SR,SRB=f('DejaVuSans-Bold.ttf',22),f('DejaVuSans.ttf',17),f('DejaVuSerif-Bold.ttf',40)
BG=(36,24,26); CARD=(58,38,42); GOLD=(222,186,130); TXT=(240,230,225); MUTE=(190,170,165); REAL=(126,196,150); AI=(236,150,170)
W,H=2400,1880
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
d.text((60,40),"ANNIE ASMR · STORYBOARD TEST",font=SB,fill=GOLD)
d.text((60,72),"Bedtime with Ace: 1 minute, 12 shots x 5 seconds",font=SRB,fill=TXT)
d.text((60,128),"Real purring all the way through (cat-purr-01). No talking. Slow, warm, lamp-lit bedroom look. 16:9.",font=SR,fill=MUTE)
def thumb(path,w,h,flip=False,blur=0):
    t=Image.open(path).convert('RGB')
    if '/stills/' in path:  # presenter: keep nose-down only
        t=t.crop((0,int(t.height*0.42),t.width,t.height))
    t=ImageOps.fit(t,(w,h),centering=(0.5,0.45 if '/stills/' not in path else 0.1))
    if flip: t=ImageOps.mirror(t)
    if blur: t=t.filter(ImageFilter.GaussianBlur(blur))
    return t
A=R+'ace/'; S=R+'stills/'
P=[ # time,title,src,img,visual,camera,action
("0:00","Lamp on","AI",S+'bedroom/gloss.png',"Dim bedroom, fairy lights, snowy window","Wide, static","Lamp clicks on, warm glow fills the room"),
("0:05","Ace on the bed","REAL",A+'ace-lying-on-blanket-2026-08-18.jpg',"Ace stretched on the blanket","Phone on the bed, eye level","He blinks slowly, tail settles"),
("0:10","Hand comes in","AI",R+'stills/hands.png',"Caramel hand, long coffin nails, gold ring","Close, from above","Hand lowers slowly toward his head"),
("0:15","First stroke","AI",A+'ace-face-closeup-2026-04-03.jpg',"Fingers stroke between his ears","Close-up, still","One slow stroke, head to neck"),
("0:20","Eyes closing","REAL",A+'ace-face-closeup-2026-04-03.jpg',"Ace's face, eyes half shut","Very close, handheld steady","Eyes close; whiskers relax"),
("0:25","Chin scratch","AI",R+'stills/hands.png',"Nails under his chin","Close, side angle","Gentle scratch, he lifts his chin"),
("0:30","Paws kneading","REAL",A+'ace-lying-on-blanket-2026-08-18.jpg',"Front paws on the blanket","Low, close to paws","Slow kneading"),
("0:35","Purr close-up","REAL",A+'ace-face-closeup-2026-04-03.jpg',"Side of his face and chest","Macro, still","Chest rises and falls with the purr"),
("0:40","Long strokes","AI",A+'ace-sleeping-loaf-2026-06-13.jpg',"Hand along his back","Top-down","Three long, slow strokes"),
("0:45","Curling up","REAL",A+'ace-sleeping-loaf-2026-06-13.jpg',"Ace tucks into a loaf","Medium, static","He curls in and settles"),
("0:50","Lamp dims","AI",S+'bedroom/gum.png',"Room with Ace asleep","Slow pull-back","Light dims to night-light"),
("0:55","Title card","EDIT",A+'ace-sleeping-loaf-2026-06-13.jpg',"Text over the last shot","Static","'Fall asleep with Ace · 1 hour' fades in"),
]
cw,ch=(W-60*2-30*3)//4,520
for i,(t,ti,src,img,vis,cam,act) in enumerate(P):
    x=60+(i%4)*(cw+30); y=180+(i//4)*(ch+24)
    d.rounded_rectangle((x,y,x+cw,y+ch),14,fill=CARD)
    th=thumb(img,cw-24,250,blur=0); im.paste(th,(x+12,y+12))
    col={'REAL':REAL,'AI':AI,'EDIT':GOLD}[src]
    lab={'REAL':'REAL: film Ace','AI':'AI clip','EDIT':'Edit only'}[src]
    d.rounded_rectangle((x+20,y+20,x+20+d.textlength(lab,font=SB)+24,y+56),10,fill=col)
    d.text((x+32,y+24),lab,font=SB,fill=BG)
    d.text((x+16,y+276),f"{i+1:02d}  {t}-0:{int(t[2:])+5:02d}",font=SB,fill=GOLD)
    d.text((x+16,y+306),ti,font=SB,fill=TXT)
    yy=y+342
    for k,v in (("Visual",vis),("Camera",cam),("Action",act)):
        for j,line in enumerate(textwrap.wrap(f"{k}: {v}",44)):
            d.text((x+16,yy),line,font=SR,fill=TXT); yy+=22
        yy+=4
fy=180+3*(ch+24)+6
d.text((60,fy),"REFERENCES  ·  Ace: real tuxedo coat, white chest and paws  ·  Hand: caramel skin, long glossy coffin nails, gold ring  ·  Never a full face or eyes",font=SR,fill=GOLD)
d.text((60,fy+28),"Mix: 5 shots real (Ann films 10 to 15 min of Ace), 6 AI hand shots from one fixed presenter still, 1 edit-only. AI clips: test 3 premium models on shot 04 first, then make the rest with the winner.",font=SR,fill=MUTE)
out='/home/user/annfluential/annie-asmr/storyboards/ace-bedtime-1min-test.png'
im.save(out); print(out, im.size)
