#!/usr/bin/env python3
"""
FILTRO FINAL - AliExpress Bot
Versão: 3.4
Data: 2026-05-09
Baseado em análise real de 4.500+ produtos
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
        # PREÇO MÍNIMO POR CATEGORIA (para detectar falsificações)
        # ==========================================
        self.preco_minimo_ram_gb = 15.0    # RAM original custa no mínimo R$15/GB
        self.preco_minimo_ssd_gb = 1.5     # SSD original custa no mínimo R$1.50/GB
        self.preco_minimo_fonte = 150.0    # Fonte original custa no mínimo R$150
        self.preco_minimo_cooler = 80.0    # Cooler original custa no mínimo R$80
        
        # ==========================================
        # MARCAS LEGÍTIMAS (para não bloquear)
        # ==========================================
        self.marcas_legitimas = {
            # Placas-mãe
            'asus', 'msi', 'gigabyte', 'asrock', 'aorus', 'rog', 'tuf',
            'huananzhi', 'jginyue', 'maxsun', 'biostar', 'evga',
            # Fontes
            'corsair', 'seasonic', 'evga', 'cooler master', 'lian li',
            'thermaltake', 'xpg', 'be quiet', 'nzxt', 'silverstone',
            # Coolers
            'noctua', 'thermalright', 'deepcool', 'arctic', 'cryorig',
            'be quiet', 'id-cooling', 'scythe',
            # SSDs
            'samsung', 'kingston', 'wd', 'crucial', 'adata', 'sandisk',
            'seagate', 'toshiba', 'hynix', 'micron',
            # Fones IEM (entusiastas)
            'kz', 'cca', 'kbear', 'fifine', 'epz', 'xinhs', 'moondrop',
            '7hz', 'simgot', 'kiwi ears', 'thieaudio', 'trn', 'tangzu',
            'celest', 'qoa', 'artti', 'whizzer', 'linsoul', 'nicehck',
            'astrotec', 'geek wold', 'kefine', 'letshuoer', 'tripowin',
            'kinera', 'audeze',
            # Outros
            'beelink', 'broadlink', 'dji', 'insta360', 'gopro',
            'xcpg', 'flykantech', 'ac infinity', 'riitop',
            'jeyi',  # Marca de acessórios SSD (cases, heatsinks)
            # Marcas bloqueadas (white label)
            'xc y', 'helorpc', 'texhoo', 'zxipc', 'forgenmachine',
            'genmachine', 'bebepec', 'topton', 'firebat', 'aoostar',
            'trigkey', 'kamrui', 'valkyrie'
        }
        
        # ==========================================
        # MARCAS WHITE LABEL (BLOQUEAR)
        # ==========================================
        self.marcas_white_label = {
            'xc y', 'helorpc', 'texhoo', 'zxipc', 'forgenmachine',
            'genmachine', 'bebepec', 'topton', 'firebat', 'aoostar',
            'trigkey', 'kamrui', 'valkyrie'
        }
        
        # ==========================================
        # PALAVRAS DE BLOQUEIO (LIXO IDENTIFICADO)
        # ==========================================
        self.palavras_bloqueio = {
            # Enclosures com tela LCD
            'enclosure.*display screen', 'digital.*enclosure', 'ssd enclosure with display',
            
            # Capas de AirPods e fones
            'airpods? case', 'airpods? cover', 'earphone case', 'earphone cover',
            'bluetooth earphone case', 'wireless earphone case', 'headphone case',
            'earbuds case', 'earpods case', 'headset case',
            
            # Carregadores de madeira (sem marca)
            'bamboo wireless charger', 'wood wireless charger', 'wooden wireless charger',
            'bamboo charger', 'wood charger',
            
            # Almofadas e reposição de fones
            'replacement ear pads', 'replacement earpads', 'ear cushion',
            'earmuffs', 'ear pads for', 'earpad for', 'ear cushion for',
            'replacement foam ear', 'memory foam ear', 'gel earpads',
            'headband cushion', 'replacement headband', 'earpads replacement',
            'replacement ear', 'ear pads replacement', 'cushion cover',
            'ear tips', 'replacement eartips',
            
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
            
            # Fans genéricos (padrão "for/compatible")
            'fan for', 'fan compatible', 'cooler for', 'cooler compatible',
            
            # Peças de reposição (PC)
            'replacement cpu', 'cpu bracket', 'cpu backplate', 'cpu holder',
            'water block', 'cpu water block', 'bykski', 'barrow', 'syscooling',
            'lga socket', 'am4 socket', 'cpu socket', 'bga socket',
            'granzon', 'lanshuo', 'foxconn', 'backplate', 'lga1700',
            
            # Acessórios automotivos
            'car dashboard mat', 'bike mount', 'bicycle mount',
            'car mount', 'headlight bracket', 'car adapter',
            'auto stop canceller', 'power liftgate', 'spark plug',
            'canbus box', 'decoder', 'dash cam', 'dvr', 'video recorder',
            'volvo xc40', 'dashboard avoid light',
            
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
            'hearing aid', 'oneodio', 'neckband', 'tws',
            
            # Cabos IEM (upgrade)
            'iem cable', 'upgrade cable', '2pin', 'mmcx', 'silver plated cable',
            '8-core', '16-core', '4-core', 'balanced cable', 'iem wire',
            
            # Keycaps e acessórios de teclado
            'keycap', 'keycaps', 'pbt keycap', 'cherry profile', 'oem profile',
            'moa profile', 'custom keycap', 'resin keycap', 'gmk keycap',
            
            # CarPlay/Android Auto adapters
            'carplay adapter', 'android auto adapter', 'carplay ai box',
            'wireless carplay', 'android tv box car', 'ottocast',
            'carlinkit', 'car ai box', 'carplay dongle',
            
            # Protetores de tela
            'screen protector', 'tempered glass', 'película', 'hydrogel',
            'glass protector', 'shatterproof',
            
            # Acessórios de câmera ação
            'for insta360', 'for gopro', 'for dji', 'telesin', 'flymile',
            'amagisn', 'action camera mount', 'selfie stick', 'tripod adapter',
            'camera cage', 'protective case for', 'dive case', 'lens guard',
            'chest mount', 'helmet mount', 'handlebar mount', 'magnetic mount',
            
            # Itens médicos
            'glucose', 'ultrasound', 'gel', 'syringe', 'insulin', 'blood',
            'ecg', 'eeg', 'fetal', 'baby monitor', 'medical', 'surgical',
            
            # Falsificações baratas
            'replacement part', 'repair part', 'spare part', 'used',
            
            # Fones white label
            'valkyrie',
        }
        
        # ==========================================
        # PALAVRAS DE APROVAÇÃO (SOBRESCREVE BLOQUEIO)
        # ==========================================
        self.palavras_aprovacao = {
            # SSDs legítimos
            'samsung ssd', 'kingston ssd', 'wd ssd', 'crucial ssd',
            'samsung 970 evo', 'samsung 870 evo', 'kingston nv',
            'samsung 980', 'samsung 990', 'wd black', 'adata xpg',
            
            # RAM legítima
            'hyperx fury', 'hyperx beast', 'kingston fury',
            'samsung ram', 'samsung memory', 'kingston ram',
            'corsair vengeance', 'corsair dominator',
            
            # Fones entusiastas (marcas boas)
            'eardeco', 'cca', 'kbear', 'fifine', 'kz', 'epz', 'xinhs',
            'moondrop', '7hz', 'simgot', 'kiwi ears', 'thieaudio',
            'trn', 'tangzu', 'celest', 'qoa', 'artti', 'whizzer',
            'linsoul', 'nicehck', 'astrotec', 'kinera', 'audeze',
            
            # Ações e acessórios de qualidade
            'action camera', 'dji', 'insta360', 'gopro',
            
            # Automação de qualidade
            'broadlink',
            
            # Mouse pads (aprovados)
            'mouse pad', 'mousepad', 'desk mat', 'gaming mouse pad',
            
            # Placas-mãe legítimas (marcas conhecidas)
            'asus rog', 'msi meg', 'gigabyte aorus', 'asrock phantom',
            'original', 'genuine',
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
    
    def extrair_capacidade_ram(self, titulo: str) -> int:
        """Extrai capacidade da RAM em GB"""
        titulo_lower = titulo.lower()
        # Procura padrões como "16gb", "32 gb", "8gb"
        match = re.search(r'(\d+)\s*(?:gb|gigabyte)', titulo_lower)
        if match:
            return int(match.group(1))
        return 0
    
    def extrair_capacidade_ssd(self, titulo: str) -> int:
        """Extrai capacidade do SSD em GB"""
        titulo_lower = titulo.lower()
        # Procura padrões como "512gb", "1tb", "2tb"
        match = re.search(r'(\d+)\s*(?:gb|tb|gigabyte|terabyte)', titulo_lower)
        if match:
            valor = int(match.group(1))
            # Se for TB, converte para GB
            if 'tb' in titulo_lower and 'tb' in match.group(0).lower():
                return valor * 1024
            return valor
        return 0
    
    def verificar_preco(self, preco: float, desconto: int) -> Tuple[bool, str]:
        """Verifica se o preço é aceitável"""
        if preco < self.PRECO_MINIMO:
            return False, f"Preço R${preco:.2f} abaixo do mínimo R${self.PRECO_MINIMO}"
        
        if desconto > 80:
            return False, f"Desconto suspeito de {desconto}%"
        
        return True, ""
    
    def verificar_ram_falsa(self, titulo: str, preco: float) -> Tuple[bool, str]:
        """Verifica se é RAM falsa (preço muito baixo para marca conhecida)"""
        titulo_lower = titulo.lower()
        
        # Verifica se é marca nobre
        marcas_nobres = ['samsung', 'kingston', 'hyperx', 'corsair', 'g.skill']
        marca_encontrada = any(marca in titulo_lower for marca in marcas_nobres)
        
        if not marca_encontrada:
            return True, ""
        
        # Extrai capacidade
        capacidade_gb = self.extrair_capacidade_ram(titulo)
        if capacidade_gb <= 0:
            return True, ""
        
        # Calcula preço por GB
        preco_por_gb = preco / capacidade_gb
        
        # Se preço por GB for menor que o mínimo, bloqueia
        if preco_por_gb < self.preco_minimo_ram_gb:
            return False, f"RAM falsa: R${preco:.2f} para {capacidade_gb}GB (R${preco_por_gb:.2f}/GB)"
        
        return True, ""
    
    def verificar_ssd_falso(self, titulo: str, preco: float) -> Tuple[bool, str]:
        """Verifica se é um SSD/HD falso"""
        titulo_lower = titulo.lower()
        
        if 'ssd' in titulo_lower or 'hdd' in titulo_lower or 'hard disk' in titulo_lower:
            if preco < self.SSD_PRECO_MINIMO:
                return False, f"SSD/HD por R${preco:.2f} (abaixo de R${self.SSD_PRECO_MINIMO})"
            
            # Verifica se é marca nobre
            marcas_nobres = ['samsung', 'kingston', 'wd', 'crucial', 'sandisk', 'seagate', 'toshiba']
            marca_encontrada = any(marca in titulo_lower for marca in marcas_nobres)
            
            if marca_encontrada:
                capacidade_gb = self.extrair_capacidade_ssd(titulo)
                if capacidade_gb > 0:
                    preco_por_gb = preco / capacidade_gb
                    if preco_por_gb < self.preco_minimo_ssd_gb:
                        return False, f"SSD falso: R${preco:.2f} para {capacidade_gb}GB (R${preco_por_gb:.2f}/GB)"
            
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
        
        # Se for marca boa, libera
        for marca in self.marcas_legitimas:
            if marca in titulo_lower:
                return True, ""
        
        # Palavras que indicam áudio genérico
        palavras_audio = ['earphone', 'headphone', 'earbud', 'headset']
        if any(palavra in titulo_lower for palavra in palavras_audio) and preco < 80:
            return False, f"Áudio genérico por R${preco:.2f} (marca desconhecida)"
        
        return True, ""
    
    def verificar_fan_generico(self, titulo: str, preco: float) -> Tuple[bool, str]:
        """Verifica se é fan genérico (sem marca, barato, com 'for/compatible')"""
        titulo_lower = titulo.lower()
        
        # Palavras que indicam fan
        palavras_fan = ['fan', 'cooler']
        if not any(palavra in titulo_lower for palavra in palavras_fan):
            return True, ""
        
        # Se tem marca conhecida, libera
        marcas_fan = ['noctua', 'arctic', 'corsair', 'cooler master', 'be quiet', 'nzxt', 'thermalright', 'silverstone', 'lian li']
        for marca in marcas_fan:
            if marca in titulo_lower:
                return True, ""
        
        # Se tem 'original' ou 'genuine', libera
        if 'original' in titulo_lower or 'genuine' in titulo_lower:
            return True, ""
        
        # Se tem 'for' ou 'compatible', bloqueia (fan genérico)
        if (' for ' in titulo_lower or ' compatible ' in titulo_lower or 'fan for' in titulo_lower) and preco < 60:
            return False, f"Fan genérico por R${preco:.2f} (sem marca)"
        
        return True, ""
    
    def verificar_cooler_generico(self, titulo: str, preco: float) -> Tuple[bool, str]:
        """Verifica se é cooler genérico sem marca"""
        titulo_lower = titulo.lower()
        
        if 'cpu cooler' not in titulo_lower:
            return True, ""
        
        # Se tem marca conhecida, libera
        marcas_cooler = ['noctua', 'thermalright', 'deepcool', 'arctic', 'cryorig', 'be quiet', 'id-cooling', 'scythe', 'cooler master', 'corsair']
        for marca in marcas_cooler:
            if marca in titulo_lower:
                return True, ""
        
        # Senão, bloqueia (cooler genérico)
        if preco < self.preco_minimo_cooler:
            return False, f"Cooler genérico sem marca por R${preco:.2f}"
        
        return True, ""
    
    def verificar_fonte_generica(self, titulo: str, preco: float) -> Tuple[bool, str]:
        """Verifica se é fonte genérica sem marca"""
        titulo_lower = titulo.lower()
        
        if 'power supply' not in titulo_lower and 'psu' not in titulo_lower:
            return True, ""
        
        # Se tem marca conhecida, libera
        marcas_fonte = ['corsair', 'seasonic', 'evga', 'cooler master', 'lian li', 'thermaltake', 'xpg', 'be quiet', 'nzxt', 'silverstone', 'msi', 'asus', 'gigabyte']
        for marca in marcas_fonte:
            if marca in titulo_lower:
                return True, ""
        
        # Senão, bloqueia (fonte genérica)
        if preco < self.preco_minimo_fonte:
            return False, f"Fonte genérica sem marca por R${preco:.2f}"
        
        return True, ""
    
    def verificar_mini_pc_genérico(self, titulo: str) -> Tuple[bool, str]:
        """Verifica se é mini PC de marca white label"""
        titulo_lower = titulo.lower()
        
        for marca in self.marcas_white_label:
            if marca in titulo_lower:
                return False, f"Mini PC marca white label: {marca}"
        
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
        
        # Marca legítima
        for marca in self.marcas_legitimas:
            if marca in titulo:
                score += 15
                break
        
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
        
        # 3. Verifica RAM falsa (CRÍTICO)
        ok, motivo = self.verificar_ram_falsa(titulo, preco)
        if not ok:
            return False, motivo
        
        # 4. Verifica SSD/HD falso
        ok, motivo = self.verificar_ssd_falso(titulo, preco)
        if not ok:
            return False, motivo
        
        # 5. Verifica áudio genérico
        ok, motivo = self.verificar_audio_generico(titulo, preco)
        if not ok:
            return False, motivo
        
        # 6. Verifica fan genérico
        ok, motivo = self.verificar_fan_generico(titulo, preco)
        if not ok:
            return False, motivo
        
        # 7. Verifica cooler genérico
        ok, motivo = self.verificar_cooler_generico(titulo, preco)
        if not ok:
            return False, motivo
        
        # 8. Verifica fonte genérica
        ok, motivo = self.verificar_fonte_generica(titulo, preco)
        if not ok:
            return False, motivo
        
        # 9. Verifica mini PC white label
        ok, motivo = self.verificar_mini_pc_genérico(titulo)
        if not ok:
            return False, motivo
        
        # 10. Verifica preço
        ok, motivo = self.verificar_preco(preco, desconto)
        if not ok:
            return False, motivo
        
        # 11. Calcula score
        score = self.calcular_score(produto)
        if score < self.SCORE_MINIMO:
            return False, f"Score {score} abaixo do mínimo {self.SCORE_MINIMO}"
        
        # 12. Verifica repetição
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