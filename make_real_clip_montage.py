#!/usr/bin/env python3
from pathlib import Path
import subprocess, math, shutil
from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageEnhance, ImageFilter
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs' / 'ai_robots_montage'
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path('/tmp/ai_robot_realclips')
TMP.mkdir(parents=True, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1280, 720, 24
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
GYM = Path('/tmp/GymRob/docs/_static/videos')

# Trechos reais de vídeo/GIF de demonstrações open-source (Gymnasium-Robotics, MIT License)
CLIPS = [
    (GYM/'adroit_hand/adroit_door.gif', 'MÃO ROBÓTICA ABRINDO PORTA', 'Manipulação fina: sensores, controle e aprendizado por reforço'),
    (GYM/'adroit_hand/adroit_hammer.gif', 'ROBÔ USANDO FERRAMENTA', 'A IA aprende sequências de ação para executar tarefas físicas'),
    (GYM/'adroit_hand/adroit_relocate.gif', 'PEGAR, MOVER E POSICIONAR', 'Coordenação de dedos robóticos em tarefas complexas'),
    (GYM/'franka_kitchen/franka_kitchen.gif', 'BRAÇO ROBÓTICO NA COZINHA', 'Robôs manipuladores executam várias etapas em ambiente doméstico'),
    (GYM/'fetch/pick_and_place.gif', 'PEGAR E COLOCAR OBJETOS', 'Robótica móvel: visão, trajetória e precisão'),
    (GYM/'fetch/push.gif', 'EMPURRAR COM PLANEJAMENTO', 'Controle inteligente para alterar o estado do mundo físico'),
    (GYM/'fetch/slide.gif', 'AÇÃO COM DINÂMICA', 'Robôs lidam com atrito, velocidade e incerteza'),
    (GYM/'shadow_dexterous_hand/manipulate_block_touch_sensors.gif', 'SENSORES TÁTEIS', 'Mãos robóticas usam toque para ajustar movimentos'),
    (GYM/'shadow_dexterous_hand/manipulate_pen.gif', 'DESTREZA ROBÓTICA', 'Manipulação contínua: girar, equilibrar e corrigir'),
    (GYM/'maze/ant_maze.gif', 'ROBÔ QUADRÚPEDE EM LABIRINTO', 'Navegação autônoma, exploração e tomada de decisão'),
]
INTRO, SCENE, OUTRO = 7, 14, 7

def fnt(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)

def run(cmd):
    print('RUN', ' '.join(map(str, cmd[:8])), '...')
    subprocess.check_call(cmd)

def text(draw, xy, s, font, fill=(255,255,255,255), stroke=2, anchor=None):
    draw.text(xy, s, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0,0,0,220), anchor=anchor)

def center_text(draw, y, s, font, fill):
    bbox = draw.textbbox((0,0), s, font=font)
    x = (W - (bbox[2]-bbox[0]))//2
    text(draw, (x,y), s, font, fill, 3)

def background(t):
    img = Image.new('RGB', (W,H), (5, 8, 20))
    d = ImageDraw.Draw(img, 'RGBA')
    for y in range(0,H,8):
        r = int(8 + 18*y/H + 9*math.sin(t*1.4+y/80))
        g = int(12 + 18*y/H + 8*math.cos(t*1.1+y/60))
        b = int(35 + 55*y/H)
        d.rectangle((0,y,W,y+8), fill=(r,g,b,255))
    for i in range(38):
        x = int((i*97 + t*88) % (W+160)-80)
        y = int((i*61 + math.sin(t+i)*100) % (H+120)-60)
        col = (0,210,255,34) if i%2 else (160,80,255,30)
        d.ellipse((x-42,y-42,x+42,y+42), outline=col, width=2)
        d.line((x,y,(x+190)%W,(y+70)%H), fill=col, width=1)
    return img.convert('RGBA')

def title_frame(t, dur, title, subtitle):
    img = background(t)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle((0,0,W,H), fill=(0,0,0,70))
    center_text(d, 270, title, fnt(54, True), (255,255,255,255))
    center_text(d, 350, subtitle, fnt(29), (80,235,255,255))
    fade = min(1, t/1.1, (dur-t)/1.1)
    if fade < 1:
        img = Image.blend(Image.new('RGBA',(W,H),(0,0,0,255)), img, fade)
    return img.convert('RGB')

def load_gif(path):
    im = Image.open(path)
    frames = []
    for fr in ImageSequence.Iterator(im):
        frames.append(fr.convert('RGB'))
    return frames

def fit_contain(frame):
    # Maintains the real clip without cropping; blurred duplicate fills the sides.
    iw, ih = frame.size
    scale_bg = max(W/iw, H/ih)
    bg = frame.resize((int(iw*scale_bg), int(ih*scale_bg)), Image.Resampling.LANCZOS)
    x = (bg.width - W)//2; y = (bg.height - H)//2
    bg = bg.crop((x,y,x+W,y+H)).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.55).convert('RGBA')
    scale = min((W*0.86)/iw, (H*0.62)/ih)
    fg = frame.resize((int(iw*scale), int(ih*scale)), Image.Resampling.LANCZOS).convert('RGBA')
    canvas = bg
    px = (W - fg.width)//2
    py = 72 + (int(420 - fg.height)//2 if fg.height < 420 else 0)
    shadow = Image.new('RGBA', (fg.width+24, fg.height+24), (0,0,0,0))
    sd = ImageDraw.Draw(shadow,'RGBA')
    sd.rounded_rectangle((0,0,shadow.width,shadow.height), radius=18, fill=(0,0,0,115))
    canvas.alpha_composite(shadow, (px-12, py-12))
    canvas.alpha_composite(fg, (px, py))
    return canvas

def clip_frame(frames, n, total, title, sub, idx):
    # loop through original GIF frames, speed adjusted by frame index
    src = frames[(n*2) % len(frames)]
    canvas = fit_contain(src)
    d = ImageDraw.Draw(canvas, 'RGBA')
    # top tag
    d.rounded_rectangle((38,26,360,62), radius=10, fill=(0,0,0,135))
    text(d, (55,32), 'TRECHO OPEN-SOURCE / MIT', fnt(18, True), (110,240,255,230), 1)
    text(d, (W-42, 30), f'{idx:02d}/10', fnt(20, True), (150,240,255,230), 1, anchor='ra')
    # bottom caption
    d.rectangle((0,H-170,W,H), fill=(0,0,0,165))
    text(d, (48,H-142), title, fnt(40, True), (255,255,255,255), 2)
    text(d, (50,H-82), sub, fnt(25), (232,246,255,235), 1)
    return canvas.convert('RGB')

def render_video(video_path):
    cmd = [FFMPEG, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', str(video_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for n in range(INTRO*FPS):
            proc.stdin.write(title_frame(n/FPS, INTRO, 'IA E ROBÔS EM AÇÃO', 'agora com trechos reais de demonstrações robóticas open-source').tobytes())
        for idx, (path, title, sub) in enumerate(CLIPS, 1):
            print('clip', idx, path)
            frames = load_gif(path)
            total = SCENE*FPS
            for n in range(total):
                proc.stdin.write(clip_frame(frames, n, total, title, sub, idx).tobytes())
        for n in range(OUTRO*FPS):
            proc.stdin.write(title_frame(n/FPS, OUTRO, 'O FUTURO JÁ ESTÁ EM MOVIMENTO', 'IA aprende, robôs executam, humanos ampliam possibilidades').tobytes())
    finally:
        proc.stdin.close()
        ret = proc.wait()
        if ret:
            raise SystemExit(ret)

def music(path, dur):
    # Trilha eletrônica original. Como o usuário não tem licença, não usamos a música do Short.
    cmd=[FFMPEG,'-y']
    freqs=[49,73.42,98,146.83,196,293.66,392,587.33]
    for fr in freqs:
        cmd += ['-f','lavfi','-i',f'sine=frequency={fr}:sample_rate=44100:duration={dur}']
    filt=(
        '[0:a]volume=0.18,tremolo=f=1.7:d=0.45,lowpass=f=130[a0];'
        '[1:a]volume=0.11,tremolo=f=2.2:d=0.42,lowpass=f=240[a1];'
        '[2:a]volume=0.07,tremolo=f=4.0:d=0.55,highpass=f=70,lowpass=f=600[a2];'
        '[3:a]volume=0.055,tremolo=f=5.5:d=0.38,adelay=190|190[a3];'
        '[4:a]volume=0.04,tremolo=f=7.5:d=0.50,adelay=360|360[a4];'
        '[5:a]volume=0.028,tremolo=f=10:d=0.45,adelay=540|540[a5];'
        '[6:a]volume=0.020,tremolo=f=12.5:d=0.42,adelay=720|720[a6];'
        '[7:a]volume=0.014,tremolo=f=15:d=0.40,adelay=900|900[a7];'
        '[a0][a1][a2][a3][a4][a5][a6][a7]amix=inputs=8:duration=longest,'
        'acompressor=threshold=-18dB:ratio=3:attack=15:release=180,'
        f'afade=t=in:st=0:d=2,afade=t=out:st={max(dur-4,0)}:d=4[a]'
    )
    cmd += ['-filter_complex',filt,'-map','[a]','-c:a','aac','-b:a','160k',str(path)]
    run(cmd)

def mux(video, audio, final):
    run([FFMPEG,'-y','-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-shortest','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)])

def main():
    for p,_,_ in CLIPS:
        if not p.exists():
            raise FileNotFoundError(f'Arquivo de clipe não encontrado: {p}. Rode o clone de Farama-Foundation/Gymnasium-Robotics em /tmp/GymRob')
    dur = INTRO + len(CLIPS)*SCENE + OUTRO
    video = TMP/'silent_realclips.mp4'
    audio = TMP/'trilha_original_realclips.m4a'
    final = OUT/'video_ia_robos_REAL_clipes.mp4'
    render_video(video)
    music(audio, dur+1)
    mux(video, audio, final)
    shutil.copy2(final, ROOT/'video_ia_robos_REAL_clipes.mp4')
    (OUT/'CREDITOS_REAL_CLIPES.md').write_text(
        '# Créditos da nova versão\n\n'
        f'Duração: {dur//60}min{dur%60:02d}s.\n\n'
        'Esta versão usa trechos reais em movimento de demonstrações robóticas do projeto Gymnasium-Robotics, licenciado sob MIT License.\n'
        'Repositório: https://github.com/Farama-Foundation/Gymnasium-Robotics\n\n'
        'A música do Short do YouTube NÃO foi usada, porque você informou que não possui licença. No lugar, usei trilha eletrônica original sintetizada para este vídeo.\n\n'
        'Clipes usados:\n' + '\n'.join([f'- {p.relative_to(GYM)} — {title}' for p,title,_ in CLIPS]) + '\n',
        encoding='utf-8'
    )
    print('FINAL', final, 'and', ROOT/'video_ia_robos_REAL_clipes.mp4')

if __name__ == '__main__':
    main()
