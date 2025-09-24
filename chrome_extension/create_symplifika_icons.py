#!/usr/bin/env python3
"""
Script para criar ícones da extensão Chrome com as cores corretas do Symplifika
"""

import os

def create_symplifika_svg_icon(size, output_path):
    """Cria um ícone SVG da extensão com as cores do Symplifika"""
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradiente principal do Symplifika -->
    <linearGradient id="symplifikaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00ff57;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00c853;stop-opacity:1" />
    </linearGradient>
    
    <!-- Padrão mesh de fundo -->
    <pattern id="meshPattern" x="0" y="0" width="12" height="12" patternUnits="userSpaceOnUse">
      <g fill="none" fill-rule="evenodd">
        <g fill="#ffffff" fill-opacity="0.1">
          <path d="M7 7v-1h-1v1h-1v1h1v1h1v-1h1v-1h-1zm0-6V0h-1v1h-1v1h1v1h1V2h1V1h-1zM1 7v-1H0v1H0v1h1v1h1v-1h1v-1H1zM1 1V0H0v1H0v1h1v1h1V2h1V1H1z"/>
        </g>
      </g>
    </pattern>
    
    <!-- Sombra -->
    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.2"/>
    </filter>
  </defs>
  
  <!-- Fundo com gradiente -->
  <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 1}" fill="url(#symplifikaGrad)" filter="url(#shadow)"/>
  
  <!-- Padrão mesh -->
  <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 1}" fill="url(#meshPattern)"/>
  
  <!-- Letra S estilizada -->
  <text x="{size//2}" y="{size//2 + size//6}" 
        font-family="Poppins, Arial, sans-serif" 
        font-size="{size//2.2}" 
        font-weight="700" 
        text-anchor="middle" 
        fill="white"
        style="text-shadow: 0 1px 2px rgba(0,0,0,0.3);">S</text>
  
  <!-- Borda sutil -->
  <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 1}" 
          fill="none" 
          stroke="rgba(255,255,255,0.2)" 
          stroke-width="1"/>
</svg>'''
    
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"✅ Ícone Symplifika SVG {size}x{size} criado: {output_path}")

def main():
    """Criar todos os ícones necessários com as cores do Symplifika"""
    
    # Criar diretório de ícones
    icons_dir = "icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Tamanhos necessários para extensão Chrome
    sizes = [16, 32, 48, 128]
    
    print("🎨 Criando ícones da extensão com identidade Symplifika...")
    print("🎯 Cores: Verde claro (#00ff57) → Verde escuro (#00c853)")
    print("✨ Padrão mesh + fonte Poppins + sombras")
    
    for size in sizes:
        output_path = os.path.join(icons_dir, f"icon{size}.svg")
        create_symplifika_svg_icon(size, output_path)
    
    print("\n🎉 Todos os ícones Symplifika criados com sucesso!")
    print("📁 Localização: chrome_extension/icons/")
    print("\n📋 Ícones criados:")
    for size in sizes:
        print(f"  - icon{size}.svg ({size}x{size}) - Cores e padrão Symplifika")
    
    print("\n🔄 Próximo passo: Executar 'npm run build' para aplicar as mudanças")

if __name__ == "__main__":
    main()
