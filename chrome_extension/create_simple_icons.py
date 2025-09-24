#!/usr/bin/env python3
"""
Script simples para criar ícones da extensão Chrome Symplifika
"""

import os

def create_svg_icon(size, output_path):
    """Cria um ícone SVG da extensão Symplifika"""
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Círculo de fundo com gradiente -->
  <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 2}" fill="url(#grad1)" />
  
  <!-- Letra S estilizada -->
  <text x="{size//2}" y="{size//2 + size//6}" 
        font-family="Arial, sans-serif" 
        font-size="{size//2}" 
        font-weight="bold" 
        text-anchor="middle" 
        fill="white">S</text>
</svg>'''
    
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"✅ Ícone SVG {size}x{size} criado: {output_path}")

def main():
    """Criar todos os ícones necessários"""
    
    # Criar diretório de ícones
    icons_dir = "icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Tamanhos necessários para extensão Chrome
    sizes = [16, 32, 48, 128]
    
    print("🎨 Criando ícones SVG da extensão Symplifika...")
    
    for size in sizes:
        output_path = os.path.join(icons_dir, f"icon{size}.svg")
        create_svg_icon(size, output_path)
    
    # Criar também versões PNG simples (placeholders)
    print("\n📦 Criando placeholders PNG...")
    
    for size in sizes:
        png_path = os.path.join(icons_dir, f"icon{size}.png")
        # Criar arquivo PNG vazio como placeholder
        with open(png_path, 'wb') as f:
            # PNG mínimo válido (1x1 pixel transparente)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            f.write(png_data)
        print(f"✅ Placeholder PNG {size}x{size} criado: {png_path}")
    
    print("\n🎉 Todos os ícones criados com sucesso!")
    print("📁 Localização: chrome_extension/icons/")
    print("\n📋 Ícones criados:")
    for size in sizes:
        print(f"  - icon{size}.svg ({size}x{size}) - Ícone principal")
        print(f"  - icon{size}.png ({size}x{size}) - Placeholder")

if __name__ == "__main__":
    main()
