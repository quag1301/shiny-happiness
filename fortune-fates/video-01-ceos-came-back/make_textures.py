"""Procedurally generate paper, wall and stamp-grunge textures (no stock assets)."""
import numpy as np, sys
from PIL import Image, ImageFilter
out=sys.argv[1]; rng=np.random.default_rng(7)
def blur_noise(h,w,s):
    n=Image.fromarray((rng.random((h,w))*255).astype('uint8')).filter(ImageFilter.GaussianBlur(s))
    a=np.asarray(n).astype(float); return (a-a.min())/(a.max()-a.min()+1e-9)
# paper card 500x820 (rendered at 2x for crispness)
H,W=1640,1000
base=np.array([239,230,207],float)
fib=blur_noise(H,W,1.2)*0.6+blur_noise(H,W,6)*0.4
blot=blur_noise(H,W,60)
yy,xx=np.mgrid[0:H,0:W]; edge=np.minimum.reduce([xx,W-xx,yy,H-yy])/80; edge=np.clip(edge,0,1)
shade=(fib-0.5)*18+(blot-0.5)*22-(1-edge)*28
img=np.clip(base[None,None,:]+shade[...,None]*np.array([1,1,1.25]),0,255)
# a coffee ring on some cards? keep subtle foxing specks
sp=rng.random((H,W))>0.9993; specks=Image.fromarray((sp*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2.2)); s=np.asarray(specks)/255.0
img-= s[...,None]*np.array([40,55,80])*3
Image.fromarray(np.clip(img,0,255).astype('uint8')).save(f'{out}/paper.png')
# wall 1920x1080: dark green painted plaster
H,W=1080,1920
n=blur_noise(H,W,1)*0.35+blur_noise(H,W,14)*0.4+blur_noise(H,W,120)*0.25
col=np.array([34,46,40],float)
img=col[None,None,:]*(0.75+0.5*n[...,None])
yy,xx=np.mgrid[0:H,0:W]; vig=1-0.55*(((xx-W/2)/(W/1.3))**2+((yy-H/2.4)/(H/1.1))**2)
img*=np.clip(vig,0.35,1)[...,None]
Image.fromarray(np.clip(img,0,255).astype('uint8')).save(f'{out}/wall.png')
# stamp grunge mask (alpha) 600x220
H,W=440,1200
g=blur_noise(H,W,1.5)*0.7+blur_noise(H,W,10)*0.3
alpha=np.where(g>0.30,255,0).astype('uint8')
holes=rng.random((H,W))>0.985; alpha[holes]=0
a=Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8))
rgba=Image.new('RGBA',(W,H),(0,0,0,0)); rgba.putalpha(a); rgba.save(f'{out}/grunge.png')
# ink mask: lighter erosion for clock-printed rows
g=blur_noise(H,W,0.8); alpha=np.where(g>0.18,255,90).astype('uint8')
rgba=Image.new('RGBA',(W,H),(0,0,0,0)); rgba.putalpha(Image.fromarray(alpha)); rgba.save(f'{out}/inkmask.png')
# brushed steel strip 1920x200
H,W=200,1920
streak=np.asarray(Image.fromarray((rng.random((H,W))*255).astype('uint8')).resize((W,H)).filter(ImageFilter.BoxBlur(0)))/255
streak=np.asarray(Image.fromarray((rng.random((H,8))*255).astype('uint8')).resize((W,H),Image.BILINEAR))/255*0.5+streak*0.15
grad=np.linspace(1.05,0.6,H)[:,None]
v=(118+60*streak)*grad
img=np.stack([v,v*1.01,v*1.04],-1)
Image.fromarray(np.clip(img,0,255).astype('uint8')).save(f'{out}/steel.png')
print('textures ok')
