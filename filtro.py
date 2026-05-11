#!/usr/bin/env python3
"""
FILTRO FINAL - AliExpress Bot
Versão: 3.5
Data: 2026-05-10
Baseado em análise real de 5.000+ produtos
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
        self.PRECO_MINIMO = 15.0
        self.SSD_PRECO_MINIMO = 30.0
        self.SCORE_MINIMO = 25
        
        # ==========================================
        # PREÇO MÍNIMO POR CATEGORIA
        # ==========================================
        self.preco_minimo_ram_gb = 15.0
        self.preco_minimo_ssd_gb = 1.5
        self.preco_minimo_fonte = 150.0
        self.preco_minimo_cooler = 80.0
        
        # ==========================================
        # MARCAS LEGÍTIMAS
        # ==========================================
        self.marcas_legitimas = {
            'asus', 'msi', 'gigabyte', 'asrock', 'aorus', 'rog', 'tuf',
            'huananzhi', 'jginyue', 'maxsun', 'biostar', 'evga',
            'corsair', 'seasonic', 'cooler master', 'lian li',
            'thermaltake', 'xpg', 'be quiet', 'nzxt', 'silverstone',
            'noctua', 'thermalright', 'deepcool', 'arctic', 'cryorig',
            'id-cooling', 'scythe',
            'samsung', 'kingston', 'wd', 'crucial', 'adata', 'sandisk',
            'seagate', 'toshiba', 'hynix', 'micron',
            'kz', 'cca', 'kbear', 'fifine', 'epz', 'xinhs', 'moondrop',
            '7hz', 'simgot', 'kiwi ears', 'thieaudio', 'trn', 'tangzu',
            'celest', 'qoa', 'artti', 'whizzer', 'linsoul', 'nicehck',
            'astrotec', 'geek wold', 'kefine', 'letshuoer', 'tripowin',
            'kinera', 'audeze',
            'beelink', 'broadlink', 'dji', 'insta360', 'gopro',
            'xcpg', 'flykantech', 'ac infinity', 'riitop', 'jeyi'
        }
        
        # ==========================================
        # MARCAS WHITE LABEL (BLOQUEAR)
        # ==========================================
        self.marcas_white_label = {
            'xc y', 'helorpc', 'texhoo', 'zxipc', 'forgenmachine',
            'genmachine', 'bebepec', 'topton', 'firebat', 'aoostar',
            'trigkey', 'kamrui', 'valkyrie', 'paulkitson', 'hagibis',
            'orico', 'machinist', 'sabrent', 'ugreen', 'lemorile', 'oullx'
        }
        
        # ==========================================
        # PALAVRAS DE BLOQUEIO
        # ==========================================
        self.palavras_bloqueio = {
            'enclosure.*display screen', 'digital.*enclosure',
            'airpods? case', 'airpods? cover', 'earphone case', 'earphone cover',
            'bluetooth earphone case', 'wireless earphone case', 'headphone case',
            'earbuds case', 'earpods case', 'headset case',
            'bamboo wireless charger', 'wood wireless charger', 'wooden wireless charger',
            'replacement ear pads', 'replacement earpads', 'ear cushion',
            'earmuffs', 'ear pads for', 'earpad for', 'ear cushion for',
            'replacement foam ear', 'memory foam ear', 'gel earpads',
            'headband cushion', 'replacement headband', 'earpads replacement',
            'replacement ear', 'ear pads replacement', 'cushion cover',
            'ear tips', 'replacement eartips', 'replacement part', 'repair part',
            'replacement mic', 'replacement cable', 'spare part', 'used',
            
            # Peças de reposição com "for + marca"
            r'for\s+(?:seasonic|corsair|evga|asus|gigabyte|msi|dell|alienware|hp|lenovo|logitech|hyperx|sennheiser|marshall|steelseries)',
            
            'tester', 'testador', 'diagnosis', 'diagnostic', 'multimeter',
            'smart bulb', 'smart lamp', 'led bulb', 'rgb light', 'smart light',
            'smart socket', 'smart plug', 'wifi socket', 'tuya socket',
            'smart watch', 'smartwatch', 'fitness tracker', 'activity tracker',
            'addiesdive', 'olevs', 'megir', 'playboy watch', 'ciloa',
            'cooling fan', 'usb fan', 'desk fan', 'mini fan', 'cpu fan',
            'gpu fan', 'radiator fan', 'case fan', 'xuanfeng', 'adegrees',
            'fan for', 'fan compatible', 'cooler for', 'cooler compatible',
            'water block', 'bykski', 'barrow', 'syscooling', 'granzon', 'lanshuo',
            'lga socket', 'am4 socket', 'bga socket', 'foxconn', 'backplate',
            'car dashboard mat', 'bike mount', 'bicycle mount', 'car mount',
            'auto stop canceller', 'power liftgate', 'canbus box', 'decoder',
            'volvo xc40', 'dashboard avoid light',
            'usb cable', 'hdmi cable', 'displayport cable', 'sata cable',
            'sticker', 'decal', 'skin', 'vinyl', 'adhesive', 'grip tape',
            'wireless headset', 'bluetooth headset', 'over ear headphone',
            'iem cable', 'upgrade cable', '2pin', 'mmcx', 'silver plated cable',
            'keycap', 'keycaps', 'pbt keycap', 'custom keycap', 'gmk keycap',
            'carplay adapter', 'android auto adapter', 'ottocast', 'carlinkit',
            'screen protector', 'tempered glass', 'hydrogel', 'glass protector',
            'for insta360', 'for gopro', 'for dji', 'telesin', 'flymile',
            'glucose', 'ultrasound', 'syringe', 'insulin', 'ecg', 'eeg',
        }
        
        # ==========================================
        # PALAVRAS DE APROVAÇÃO
        # ==========================================
        self.palavras_aprovacao = {
            'samsung ssd', 'kingston ssd', 'wd ssd', 'crucial ssd',
            'samsung 970 evo', 'samsung 870 evo', 'kingston nv',
            'hyperx fury', 'kingston fury', 'corsair vengeance',
            'eardeco', 'cca', 'kbear', 'fifine', 'kz', 'moondrop',
            '7hz', 'simgot', 'kiwi ears', 'trn', 'tangzu', 'kinera', 'audeze',
            'action camera', 'dji', 'insta360', 'gopro',
            'mouse pad', 'mousepad', 'desk mat', 'gaming mouse pad',
            'asus rog', 'msi meg', 'gigabyte aorus', 'original', 'genuine'
        }
        
        # Compila regex
        self.regex_bloqueio = re.compile('|'.join(self.palavras_bloqueio), re.IGNORECASE)
        self.regex_aprovacao = re.compile('|'.join(self.palavras_aprovacao), re.IGNORECASE)
    
    # ==========================================
    # MÉTODOS PRINCIPAIS
    # ==========================================
    
    def verificar_preco(self, preco: float, desconto: int) -> Tuple[bool, str]:
        if preco < self.PRECO_MINIMO:
            return False, f"Preço R${preco:.2f} abaixo do mínimo"
        if desconto > 80:
            return False, f"Desconto suspeito de {desconto}%"
        return True, ""
    
    def verificar_ram_falsa(self, titulo: str, preco: float) -> Tuple[bool, str]:
        marcas_nobres = ['samsung', 'kingston', 'hyperx', 'corsair']
        if not any(m in titulo.lower() for m in marcas_nobres):
            return True, ""
        
        cap = re.search(r'(\d+)\s*gb', titulo.lower())
        if not cap:
            return True, ""
        
        preco_por_gb = preco / int(cap.group(1))
        if preco_por_gb < self.preco_minimo_ram_gb:
            return False, f"RAM falsa: R${preco:.2f} para {cap.group(1)}GB"
        return True, ""
    
    def verificar_ssd_falso(self, titulo: str, preco: float) -> Tuple[bool, str]:
        if 'ssd' not in titulo.lower():
            return True, ""
        if preco < self.SSD_PRECO_MINIMO:
            return False, f"SSD falso: R${preco:.2f}"
        
        if re.search(r'(\d+)\s*tb', titulo.lower()):
            cap = re.search(r'(\d+)\s*tb', titulo.lower())
            if cap and int(cap.group(1)) >= 2 and preco < 200:
                return False, f"Capacidade {cap.group(1)}TB suspeita"
        return True, ""
    
    def verificar_mini_pc_genérico(self, titulo: str) -> Tuple[bool, str]:
        for marca in self.marcas_white_label:
            if marca in titulo.lower():
                return False, f"Marca white label: {marca}"
        return True, ""
    
    def verificar_repeticao(self, titulo: str, historico: List[str]) -> Tuple[bool, str]:
        titulo_simples = re.sub(r'[^a-z0-9]', '', titulo.lower())
        for anterior in historico:
            anterior_simples = re.sub(r'[^a-z0-9]', '', anterior.lower())
            if len(titulo_simples) > 20 and len(anterior_simples) > 20:
                if titulo_simples in anterior_simples or anterior_simples in titulo_simples:
                    return False, "Produto similar já enviado"
        return True, ""
    
    def calcular_score(self, produto: Dict[str, Any]) -> int:
        score = 0
        titulo = produto.get('title', '').lower()
        preco = produto.get('price', 0)
        desconto = produto.get('discount', 0)
        vendas = produto.get('sold_quantity', 0)
        
        if 20 <= desconto <= 60:
            score += 20
        elif desconto > 80:
            score -= 10
        
        if 30 <= preco <= 100:
            score += 15
        elif preco < 20:
            score -= 15
        elif preco > 500:
            score -= 10
        
        if vendas >= 500:
            score += 20
        elif vendas >= 100:
            score += 12
        
        if produto.get('free_shipping'):
            score += 10
        if 'br' in produto.get('ship_from', '').lower():
            score += 20
        
        for marca in self.marcas_legitimas:
            if marca in titulo:
                score += 15
                break
        
        if self.regex_aprovacao.search(titulo):
            score += 25
        if self.regex_bloqueio.search(titulo):
            score -= 40
        
        return max(-10, min(score, 100))
    
    # ==========================================
    # MÉTODO PRINCIPAL
    # ==========================================
    
    def filtrar(self, produto: Dict[str, Any], historico: List[str] = None) -> Tuple[bool, str]:
        if historico is None:
            historico = []
        
        titulo = produto.get('title', '')
        preco = produto.get('price', 0)
        desconto = produto.get('discount', 0)
        
        if self.regex_aprovacao.search(titulo.lower()):
            ok, motivo = self.verificar_repeticao(titulo, historico)
            if ok:
                return True, "Aprovado por palavras positivas"
            return False, motivo
        
        if self.regex_bloqueio.search(titulo.lower()):
            return False, "Bloqueado (categoria excluída)"
        
        ok, motivo = self.verificar_ram_falsa(titulo, preco)
        if not ok:
            return False, motivo
        
        ok, motivo = self.verificar_ssd_falso(titulo, preco)
        if not ok:
            return False, motivo
        
        ok, motivo = self.verificar_mini_pc_genérico(titulo)
        if not ok:
            return False, motivo
        
        ok, motivo = self.verificar_preco(preco, desconto)
        if not ok:
            return False, motivo
        
        score = self.calcular_score(produto)
        if score < self.SCORE_MINIMO:
            return False, f"Score {score} abaixo do mínimo"
        
        ok, motivo = self.verificar_repeticao(titulo, historico)
        if not ok:
            return False, motivo
        
        return True, f"Aprovado (score: {score})"


_filtro_global = FiltroAli()


def filtrar_produto(produto: Dict[str, Any], historico: List[str] = None) -> bool:
    aprovado, _ = _filtro_global.filtrar(produto, historico)
    return aprovado