"""
Script para generar el ícono de Spectral Galileo
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Crea un ícono de 512x512 para las notificaciones."""
    
    # Tamaño del ícono
    size = 512
    
    # Crear imagen con fondo degradado oscuro
    img = Image.new('RGB', (size, size), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # Dibujar círculo de fondo (azul oscuro)
    margin = 40
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='#16213e',
        outline='#0f3460',
        width=8
    )
    
    # Dibujar círculo interno (acento)
    margin2 = 80
    draw.ellipse(
        [margin2, margin2, size - margin2, size - margin2],
        fill='#0f3460',
        outline='#53a8e2',
        width=6
    )
    
    # Dibujar símbolo de gráfico de línea (estilizado)
    # Línea de tendencia alcista
    points = [
        (150, 350),  # inicio bajo
        (200, 320),
        (250, 280),
        (300, 240),
        (350, 180),  # punto alto
    ]
    
    # Dibujar línea gruesa
    draw.line(points, fill='#53a8e2', width=12, joint='curve')
    
    # Dibujar puntos en la línea
    for x, y in points:
        draw.ellipse([x-15, y-15, x+15, y+15], fill='#00d9ff', outline='#ffffff', width=3)
    
    # Dibujar flecha hacia arriba (bullish)
    arrow_x = 380
    arrow_y = 140
    arrow_points = [
        (arrow_x, arrow_y),           # punta
        (arrow_x - 25, arrow_y + 40), # izquierda
        (arrow_x - 10, arrow_y + 40), # centro izq
        (arrow_x - 10, arrow_y + 80), # base izq
        (arrow_x + 10, arrow_y + 80), # base der
        (arrow_x + 10, arrow_y + 40), # centro der
        (arrow_x + 25, arrow_y + 40), # derecha
    ]
    draw.polygon(arrow_points, fill='#4ecca3', outline='#ffffff', width=2)
    
    # Dibujar texto "SG" (Spectral Galileo)
    try:
        # Intentar usar una fuente del sistema
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
    except:
        # Fallback a fuente por defecto
        font = ImageFont.load_default()
    
    text = "SG"
    # Calcular posición centrada del texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 20
    
    # Dibujar sombra del texto
    draw.text((text_x + 3, text_y + 3), text, fill='#000000', font=font)
    # Dibujar texto principal
    draw.text((text_x, text_y), text, fill='#ffffff', font=font)
    
    # Guardar en diferentes tamaños
    output_dir = 'assets'
    os.makedirs(output_dir, exist_ok=True)
    
    # Ícono principal (512x512)
    img.save(f'{output_dir}/icon.png', 'PNG')
    print(f"✅ Creado: {output_dir}/icon.png (512x512)")
    
    # Ícono para notificaciones (128x128)
    img_notification = img.resize((128, 128), Image.Resampling.LANCZOS)
    img_notification.save(f'{output_dir}/icon_notification.png', 'PNG')
    print(f"✅ Creado: {output_dir}/icon_notification.png (128x128)")
    
    # Ícono pequeño (64x64)
    img_small = img.resize((64, 64), Image.Resampling.LANCZOS)
    img_small.save(f'{output_dir}/icon_small.png', 'PNG')
    print(f"✅ Creado: {output_dir}/icon_small.png (64x64)")
    
    print("\n🎨 Íconos generados exitosamente!")

if __name__ == '__main__':
    create_icon()
