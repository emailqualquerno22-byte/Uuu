#!/usr/bin/env python3
"""
Generates a realistic newspaper front page cover image in JPEG format
about the Brazil vs Norway 2026 World Cup match.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Canvas settings
WIDTH = 1400
HEIGHT = 2000
BACKGROUND = (245, 242, 235)
INK = (20, 20, 20)
RED = (180, 30, 30)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)
BORDER_COLOR = (40, 40, 40)

# Try to load fonts; fall back gracefully
def load_font(size, bold=False):
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    candidates_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]
    candidates = candidates_bold if bold else candidates_regular
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# Load fonts
font_masthead = load_font(90, bold=True)
font_masthead_small = load_font(28, bold=False)
font_headline = load_font(64, bold=True)
font_subhead = load_font(32, bold=False)
font_section_head = load_font(26, bold=True)
font_body = load_font(22, bold=False)
font_body_bold = load_font(22, bold=True)
font_stats = load_font(20, bold=False)
font_stats_bold = load_font(20, bold=True)
font_caption = load_font(18, bold=False)
font_quote = load_font(24, bold=False)
font_quote_attribution = load_font(20, bold=False)

# Create canvas
img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
draw = ImageDraw.Draw(img)

# Helper: draw wrapped text
def draw_wrapped_text(draw, text, x, y, max_width, font, fill, line_height=None, align="left"):
    if line_height is None:
        line_height = font.getbbox("Ay")[3] + 6
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        lx = x
        if align == "center":
            lx = x + (max_width - line_w) // 2
        elif align == "right":
            lx = x + max_width - line_w
        draw.text((lx, y), line, font=font, fill=fill)
        y += line_height
    return y

# Helper: draw a horizontal rule
def draw_rule(y, thickness=2, color=BORDER_COLOR):
    draw.rectangle([(60, y), (WIDTH - 60, y + thickness)], fill=color)

# ===== TOP BAR =====
draw.rectangle([(0, 0), (WIDTH, 60)], fill=INK)
draw.text((WIDTH // 2, 18), "EDIÇÃO DE 5 DE JULHO DE 2026", font=font_masthead_small, fill=(220, 220, 220), anchor="mt")

# ===== MASTHEAD =====
masthead_y = 65
draw.text((WIDTH // 2, masthead_y), "O GLOBO ESPORTIVO", font=font_masthead, fill=INK, anchor="mt")
masthead_bottom = masthead_y + font_masthead.getbbox("O")[3] + 20
draw_rule(masthead_bottom, thickness=4)

# Date line
date_y = masthead_bottom + 10
draw.text((WIDTH // 2, date_y), "Sábado, 5 de Julho de 2026  |  Ano XLVII  |  Nº 16.842  |  R$ 5,00", font=font_masthead_small, fill=DARK_GRAY, anchor="mt")
draw_rule(date_y + 35, thickness=1)

# ===== MAIN HEADLINE AREA =====
headline_y = date_y + 50
headline_text = "NORUEGA ELIMINA BRASIL NO METLIFE: 2 A 1"
headline_w = WIDTH - 120
headline_end_y = draw_wrapped_text(draw, headline_text, 60, headline_y, headline_w, font_headline, fill=RED, line_height=76)

draw_rule(headline_end_y + 5, thickness=2)

# Subheadline
subhead_y = headline_end_y + 15
subhead_text = "Haaland marca duas vezes, Neymar despede-se da Seleção, e Brasil sofre sexta eliminação consecutiva em Copas"
subhead_end_y = draw_wrapped_text(draw, subhead_text, 60, subhead_y, WIDTH - 120, font_subhead, fill=INK, line_height=36)

draw_rule(subhead_end_y + 10, thickness=1)

# ===== SPLIT: LEFT COLUMN (main story) + RIGHT COLUMN (stats / side) =====
content_top = subhead_end_y + 20
content_bottom = HEIGHT - 80
col_gap = 30
left_x = 60
left_w = WIDTH - 120 - col_gap // 2
right_x = 60 + left_w + col_gap
right_w = WIDTH - 60 - right_x

# --- LEFT COLUMN ---
ly = content_top

# Section: Ficha Técnica
draw.text((left_x, ly), "FICHA TÉCNICA", font=font_section_head, fill=RED)
ly += 36
draw_rule(ly, thickness=1)
ly += 8

tech_lines = [
    "Brasil 1 x 2 Noruega  |  Round of 16",
    "Local: MetLife Stadium, East Rutherford, Nova Jersey (EUA)",
    "Árbitro: Clément Turpin (França)",
    "Gols: Haaland (Nor) 79', 90' | Neymar (BRA) 90+10' (pênalti)",
    "Cartão amarelo: Bruno Guimarães (BRA) 28'",
    "Pênalti perdido: Bruno Guimarães (BRA) 34' (defendido)",
]
for line in tech_lines:
    ly = draw_wrapped_text(draw, line, left_x, ly, left_w - 10, font_body, fill=INK, line_height=26)
ly += 12

# Section: A Partida
draw.text((left_x, ly), "A PARTIDA", font=font_section_head, fill=RED)
ly += 36
draw_rule(ly, thickness=1)
ly += 8

body1 = """NEW JERSEY — Em uma noite para esquecer no MetLife Stadium, o Brasil foi eliminado da Copa do Mundo de 2026 pela Noruega por 2 a 1, na noite deste sábado. A derrota aprofunda a crise da Seleção, que agora amarga a sexta eliminação consecutiva em Copas do Mundo, todas contra adversários europeus, e a pior campanha em 36 anos.

O time de Carlo Ancelotti não conseguiu impor seu futebol contra uma Noruega organizada e letal nos contra-ataques. Erling Haaland, o artilheiro nórdico, decidiu a partida com dois gols, aos 79 e 90 minutos, deixando a torcida brasileira em estado de choque.

Aos 34 minutos do primeiro tempo, o Brasil teve a chance de abrir o placar quando o árbitro marcou pênalti após toque de mão na área. Bruno Guimarães, porém, chutou para a defesa do goleiro norueguês, desperdiçando a oportunidade que poderia mudar o destino do jogo.

Na segunda etapa, a Noruega cresceu e, aos 79 minutos, Haaland recebeu lançamento em profundidade, driblou o zagueiro e finalizou sem chances para Alisson. Dez minutos depois, o mesmo Haaland ampliou após rebote de escanteio, selando a classificação nórdica."""

ly = draw_wrapped_text(draw, body1, left_x, ly, left_w - 10, font_body, fill=INK, line_height=26)
ly += 16

# Quote box
quote_box_top = ly
quote_box_bottom = quote_box_top + 140
draw.rectangle([(left_x, quote_box_top), (left_x + left_w - 10, quote_box_bottom)], fill=(240, 235, 230), outline=BORDER_COLOR, width=2)
quote_inner_y = quote_box_top + 20
quote_text = ""\"É um momento de tristeza profunda. Não consigo mais vestir essa camisa depois do que vivemos hoje."\"
qy = draw_wrapped_text(draw, quote_text, left_x + 20, quote_inner_y, left_w - 50, font_quote, fill=RED, line_height=30)
draw.text((left_x + 20, qy + 8), "— Neymar, ao deixar o campo, em coletiva", font=font_quote_attribution, fill=DARK_GRAY)
ly = quote_box_bottom + 16

# Section: Repercussão
draw.text((left_x, ly), "REPERCUSSÃO", font=font_section_head, fill=RED)
ly += 36
draw_rule(ly, thickness=1)
ly += 8

body2 = """Carlo Ancelotti, técnico da Seleção Brasileira, enfrentou duras críticas após a eliminação. A imprensa brasileira questiona o esquema tático do italiano e a ausência de soluções criativas no ataque. "Não fizemos um primeiro tempo decente e pagamos o preço", admitiu o treinador na coletiva pós-jogo.

A Confederação Brasileira de Futebol deve reunir-se na próxima semana para avaliar a continuidade do projeto. A torcida já pede mudanças, e a sombra do fracasso da Copa de 1990 — quando o Brasil também caiu nas oitavas — volta a pairar sobre a Seleção.

Com a eliminação, Neymar confirmou que não voltará a defender a camisa amarela, encerrando uma era de 12 anos na Seleção. O atacante, de 34 anos, deixa o futebol internacional com 128 gols pela Seleção e como maior artilheiro da história do Brasil.

A Noruega comemora a classificação inédita às quartas de final e enfrentará o vencedor do jogo entre Portugal e Japão, na próxima terça-feira."""

ly = draw_wrapped_text(draw, body2, left_x, ly, left_w - 10, font_body, fill=INK, line_height=26)
ly += 20

# --- RIGHT COLUMN ---
ry = content_top

# Stats box
draw.rectangle([(right_x, ry), (right_x + right_w, ry + 420)], fill=(235, 232, 225), outline=BORDER_COLOR, width=2)
stats_inner_y = ry + 20
draw.text((right_x + right_w // 2, stats_inner_y), "ESTATÍSTICAS", font=font_section_head, fill=RED, anchor="mt")
stats_inner_y += 42

stats_data = [
    ("Posse de bola", "Brasil 58%", "Noruega 42%"),
    ("Finalizações", "18", "11"),
    ("No gol", "7", "4"),
    ("Escanteios", "8", "5"),
    ("Faltas", "13", "16"),
    ("Passes certos", "642", "398"),
    ("Precisão passes", "89%", "84%"),
]

stat_x = right_x + 20
for label, bra, nor in stats_data:
    draw.text((stat_x, stats_inner_y), label, font=font_stats_bold, fill=INK)
    draw.text((stat_x + 140, stats_inner_y), bra, font=font_stats, fill=RED if "Brasil" not in bra else INK)
    draw.text((stat_x + 220, stats_inner_y), nor, font=font_stats, fill=INK)
    stats_inner_y += 26

stats_inner_y += 20

# Timeline box
draw.text((right_x + right_w // 2, stats_inner_y), "CRONOLOGIA", font=font_section_head, fill=RED, anchor="mt")
stats_inner_y += 42

timeline = [
    "0' — Início da partida",
    "28' — Cartão amarelo: Bruno Guimarães (BRA)",
    "34' — Pênalti perdido: Bruno Guimarães (BRA)",
    "45' — Fim do primeiro tempo: 0 x 0",
    "79' — Gol: Haaland (NOR) 0 x 1",
    "90' — Gol: Haaland (NOR) 0 x 2",
    "90+10' — Gol: Neymar (BRA), de pênalti 1 x 2",
    "90+12' — Fim de jogo",
]
for ev in timeline:
    draw_wrapped_text(draw, ev, right_x + 20, stats_inner_y, right_w - 40, font_stats, fill=INK, line_height=22)
    stats_inner_y += 26

stats_inner_y += 16

# Historical context box
hist_box_top = stats_inner_y
hist_box_bottom = hist_box_top + 220
draw.rectangle([(right_x, hist_box_top), (right_x + right_w, hist_box_bottom)], fill=(235, 232, 225), outline=BORDER_COLOR, width=2)
hist_inner_y = hist_box_top + 20
draw.text((right_x + right_w // 2, hist_inner_y), "CONTEXTO HISTÓRICO", font=font_section_head, fill=RED, anchor="mt")
hist_inner_y += 42

context_text = """• Sexta eliminação consecutiva da Seleção Brasileira em Copas do Mundo.
• Todas as eliminações foram contra equipes europeias.
• Pior campanha em 36 anos: eliminação nas oitavas pela primeira vez desde 1990.
• Neymar anuncia aposentadoria da Seleção após 12 anos.
• Noruega chega às quartas de final pela primeira vez na história."""

hist_inner_y = draw_wrapped_text(draw, context_text, right_x + 20, hist_inner_y, right_w - 40, font_body, fill=INK, line_height=24)

ry = hist_box_bottom + 20

# ===== BOTTOM BAR =====
bottom_y = HEIGHT - 60
draw.rectangle([(0, HEIGHT - 60), (WIDTH, HEIGHT)], fill=INK)
draw.text((WIDTH // 2, HEIGHT - 40), "www.ogloboesportivo.com.br  |  @ogloboesportivo  |  Facebook / O Globo Esportivo", font=font_masthead_small, fill=(200, 200, 200), anchor="mm")

# Save
output_path = "capa_jornal_brasil_noruega.jpg"
img.save(output_path, "JPEG", quality=95)
print(f"Saved newspaper cover to: {output_path}")
