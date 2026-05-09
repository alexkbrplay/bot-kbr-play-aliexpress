#!/usr/bin/env python3
"""
FILTRO FINAL - AliExpress Bot
Versão: 3.0
Data: 2026-05-08
Baseado em análise real de 2.000+ produtos
"""

import re
from typing import Dict, Any, List, Tuple


class FiltroAli:
    """
    Filtro de qualidade para produtos do AliExpress
    """
    
    def __init__(self):
        # ==========================================
        # CONFIGURAÇÕES GERAIS
        # ==========================================
        self.PRECO_MINIMO = 15.0           # Produtos abaixo disso são bloqueados
        self.SSD_PRECO_MINIMO = 30.0       # SSD/HD abaixo disso é falso
        self.SCORE_MINIMO = 25              # Score mínimo para aprovação
        
        # ==========================================
        # PALAVRAS DE BLOQUEIO (LIXO IDENTIFICADO)
        # ==========================================
        self.palavras_bloqueio = {
            # Capas de AirPods e fones
            'airpods? case', 'airpods? cover', 'earphone case', 'earphone cover',
            'bluetooth earphone case', 'wireless earphone case', 'headphone case',
            'earbuds case', 'earpods case', 'headset case',
            
            # Almofadas e reposição de fones
            'replacement ear pads', 'replacement earpads', 'ear cushion',
            'earmuffs', 'ear pads for', 'earpad for', 'ear cushion for',
            'replacement foam ear', 'memory foam ear', 'gel earpads',
            'headband cushion', 'replacement headband', 'earpads replacement',
            'replacement ear', 'ear pads replacement', 'cushion cover',
            
            # Peças de reposição (fones)
            'replacement mic', 'replacement microphone', 'replacement cable',
            'replacement volume controller', 'replacement aux',
            
            # Testadores e ferramentas genéricas
            'tester', 'testador', 'diagnosis', 'diagnostic', 'multimeter',
            
            # Lâmpadas smart
            'smart bulb', 'smart lamp', 'led bulb', 'rgb light', 'smart light',
            'emergency light', 'solar light', 'motion sensor light',
            'night light', 'led lamp', 'ceiling light', 'floodlight',
            'pendant light', 'led strip', 'rgbw light', 'filament bulb',
            
            # Tomadas inteligentes
            'smart socket', 'smart plug', 'wifi socket', 'tuya socket',
            'zigbee socket', 'smart power strip', 'smart outlet',
            'wall socket', 'usb socket', 'extension cord', 'power strip',
            
            # Relógios genéricos
            'smart watch', 'smartwatch', 'fitness tracker', 'activity tracker',
            'addiesdive', 'olevs', 'megir', 'playboy watch', 'ciloa',
            'quartz watch', 'automatic watch', 'chronograph',
            
            # Ventoinhas genéricas
            'cooling fan', 'usb fan', 'desk fan', 'mini fan', 'cpu fan',
            'gpu fan', 'radiator fan', 'cooler fan', 'case fan',
            'xuanfeng', 'adegrees',
            
            # Peças de reposição (PC)
            'replacement cpu', 'cpu bracket', 'cpu backplate', 'cpu holder',
            'water block', 'cpu water block', 'bykski', 'barrow', 'syscooling',
            'lga socket', 'am4 socket', 'cpu socket', 'bga socket',
            'granzon', 'lanshuo',
            
            # Acessórios automotivos
            'car dashboard mat', 'bike mount', 'bicycle mount',
            'car mount', 'headlight bracket', 'car adapter',
            'auto stop canceller', 'power liftgate', 'spark plug',
            'canbus box', 'decoder', 'dash cam', 'dvr', 'video recorder',
            
            # Cabos genéricos
            'usb cable', 'type c cable', 'charging cable', 'data cable',
            'hdmi cable', 'displayport cable', 'extension cable',
            'sata cable', 'power cable', 'adapter cable', 'converter',
            'dongle', 'splitter', 'connector',
            
            # Stickers e adesivos
            'sticker', 'decal', 'skin', 'vinyl', 'adhesive', 'grip tape',
            
            # Áudio genérico
            'wireless headset', 'bluetooth headset', 'over ear headphone',
            'earhook headphone', 'karaoke', 'lavalier', 'walkie talkie',
            'hearing aid',
            
            # CarPlay/Android Auto adapters
            'carplay adapter', 'android auto adapter', 'carplay ai box',
            'wireless carplay', 'android tv box car', 'ottocast',
            'carlinkit', 'car ai box', 'carplay dongle',
            
            # Mini PCs white label
            'kamrui', 'texhoo', 'zxipc', 'forgenmachine', 'genmachine',
            'bebepec', 'xcj', 'jginyue', 'huananzhi', 'topton', 'firebat',
            'beelink', 'aoostar', 'trigkey',
            
            # Protetores de tela
            'screen protector', 'tempered glass', 'película', 'hydrogel',
            'glass protector', 'shatterproof',
        }
        
        # ==========================================
        # PALAVRAS DE APROVAÇÃO (SOBRESCREVE BLOQUEIO)
        # ==========================================
        self.palavras_aprovacao = {
            # SSDs legítimos
            'samsung ssd', 'kingston ssd', 'wd ssd', 'crucial ssd',
            'samsung 970 evo', 'samsung 870 evo', 'kingston nv',
            'samsung 980', 'samsung 990', 'wd black',
            
            # RAM legítima
            'hyperx fury', 'hyperx beast', 'kingston fury',
            'samsung ram', 'samsung memory', 'kingston ram',
            'corsair vengeance', 'corsair dominator',
            
            # Fones entusiastas
            'eardeco', 'cca', 'kbear', 'fifine', 'kz', 'epz', 'xinhs',
            
            # Ações e acessórios de qualidade
            'action camera', 'dji', 'insta360', 'gopro',
            
            # Automação de qualidade
            'broadlink',
            
            # Mouse pads (aprovados)
            'mouse pad', 'mousepad', 'desk mat', 'gaming mouse pad',
        }
        
        # ==========================================
        # PALAVRAS DE ÁUDIO ACEITÁVEL (SE FOR GAMING)
        # ==========================================
        self.palavras_audio_aceitavel = {
            'gaming headset', 'gaming headphones', 'gaming earphone',
        }
        
        # Compila regex para eficiência
        self.regex_bloqueio = re.compile('|'.join(self.palavras_bloqueio), re.IGNORECASE)
        self.regex_aprovacao = re.compile('|'.join(self.palavras_aprovacao), re.IGNORECASE)
        self.regex_audio = re.compile('|'.join(self.palavras_audio_aceitavel), re.IGNORECASE)
    
    # ==========================================
    # MÉTODOS DE VERIFICAÇÃO
    # ==========================================
    
    def verificar_preco(self, preco: float, desconto: int) -> Tuple[bool, str]:
        """Verifica se o preço é aceitável"""
        if preco < self.PRECO_MINIMO:
            return False, f"Preço R${preco:.2f} abaixo do mínimo R${self.PRECO_MINIMO}"
        
        if desconto > 80:
            return False, f"Desconto suspeito de {desconto}%"
        
        return True, ""
    
    def verificar_ssd_falso(self, titulo: str, preco: float) -> Tuple[bool, str]:
        """Verifica se é um SSD/HD falso"""
        titulo_lower = titulo.lower()
        
        if 'ssd' in titulo_lower or 'hdd' in titulo_lower or 'hard disk' in titulo_lower:
            if preco < self.SSD_PRECO_MINIMO:
                return False, f"SSD/HD por R${preco:.2f} (abaixo de R${self.SSD_PRECO_MINIMO})"
            
            # Capacidades suspeitas (2TB+ por preço baixo)
            capacidades = re.findall(r'(\d+)(?:tb|pb)', titulo_lower)
            for cap in capacidades:
                if int(cap) >= 2 and preco < 200:
                    return False, f"Capacidade {cap}TB suspeita para preço R${preco:.2f}"
        
        return True, ""
    
    def verificar_audio_generico(self, titulo: str, preco: float) -> Tuple[bool, str]:
        """Verifica se é áudio genérico (não-gaming) barato"""
        titulo_lower = titulo.lower()
        
        # Se for gaming, libera
        if self.regex_audio.search(titulo_lower):
            return True, ""
        
        # Marcas boas de áudio
        marcas_boas = ['eardeco', 'cca', 'kbear', 'fifine', 'kz', 'epz', 'xinhs', 'sony', 'bose', 'jbl']
        if any(marca in titulo_lower for marca in marcas_boas):
            return True, ""
        
        # Palavras que indicam áudio genérico
        palavras_audio = ['earphone', 'headphone', 'earbud', 'headset', 'fone']
        if any(palavra in titulo_lower for palavra in palavras_audio) and preco < 50:
            return False, f"Áudio genérico por R${preco:.2f} (marca desconhecida)"
        
        return True, ""
    
    def verificar_repeticao(self, titulo: str, historico: List[str]) -> Tuple[bool, str]:
        """Verifica se produto similar já foi enviado"""
        titulo_simples = re.sub(r'[^a-z0-9]', '', titulo.lower())
        
        for anterior in historico:
            anterior_simples = re.sub(r'[^a-z0-9]', '', anterior.lower())
            if len(titulo_simples) > 20 and len(anterior_simples) > 20:
                if titulo_simples in anterior_simples or anterior_simples in titulo_simples:
                    return False, "Produto similar já enviado antes"
        
        return True, ""
    
    # ==========================================
    # CÁLCULO DE SCORE
    # ==========================================
    
    def calcular_score(self, produto: Dict[str, Any]) -> int:
        """Calcula score baseado em múltiplos fatores"""
        score = 0
        titulo = produto.get('title', '').lower()
        preco = produto.get('price', 0)
        desconto = produto.get('discount', 0)
        vendas = produto.get('sold_quantity', 0)
        frete_gratis = produto.get('free_shipping', False)
        ship_from = produto.get('ship_from', '')
        
        # Desconto (20-60% é ideal)
        if 20 <= desconto <= 60:
            score += 20
        elif 60 < desconto <= 80:
            score += 10
        elif desconto > 80:
            score -= 10
        
        # Preço (faixas razoáveis)
        if 30 <= preco <= 100:
            score += 15
        elif 100 < preco <= 250:
            score += 10
        elif 250 < preco <= 500:
            score += 5
        elif preco < 20:
            score -= 15
        elif preco > 500:
            score -= 10
        
        # Vendas (popularidade)
        if vendas >= 500:
            score += 20
        elif vendas >= 100:
            score += 12
        elif vendas >= 30:
            score += 6
        
        # Bônus
        if frete_gratis:
            score += 10
        
        if 'BR' in ship_from.upper():
            score += 20
        
        # Palavras de aprovação
        if self.regex_aprovacao.search(titulo):
            score += 25
        
        # Palavras de bloqueio reduzem score
        if self.regex_bloqueio.search(titulo):
            score -= 40
        
        return max(-10, min(score, 100))
    
    # ==========================================
    # MÉTODO PRINCIPAL
    # ==========================================
    
    def filtrar(self, produto: Dict[str, Any], historico: List[str] = None) -> Tuple[bool, str]:
        """
        Função principal de filtro
        Retorna: (aprovado, motivo)
        """
        if historico is None:
            historico = []
        
        titulo = produto.get('title', '')
        preco = produto.get('price', 0)
        desconto = produto.get('discount', 0)
        
        # 1. Verifica palavras de aprovação (sobrescreve bloqueios)
        if self.regex_aprovacao.search(titulo.lower()):
            repetido, motivo = self.verificar_repeticao(titulo, historico)
            if not repetido:
                return True, "Produto aprovado por palavras-chave positivas"
            return False, motivo
        
        # 2. Verifica palavras de bloqueio
        if self.regex_bloqueio.search(titulo.lower()):
            return False, "Filtro bloqueou (categoria excluída)"
        
        # 3. Verifica SSD/HD falso
        ok, motivo = self.verificar_ssd_falso(titulo, preco)
        if not ok:
            return False, motivo
        
        # 4. Verifica áudio genérico
        ok, motivo = self.verificar_audio_generico(titulo, preco)
        if not ok:
            return False, motivo
        
        # 5. Verifica preço
        ok, motivo = self.verificar_preco(preco, desconto)
        if not ok:
            return False, motivo
        
        # 6. Calcula score
        score = self.calcular_score(produto)
        if score < self.SCORE_MINIMO:
            return False, f"Score {score} abaixo do mínimo {self.SCORE_MINIMO}"
        
        # 7. Verifica repetição
        ok, motivo = self.verificar_repeticao(titulo, historico)
        if not ok:
            return False, motivo
        
        return True, f"Aprovado (score: {score})"


# ==========================================
# INSTÂNCIA GLOBAL E FUNÇÃO DE INTERFACE
# ==========================================

_filtro_global = FiltroAli()


def filtrar_produto(produto: Dict[str, Any], historico: List[str] = None) -> bool:
    """Interface simplificada para o bot (mantém compatibilidade)"""
    aprovado, _ = _filtro_global.filtrar(produto, historico)
    return aprovado