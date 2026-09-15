from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def verificar_cor_pixel(pixel, cor_alvo, tolerancia):
    """Auxiliar para checar se a cor do pixel atende à cor alvo dentro da tolerância."""
    r, g, b = pixel[:3]
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_cruz(imagem, cor_alvo, tolerancia=15):
    """
    Procura o padrão em cruz nas colunas 1026 a 1033 na cor especificada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    x_inicio, x_fim = 1026, 1033
    largura_faixa = (x_fim - x_inicio) + 1  # 8 pixels
    altura_cruz = largura_faixa            # 8 pixels (mesma altura da largura)
    meio_x = x_inicio + (largura_faixa // 2) - 1 # Ponto central vertical da cruz
    
    posicoes_corte = []
    
    y = 0
    while y <= altura - altura_cruz:
        cruz_encontrada = True
        linha_centro = y + (altura_cruz // 2)
        
        # 1. Checa a faixa horizontal (linha central da cruz, cobrindo de x_inicio até x_fim)
        for x in range(x_inicio, x_fim + 1):
            if not verificar_cor_pixel(pixels[x, linha_centro], cor_alvo, tolerancia):
                cruz_encontrada = False
                break
        
        # 2. Checa a faixa vertical no meio (cobrindo a altura inteira na coluna central)
        if cruz_encontrada:
            for dy in range(altura_cruz):
                if not verificar_cor_pixel(pixels[meio_x, y + dy], cor_alvo, tolerancia):
                    cruz_encontrada = False
                    break
        
        if cruz_encontrada:
            # Corta 14 pixels acima de onde o padrão começa
            posicao_corte = y - 18
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão em cruz encontrado em y={y}, cortando em y={posicao_corte}")
            
            # Pula o tamanho do padrão para evitar múltiplas detecções
            y += altura_cruz
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando no padrão encontrado
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_cruz(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão em cruz encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima imagem inicia a partir da posição de corte (mantendo os 14px na nova parte)
        posicao_anterior = posicao_corte
    
    # Corta a parte final restante da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo nome da imagem
    pasta_saida = "questoes"           # Substitua pela pasta de saída
    
    # Definição direta do RGB (35, 31, 32) conforme solicitado
    cor_do_padrao = (35, 31, 32)
    print(f"Cor definida: RGB{cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")