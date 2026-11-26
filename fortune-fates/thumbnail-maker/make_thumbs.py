import json, sys, os, base64
P=sys.argv[1]  # photos dir
OUT=sys.argv[2]
def img(name):
    return 'data:image/jpeg;base64,'+base64.b64encode(open(f'{P}/{name}.jpg','rb').read()).decode()
SIL='''<svg viewBox="0 0 200 250" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMax meet" style="width:100%;height:100%"><circle cx="100" cy="95" r="52" fill="#1c1c22"/><path d="M10 250 C10 175 50 150 100 150 C150 150 190 175 190 250 Z" fill="#1c1c22"/></svg>'''
def card(c):
    hl=c.get('hl')
    if c.get('photo'):
        top=f'<div class="ph" style="background-image:url({img(c["photo"])})"></div>'
    elif c.get('brand'):
        b=c['brand']
        top=f'<div class="ph brand" style="background:{b["bg"]};color:{b["fg"]};font-size:{b.get("size",54)}px"><div>{b["text"]}</div></div>'
    else:
        top=f'<div class="ph sil">{SIL}<div class="silq">{c.get("silmark","")}</div></div>'
    stamp=f'<div class="stamp">{c["stamp"]}</div>' if c.get('stamp') else ''
    chip=f'<div class="chip" style="background:{c["chip"][1]}">{c["chip"][0]}</div>' if c.get('chip') else ''
    badge=f'<div class="badge">{c["badge"]}</div>' if c.get('badge') else ''
    tag=f'<div class="tag">{c["tag"]}</div>' if c.get('tag') else ''
    return f'''<div class="card{' hl' if hl else ''}">
  <div class="top">{top}{stamp}{chip}{badge}{tag}</div>
  <div class="name" style="background:{c.get('bar','#c62828')};font-size:{30 if len(c['name'])<=14 else 24}px">{c['name']}</div>
  <div class="why">{c['why']}</div>
  <div class="num"><div class="ico">{c['icon']}</div><div class="big" style="color:{c.get('numc','#111')};font-size:{ {1:96,2:96,3:90,4:76,5:64,6:56}.get(len(c['big']),50)}px">{c['big']}<div class="unit">{c['unit']}</div></div></div>
</div>'''
CSS='''*{margin:0;box-sizing:border-box}body{width:1280px;height:720px;background:#111;font-family:Inter,"Noto Color Emoji",sans-serif;overflow:hidden}
.row{display:flex;gap:6px;padding:6px;height:720px}
.card{flex:1;display:flex;flex-direction:column;background:#fff;border-radius:6px;overflow:hidden;position:relative}
.card.hl{outline:7px solid #ffd400;outline-offset:-7px;z-index:2}
.top{height:385px;position:relative;background:#ddd}
.ph{position:absolute;inset:0;background-size:cover;background-position:center 18%}
.ph.sil{background:linear-gradient(#9aa0aa,#6b7079);display:flex;align-items:flex-end;justify-content:center;padding-top:40px}
.silq{position:absolute;top:120px;width:100%;text-align:center;font:900 120px Inter;color:#ffd400;text-shadow:0 4px 0 #000}
.ph.brand{display:flex;align-items:center;justify-content:center;text-align:center;font-weight:900;line-height:1.02;padding:16px;letter-spacing:-1px}
.stamp{position:absolute;left:50%;top:80%;transform:translate(-50%,-50%) rotate(-14deg);border:7px solid #e01818;color:#e01818;font:900 46px Inter;padding:2px 14px;background:rgba(255,255,255,.85);letter-spacing:2px}
.chip{position:absolute;right:10px;top:10px;color:#fff;font:900 40px Inter;padding:4px 12px;border-radius:8px;box-shadow:0 3px 10px rgba(0,0,0,.4)}
.badge{position:absolute;left:0;bottom:0;background:#111;color:#fff;font:800 22px Inter;padding:5px 10px}
.tag{position:absolute;right:0;bottom:0;background:#c62828;color:#fff;font:800 20px Inter;padding:5px 10px;text-transform:uppercase}
.name{color:#fff;font:900 30px Inter;text-align:center;padding:10px 6px;text-transform:uppercase;letter-spacing:-.5px;white-space:nowrap;overflow:hidden}
.why{background:#eef0f3;color:#222;font:700 21px Inter;text-align:center;padding:9px 8px;min-height:66px;display:flex;align-items:center;justify-content:center;line-height:1.15}
.num{flex:1;display:flex;align-items:center;justify-content:space-between;padding:0 14px}
.ico{font-size:54px;flex:none}
.big{font-weight:900;letter-spacing:-3px;text-align:right;line-height:.95;white-space:nowrap}
.unit{font:800 18px Inter;white-space:nowrap;letter-spacing:0;color:#555;margin-top:6px}
'''
for t in json.load(open(sys.argv[3])):
    html=f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="row">{"".join(card(c) for c in t["cards"])}</div></body></html>'
    open(f'{OUT}/{t["file"]}.html','w').write(html)
    print(t['file'])
