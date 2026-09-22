#!/usr/bin/env python3
from pathlib import Path
import subprocess, math, shutil, os
from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageEnhance, ImageFilter
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs' / 'ai_robots_montage'
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path('/tmp/ai_robot_contextual')
TMP.mkdir(parents=True, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1280, 720, 20
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

GYM = Path('/tmp/GymRob/docs/_static/videos')
REAL = Path('/tmp/RealRobot/asserts/demos/low_cost_robot')
OSR = Path('/tmp/osr/images/osr-onshape.gif')

SEGMENTS = [
    {'kind':'title','title':'ROBÔS REAIS + IA EM AÇÃO','sub':'montagem contextual com vários trechos e habilidades diferentes','duration':6},
    {'kind':'title','title':'1. ROBÔS REAIS DE BAIXO CUSTO','sub':'tarefas físicas executadas por sistemas treinados em robôs reais','duration':4},
    {'kind':'gif','path':REAL/'pick.gif','title':'ROBÔ REAL: PEGAR OBJETOS','sub':'percepção, controle do braço e precisão para alcançar e pegar', 'source':'RealRobot — MIT', 'duration':10},
    {'kind':'gif','path':REAL/'stack.gif','title':'ROBÔ REAL: EMPILHAR','sub':'coordenação para posicionar objetos com estabilidade', 'source':'RealRobot — MIT', 'duration':10},
    {'kind':'gif','path':REAL/'fold.gif','title':'ROBÔ REAL: DOBRAR / MANIPULAR','sub':'manipulação de objetos deformáveis e sequência de ações', 'source':'RealRobot — MIT', 'duration':10},

    {'kind':'title','title':'2. MÃOS E MANIPULADORES ROBÓTICOS','sub':'habilidades finas: abrir, empurrar, pegar, tocar e ajustar', 'duration':4},
    {'kind':'gif','path':GYM/'adroit_hand/adroit_door.gif','title':'MÃO ROBÓTICA ABRINDO PORTA','sub':'controle de dedos, pulso e força para completar uma tarefa', 'source':'Gymnasium-Robotics — MIT', 'duration':9},
    {'kind':'gif','path':GYM/'adroit_hand/adroit_hammer.gif','title':'ROBÔ USANDO FERRAMENTA','sub':'aprendizado por reforço para executar movimentos com objetivo', 'source':'Gymnasium-Robotics — MIT', 'duration':9},
    {'kind':'gif','path':GYM/'fetch/pick_and_place.gif','title':'PEGAR E COLOCAR','sub':'planejamento de trajetória e manipulação precisa', 'source':'Gymnasium-Robotics — MIT', 'duration':9},
    {'kind':'gif','path':GYM/'fetch/push.gif','title':'EMPURRAR COM PLANEJAMENTO','sub':'o robô altera o estado do ambiente para cumprir uma meta', 'source':'Gymnasium-Robotics — MIT', 'duration':9},
    {'kind':'gif','path':GYM/'shadow_dexterous_hand/manipulate_block_touch_sensors.gif','title':'SENSORES TÁTEIS','sub':'feedback de toque ajuda a corrigir movimentos em tempo real', 'source':'Gymnasium-Robotics — MIT', 'duration':9},

    {'kind':'title','title':'3. AUTONOMIA, NAVEGAÇÃO E CORPO INTEIRO','sub':'robôs que exploram, planejam rotas e se movem sozinhos', 'duration':4},
    {'kind':'gif','path':GYM/'maze/ant_maze.gif','title':'ROBÔ QUADRÚPEDE EM LABIRINTO','sub':'navegação autônoma, exploração e tomada de decisão', 'source':'Gymnasium-Robotics — MIT', 'duration':10},
    {'kind':'gif','path':GYM/'franka_kitchen/franka_kitchen.gif','title':'BRAÇO ROBÓTICO EM AMBIENTE DOMÉSTICO','sub':'sequência de tarefas em cozinha: abrir, mover, acionar', 'source':'Gymnasium-Robotics — MIT', 'duration':10},
    {'kind':'gif','path':OSR,'title':'ROVER: DESIGN E MOBILIDADE','sub':'plataforma robótica aberta inspirada em rovers de Marte', 'source':'NASA/JPL Open Source Rover — Apache-2.0', 'duration':8},

    {'kind':'title','title':'4. ONDE A IA ENTRA','sub':'visão, linguagem, planejamento, diagnóstico, criação e automação', 'duration':4},
    {'kind':'image','path':OUT/'scene01.png','title':'IA ORQUESTRA SISTEMAS','sub':'modelos analisam dados, planejam ações e coordenam operações', 'source':'Cena gerada para contextualização', 'duration':8},
    {'kind':'image','path':OUT/'scene04.png','title':'IA NA SAÚDE','sub':'apoio a diagnóstico, triagem, robótica cirúrgica e análise de imagens', 'source':'Cena gerada para contextualização', 'duration':8},
    {'kind':'image','path':OUT/'scene08.png','title':'IA CRIATIVA E PRODUTIVA','sub':'geração de código, design, conteúdo, simulações e interfaces', 'source':'Cena gerada para contextualização', 'duration':8},
    {'kind':'image','path':OUT/'scene03.png','title':'ROBÔS INDUSTRIAIS COM IA','sub':'automação, inspeção, qualidade e produção em escala', 'source':'Cena gerada para contextualização', 'duration':8},

    {'kind':'title','title':'CONTEXTO FINAL','sub':'IA decide e aprende; robôs percebem, navegam e executam no mundo físico', 'duration':7},
]

def ensure_sources():
    missing=[]
    for s in SEGMENTS:
        if s.get('path') and not Path(s['path']).exists(): missing.append(str(s['path']))
    if missing:
        raise FileNotFoundError('Fontes não encontradas:\n'+'\n'.join(missing))

def fnt(size, bold=False): return ImageFont.truetype(FONT_BOLD if bold else FONT, size)

def run(cmd):
    print('RUN', ' '.join(map(str, cmd[:8])), '...')
    subprocess.check_call(cmd)

def draw_text(draw, xy, msg, font, fill=(255,255,255,255), stroke=2, anchor=None):
    draw.text(xy, msg, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0,0,0,230), anchor=anchor)

def centered(draw, y, msg, font, fill):
    box=draw.textbbox((0,0), msg, font=font)
    draw_text(draw, ((W-(box[2]-box[0]))//2,y), msg, font, fill, 3)

def tech_bg(t):
    img=Image.new('RGB',(W,H),(5,8,18)); d=ImageDraw.Draw(img,'RGBA')
    for y in range(0,H,6):
        r=int(5+20*y/H+10*math.sin(t*1.4+y/70)); g=int(10+22*y/H+8*math.cos(t*1.2+y/85)); b=int(32+65*y/H)
        d.rectangle((0,y,W,y+6), fill=(r,g,b,255))
    for i in range(45):
        x=int((i*113+t*75)%(W+200)-100); y=int((i*67+math.sin(t+i)*100)%(H+160)-80)
        col=(0,220,255,36) if i%2 else (160,80,255,30)
        d.ellipse((x-42,y-42,x+42,y+42), outline=col, width=2)
        d.line((x,y,(x+220)%W,(y+88)%H), fill=col, width=1)
    return img.convert('RGBA')

def title_frame(t,dur,title,sub):
    img=tech_bg(t); d=ImageDraw.Draw(img,'RGBA')
    d.rectangle((0,0,W,H), fill=(0,0,0,65))
    centered(d, 270, title, fnt(48, True), (255,255,255,255))
    centered(d, 350, sub, fnt(27), (90,235,255,255))
    fade=min(1,t/0.8,(dur-t)/0.8)
    if fade<1: img=Image.blend(Image.new('RGBA',(W,H),(0,0,0,255)), img, fade)
    return img.convert('RGB')

def load_gif(p):
    im=Image.open(p); frames=[]
    # sample frames if huge, to keep memory sane
    for i,fr in enumerate(ImageSequence.Iterator(im)):
        if i % 1 == 0:
            frames.append(fr.convert('RGB'))
        if len(frames) > 240: break
    return frames or [im.convert('RGB')]

def fit_video_frame(frame):
    iw,ih=frame.size
    scale_bg=max(W/iw,H/ih); bg=frame.resize((int(iw*scale_bg),int(ih*scale_bg)),Image.Resampling.LANCZOS)
    bg=bg.crop(((bg.width-W)//2,(bg.height-H)//2,(bg.width-W)//2+W,(bg.height-H)//2+H)).filter(ImageFilter.GaussianBlur(16))
    bg=ImageEnhance.Brightness(bg).enhance(0.50).convert('RGBA')
    scale=min((W*0.90)/iw,(H*0.62)/ih); fg=frame.resize((int(iw*scale),int(ih*scale)),Image.Resampling.LANCZOS).convert('RGBA')
    x=(W-fg.width)//2; y=72+(405-fg.height)//2 if fg.height<405 else 66
    shadow=Image.new('RGBA',(fg.width+28,fg.height+28),(0,0,0,0)); sd=ImageDraw.Draw(shadow,'RGBA')
    sd.rounded_rectangle((0,0,shadow.width,shadow.height), radius=18, fill=(0,0,0,135))
    bg.alpha_composite(shadow,(x-14,y-14)); bg.alpha_composite(fg,(x,y))
    return bg

def source_frame(s,n,total,idx):
    if s['kind']=='gif':
        frames=s['_frames']; base=frames[(n*2)%len(frames)]
        img=fit_video_frame(base)
    else:
        base=s['_image']; p=n/max(1,total-1); zoom=1.05+0.10*(0.5-0.5*math.cos(math.pi*p))
        iw,ih=base.size; scale=max(W/iw,H/ih)*zoom
        bg=base.resize((int(iw*scale),int(ih*scale)),Image.Resampling.LANCZOS)
        x=(bg.width-W)//2+int(math.sin(p*math.pi*1.5+idx)*min(60,max(0,bg.width-W)//2))
        y=(bg.height-H)//2+int(math.cos(p*math.pi*1.3+idx)*min(35,max(0,bg.height-H)//2))
        img=bg.crop((x,y,x+W,y+H)).convert('RGBA')
        overlay=Image.new('RGBA',(W,H),(5,12,25,45)); img=Image.alpha_composite(img,overlay)
    d=ImageDraw.Draw(img,'RGBA')
    d.rectangle((0,H-176,W,H), fill=(0,0,0,170))
    draw_text(d,(48,H-148),s['title'],fnt(38,True),(255,255,255,255),2)
    draw_text(d,(50,H-92),s['sub'],fnt(24),(235,246,255,235),1)
    d.rounded_rectangle((38,25,430,62), radius=10, fill=(0,0,0,140))
    draw_text(d,(55,31),s.get('source','Fonte aberta'),fnt(18,True),(125,238,255,230),1)
    draw_text(d,(W-42,30),f'{idx:02d}',fnt(20,True),(150,240,255,230),1,anchor='ra')
    return img.convert('RGB')

def render(video):
    cmd=[FFMPEG,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(video)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        vid_idx=0
        for s in SEGMENTS:
            dur=s['duration']; total=dur*FPS
            if s['kind']=='title':
                for n in range(total): proc.stdin.write(title_frame(n/FPS,dur,s['title'],s['sub']).tobytes())
            else:
                vid_idx+=1
                print('segment',vid_idx,s['title'])
                if s['kind']=='gif': s['_frames']=load_gif(s['path'])
                elif s['kind']=='image': s['_image']=Image.open(s['path']).convert('RGB')
                for n in range(total): proc.stdin.write(source_frame(s,n,total,vid_idx).tobytes())
                s.pop('_frames',None); s.pop('_image',None)
    finally:
        proc.stdin.close(); ret=proc.wait()
        if ret: raise SystemExit(ret)

def music(out,dur):
    # Trilha original, não usa áudio do YouTube/Short.
    cmd=[FFMPEG,'-y']; freqs=[46.25,69.3,92.5,138.6,185,277.2,370,554.4]
    for fr in freqs: cmd+=['-f','lavfi','-i',f'sine=frequency={fr}:sample_rate=44100:duration={dur}']
    filt=(
        '[0:a]volume=0.18,tremolo=f=1.7:d=0.45,lowpass=f=125[a0];'
        '[1:a]volume=0.12,tremolo=f=2.2:d=0.45,lowpass=f=245[a1];'
        '[2:a]volume=0.08,tremolo=f=4.0:d=0.55,highpass=f=70,lowpass=f=650[a2];'
        '[3:a]volume=0.055,tremolo=f=5.5:d=0.40,adelay=180|180[a3];'
        '[4:a]volume=0.038,tremolo=f=7.8:d=0.52,adelay=360|360[a4];'
        '[5:a]volume=0.027,tremolo=f=10.5:d=0.46,adelay=540|540[a5];'
        '[6:a]volume=0.019,tremolo=f=12.5:d=0.42,adelay=720|720[a6];'
        '[7:a]volume=0.013,tremolo=f=15:d=0.40,adelay=900|900[a7];'
        '[a0][a1][a2][a3][a4][a5][a6][a7]amix=inputs=8:duration=longest,'
        'acompressor=threshold=-18dB:ratio=3:attack=15:release=180,'
        f'afade=t=in:st=0:d=2,afade=t=out:st={max(dur-4,0)}:d=4[a]'
    )
    cmd+=['-filter_complex',filt,'-map','[a]','-c:a','aac','-b:a','160k',str(out)]
    run(cmd)

def mux(video,audio,final):
    run([FFMPEG,'-y','-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-shortest','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)])

def main():
    ensure_sources()
    dur=sum(s['duration'] for s in SEGMENTS)
    video=TMP/'contextual_silent.mp4'; audio=TMP/'contextual_music.m4a'
    final=OUT/'video_ia_robos_contextual_varios_clipes.mp4'
    render(video); music(audio,dur+1); mux(video,audio,final)
    shutil.copy2(final,ROOT/'VIDEO_FINAL_IA_ROBOS_VARIOS_CLIPES.mp4')
    (OUT/'CREDITOS_CONTEXTUAL.md').write_text(
        '# Créditos — vídeo contextual com vários clipes\n\n'
        f'Duração aproximada: {dur//60}min{dur%60:02d}s.\n\n'
        'Não foi usada a música do Short do YouTube porque o usuário informou que não possui licença. A trilha é original/sintetizada.\n\n'
        'Fontes abertas usadas no MP4:\n'
        '- HaoyiZhu/RealRobot — MIT — clipes reais de robô de baixo custo: pick, stack, fold.\n'
        '- Farama-Foundation/Gymnasium-Robotics — MIT — demos em movimento de manipulação, mãos robóticas, Fetch, Franka e Ant Maze.\n'
        '- nasa-jpl/open-source-rover — Apache-2.0 — visual do rover open-source.\n\n'
        'Além disso, foram usadas cenas geradas no projeto apenas para contextualizar capacidades de IA em saúde, indústria, criação e coordenação de sistemas.\n', encoding='utf-8')
    print('FINAL',final,'COPY',ROOT/'VIDEO_FINAL_IA_ROBOS_VARIOS_CLIPES.mp4','DURATION',dur)
if __name__=='__main__': main()
