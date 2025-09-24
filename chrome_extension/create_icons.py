#!/usr/bin/env python3
"""
Script para criar ícones da extensão Chrome Symplifika
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Cria um ícone da extensão Symplifika"""
    
    # Criar imagem com fundo gradiente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cores do Symplifika (gradiente azul/roxo)
    center = size // 2
    
    # Desenhar círculo de fundo com gradiente
    for i in range(center):
        alpha = int(255 * (1 - i / center))
        color1 = (102, 126, 234, alpha)  # Azul Symplifika
        color2 = (118, 75, 162, alpha)   # Roxo Symplifika
        
        # Misturar cores para gradiente
        ratio = i / center
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        
        draw.ellipse([center - i, center - i, center + i, center + i], 
                    fill=(r, g, b, alpha))
    
    # Desenhar símbolo "S" estilizado no centro
    font_size = size // 3
    try:
        # Tentar usar fonte do sistema
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        # Fallback para fonte padrão
        font = ImageFont.load_default()
    
    # Desenhar "S" branco no centro
    text = "S"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 2  # Ajuste vertical
    
    # Sombra do texto
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 128))
    # Texto principal
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # Salvar ícone
    img.save(output_path, 'PNG')
    print(f"✅ Ícone {size}x{size} criado: {output_path}")

def main():
    """Criar todos os ícones necessários"""
    
    # Criar diretório de ícones
    icons_dir = "icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Tamanhos necessários para extensão Chrome
    sizes = [16, 32, 48, 128]
    
    print("🎨 Criando ícones da extensão Symplifika...")
    
    for size in sizes:
        output_path = os.path.join(icons_dir, f"icon{size}.png")
        create_icon(size, output_path)
    
    print("\n🎉 Todos os ícones criados com sucesso!")
    print("📁 Localização: chrome_extension/icons/")
    print("\n📋 Ícones criados:")
    for size in sizes:
        print(f"  - icon{size}.png ({size}x{size})")

if __name__ == "__main__":
    main()
