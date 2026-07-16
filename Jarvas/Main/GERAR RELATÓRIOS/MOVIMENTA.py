"""
Script para filtrar dados de inscrições por local de curso
e criar abas separadas na mesma planilha do Google Sheets.

LÓGICA DE NORMALIZAÇÃO:
  Todos os nomes de locais passam por normalize_local() antes de qualquer
  processamento. Essa função aplica o dicionário NORMALIZACAO para:
    1. Corrigir variantes tipográficas (acento, pontuação, abreviação, sufixo).
    2. Mesclar locais que são o mesmo endereço físico com nomes diferentes.

LÓGICA DE DIVISÃO POR CURSO:
  Alguns locais físicos abrigam cursos de responsáveis diferentes.
  A função get_chave_aba() lê o curso da linha e decide a aba correta:

  MAANAIM:
    • "📑 PREPARATÓRIO ENCCEJA 2026"  → ENCCEJA  → aba: LOCAL_MAANAIM_ENCCEJA
    • Qualquer outro curso            → CHARBEL  → aba: LOCAL_MAANAIM

  INHOAÍBA (local genérico cadastrado sem nome completo):
    • Curso em CURSOS_INHOAIBA_EBENEZER  → CHARBEL → IGREJA BATISTA EBENEZER - INHOAÍBA
    • Qualquer outro curso (default)     → CHARBEL → ASSOCIAÇÃO DE MORADORES SÃO JORGE...

  COSMOS (local genérico cadastrado sem nome completo):
    • Curso em CURSOS_COSMOS_TENDA       → CHARBEL → MINISTÉRIO APOSTÓLICO TENDA DO ENCONTRO
    • Qualquer outro curso (default)     → CHARBEL → ASSEMBLEIA DE DEUS NA PAVUNA - COSMOS

MESCLAGENS CRISTIANE (novos):
  • POLO GUADALUPE - SALA 1/2/3          → ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE
  • IGREJA JARDIM MARAVILHA - GUARATIBA  → ASSEMBLEIA DE DEUS MINISTÉRIO TERRA RICA - GUARATIBA
  • IGREJA FONTE DE VIDA ETERNA - PRAÇA SECA → NÚCLEO PRAÇA SECA - PRAÇA SECA
  • POLO MADUREIRA - SALA 1/2            → PADRE MANSO - MADUREIRA
"""

import os
import gspread
import time
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

SPREADSHEET_ID = "1XcXcSNA4WYvVHqCQztCo4E-vIyohmZXE14QFFnx7l3Q"
ORIGIN_SHEET_NAME = "DADOS"

COL_DATA  = 0
COL_CURSO = 4   # coluna E
COL_LOCAL = 8   # coluna I

HEADERS = [
    'DATA', 'NOME', 'CPF', 'GÊNERO', 'CURSO', 'WHATSAPP',
    'CEP', 'EMAIL', 'LOCAL DO CURSO', 'DATA DE INÍCIO', 'HORÁRIO'
]

# =============================================================================
# DATAS DE INÍCIO FIXAS POR NÚCLEO
# =============================================================================

DATAS_INICIO_FIXAS = {
    'AMUBUA (ASSOCIAÇÃO) - SANTA CRUZ':                                      '02/06/2026',
    'ASSEMBLEIA DE DEUS NA PAVUNA - COSMOS':                                 '18/05/2026',
    'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)':          '16/05/2026',
    'ASSOCIAÇÃO DOS ARTESÃOS - ANA GONZAGA':                                 '03/06/2026',
    'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE - SANTA CRUZ':                  '13/06/2026',
    'CAMPO SOCYTE DE MANGUINHOS - MANGUINHOS':                               '25/05/2026',
    'CENTRO CULTURAL LOTTUS - MEIER':                                        '08/06/2026',
    'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA':                            '19/05/2026',
    'COZINHA COMUNITÁRIA - REALENGO':                                        '26/05/2026',
    'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CARIOCA)':                      '11/04/2026',
    'IGREJA BATISTA DE COLÉGIO - COLÉGIO':                                   '19/05/2026',
    'IGREJA BATISTA DO MANDELA - BENIFICA':                                  '29/05/2026',
    'IGREJA BATISTA EBENEZER - INHOAÍBA':                                    '11/05/2026',
    'IGREJA BATISTA MAANAIM MENDANHA - CAMPO GRANDE':                        '23/05/2026',
    'IGREJA BATISTA RIO DE PRATA - BANGU':                                   '01/06/2026',
    'IGREJA BATISTA SÃO BENTO - BANGU (SÃO BENTO)':                         '06/06/2026',
    'IGREJA EVANGÉLICA PÃO DA VIDA - CURICICA':                              '18/05/2026',
    'IGREJA METODISTA EMBARCADOS COM CRISTO - CAMPO GRANDE (RIO DA PRATA)':  '30/05/2026',
    'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL':                                   '30/05/2026',
    'MINISTÉRIO APOSTÓLICO MOVER PROFÉTICO - SENADOR CAMARÁ':                '10/06/2026',
    'MINISTÉRIO APOSTÓLICO TENDA DO ENCONTRO - COSMOS':                      '02/06/2026',
    'PREFEITURA - ALFONSO CAVALCANTI':                                       '03/06/2026',
    'QUADRA UNIDOS DE MANGUINHOS - MANGUINHOS':                              '26/05/2026',
    'REFORÇO ESCOLAR TIA DANI - MARÉ':                                       '06/06/2026',
    'RESIDENCIAL RIO SAMBA (CONDOMÍNIOS) - MENDANHA':                        '30/05/2026',
    'SALÃO DE FESTAS - PADRE MIGUEL':                                        '08/06/2026',
    'SALÃO DE FESTAS ENCANTOS MIL - SANTA CRUZ':                             '16/05/2026',
    'TIA LU - REALENGO':                                                     '06/05/2026',
    'VILA CRUZEIRO - PENHA':                                                 '23/05/2026',
    'VILA DO PINHEIRO - MARÉ':                                               '02/06/2026',
    'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE':                 '04/05/2026',
    'ASSEMBLEIA DE DEUS MINISTÉRIO TERRA RICA - GUARATIBA':                  '08/06/2026',
    'CABLOCOS - CAMPO GRANDE':                                               '08/06/2026',
    'COMUNIDADE EVANGÉLICA CHAMA DO AMOR - CAMPO GRANDE':                    '08/06/2026',
    'CONJUNTO HABITACIONAL/ASSOCIAÇÃO DE MORADORES BENTO RIBEIRO DANTAS - MARÉ': '25/05/2026',
    'CÂNDIDO MAGALHÃES - CAMPO GRANDE':                                      '25/05/2026',
    'ESTRADA CORONEL VIEIRA - IRAJÁ':                                        '11/05/2026',
    'IARAQUÃ - CAMPO GRANDE':                                                '30/04/2026',
    'NÚCLEO PRAÇA SECA - PRAÇA SECA':                                        '08/06/2026',
    'PADRE MANSO - MADUREIRA':                                               '11/05/2026',
    'PROJETO ESPERANÇA E VIDA - CAMPO GRANDE':                               '08/06/2026',
    'RIO GRANDE - JACAREPAGUÁ':                                              '11/05/2026',
    'URUCÂNIA - SANTA CRUZ':                                                 '25/05/2026',
    'VILA SÃO JORGE - COSMOS':                                               '11/05/2026',
    'ASSOCIAÇÃO AMUBUA - SANTA CRUZ':                                        '18/05/2026',
    'CASA COSTA MATOS - REALENGO':                                           '25/05/2026',
    'IGREJA ASSEMBLÉIA DE DEUS - COLÉGIO':                                   '25/05/2026',
    'IGREJA BATISTA MAANAIM MENDANHA - ENCCEJA':                             '18/05/2026',
    'IMMEC CHURCH - CAMPO GRANDE':                                           '01/06/2026',
}

# =============================================================================
# CONSTANTES DE SPLIT POR CURSO
# =============================================================================

CURSO_ENCCEJA         = '📑 PREPARATÓRIO ENCCEJA 2026'
LOCAL_MAANAIM         = 'IGREJA BATISTA MAANAIM MENDANHA - CAMPO GRANDE'
LOCAL_MAANAIM_ENCCEJA = 'IGREJA BATISTA MAANAIM MENDANHA - ENCCEJA'

LOCAL_INHOAIBA           = '__INHOAIBA__'
LOCAL_INHOAIBA_EBENEZER  = 'IGREJA BATISTA EBENEZER - INHOAÍBA'
LOCAL_INHOAIBA_ASSOC     = 'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)'
CURSOS_INHOAIBA_EBENEZER: list[str] = []

LOCAL_COSMOS            = '__COSMOS__'
LOCAL_COSMOS_ASSEMBLEIA = 'ASSEMBLEIA DE DEUS NA PAVUNA - COSMOS'
LOCAL_COSMOS_TENDA      = 'MINISTÉRIO APOSTÓLICO TENDA DO ENCONTRO - COSMOS'
CURSOS_COSMOS_TENDA: list[str] = []

# =============================================================================
# LISTAS CANÔNICAS POR RESPONSÁVEL
# =============================================================================

CHARBEL_LOCAIS = [
    'AMUBUA (ASSOCIAÇÃO) - SANTA CRUZ',
    LOCAL_COSMOS_ASSEMBLEIA,
    'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)',
    'ASSOCIAÇÃO DOS ARTESÃOS - ANA GONZAGA',
    'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE - SANTA CRUZ',
    'CAMPO SOCYTE DE MANGUINHOS - MANGUINHOS',
    'CENTRO CULTURAL LOTTUS - MEIER',
    'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA',
    'COZINHA COMUNITÁRIA - REALENGO',
    'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CARIOCA)',
    'IG. ASS. DE DEUS RESG. VALORES - ARNALDO EUGÊNIO',
    'IGREJA BATISTA DE COLÉGIO - COLÉGIO',
    'IGREJA BATISTA DO MANDELA - BENIFICA',
    LOCAL_INHOAIBA_EBENEZER,
    LOCAL_MAANAIM,
    'IGREJA BATISTA RIO DE PRATA - BANGU',
    'IGREJA BATISTA SÃO BENTO - BANGU (SÃO BENTO)',
    'IGREJA EVANGÉLICA PÃO DA VIDA - CURICICA',
    'IGREJA METODISTA EMBARCADOS COM CRISTO - CAMPO GRANDE (RIO DA PRATA)',
    'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL',
    'MINISTÉRIO APOSTÓLICO MOVER PROFÉTICO - SENADOR CAMARÁ',
    LOCAL_COSMOS_TENDA,
    'PREFEITURA - ALFONSO CAVALCANTI',
    'QUADRA UNIDOS DE MANGUINHOS - MANGUINHOS',
    'REFORÇO ESCOLAR TIA DANI - MARÉ',
    'RESIDENCIAL RIO SAMBA (CONDOMÍNIOS) - MENDANHA',
    'SALÃO DE FESTAS - PADRE MIGUEL',
    'SALÃO DE FESTAS ENCANTOS MIL - SANTA CRUZ',
    'TIA LU - REALENGO',
    'VILA CRUZEIRO - PENHA',
    'VILA DO PINHEIRO - MARÉ',
    'ASSEMBLEIA DE DEUS ADTS DE COLÉGIO - COLÉGIO',
    'ASSEMBLEIA DE DEUS ADTS MANDELA - BENFICA',
    'ASSOCIAÇÃO AMIGOS DO BARATA - REALENGO',
    'IMMEC CHURCH - CAMPO GRANDE',
]

CRISTIANE_LOCAIS = [
    # GUADALUPE: POLO SALA 1/2/3 e o nome antigo mesclam aqui
    'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',
    # GUARATIBA: IGREJA JARDIM MARAVILHA mescla aqui
    'ASSEMBLEIA DE DEUS MINISTÉRIO TERRA RICA - GUARATIBA',
    'CABLOCOS - CAMPO GRANDE',
    'CÂNDIDO MAGALHÃES - CAMPO GRANDE',
    'COMUNIDADE EVANGÉLICA CHAMA DO AMOR - CAMPO GRANDE',
    'CONJUNTO HABITACIONAL/ASSOCIAÇÃO DE MORADORES BENTO RIBEIRO DANTAS - MARÉ',
    'ESTRADA CORONEL VIEIRA - IRAJÁ',
    'IARAQUÃ - CAMPO GRANDE',
    # PRAÇA SECA: IGREJA FONTE DE VIDA ETERNA mescla aqui
    'NÚCLEO PRAÇA SECA - PRAÇA SECA',
    # MADUREIRA: POLO MADUREIRA SALA 1/2 mesclam aqui
    'PADRE MANSO - MADUREIRA',
    'PROJETO ESPERANÇA E VIDA - CAMPO GRANDE',
    'RIO GRANDE - JACAREPAGUÁ',
    'URUCÂNIA - SANTA CRUZ',
    'VILA SÃO JORGE - COSMOS',
    # REMOVIDOS (agora mesclados nos canônicos acima):
    #   Igreja JARDIM MARAVILHA - GUARATIBA → TERRA RICA
    #   POLO GUADALUPE - SALA 1/2/3         → MARECHAL HERMES
    #   POLO MADUREIRA - SALA 1/2           → PADRE MANSO
    #   IGREJA FONTE DE VIDA ETERNA         → NÚCLEO PRAÇA SECA
]

ENCCEJA_LOCAIS = [
    'ASSOCIAÇÃO AMUBUA - SANTA CRUZ',
    'CASA COSTA MATOS - REALENGO',
    'IGREJA ASSEMBLÉIA DE DEUS - COLÉGIO',
    'IGREJA BATISTA VIDA E ESPERANÇA - BANGU',
    LOCAL_MAANAIM_ENCCEJA,
]

# =============================================================================
# MAPA DE NORMALIZAÇÃO  (nome bruto → nome canônico)
# =============================================================================

NORMALIZACAO = {

    # ── CRISTIANE: mesclagens novas ───────────────────────────────────────────

    # GUADALUPE — Polo Salas + nome antigo → canônico MARECHAL HERMES
    'POLO GUADALUPE - SALA 1':          'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',
    'POLO GUADALUPE - SALA 2':          'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',
    'POLO GUADALUPE - SALA 3':          'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',
    'POLO GUADALUPE — SALA 1':          'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',
    'POLO GUADALUPE — SALA 2':          'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',
    'POLO GUADALUPE — SALA 3':          'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',

    # GUARATIBA — Igreja Jardim Maravilha → canônico TERRA RICA
    'IGREJA JARDIM MARAVILHA - GUARATIBA':
        'ASSEMBLEIA DE DEUS MINISTÉRIO TERRA RICA - GUARATIBA',
    'IGREJA JARDIM MARAVILHA — GUARATIBA':
        'ASSEMBLEIA DE DEUS MINISTÉRIO TERRA RICA - GUARATIBA',

    # PRAÇA SECA — Igreja Fonte de Vida Eterna → canônico NÚCLEO PRAÇA SECA
    'IGREJA FONTE DE VIDA ETERNA - PRAÇA SECA':
        'NÚCLEO PRAÇA SECA - PRAÇA SECA',
    'IGREJA FONTE DE VIDA ETERNA — PRAÇA SECA':
        'NÚCLEO PRAÇA SECA - PRAÇA SECA',

    # MADUREIRA — Polo Salas → canônico PADRE MANSO
    'POLO MADUREIRA - SALA 1':          'PADRE MANSO - MADUREIRA',
    'POLO MADUREIRA - SALA 2':          'PADRE MANSO - MADUREIRA',
    'POLO MADUREIRA — SALA 1':          'PADRE MANSO - MADUREIRA',
    'POLO MADUREIRA — SALA 2':          'PADRE MANSO - MADUREIRA',

    # IRAJÁ — Polo Irajá → mescla com ESTRADA CORONEL VIEIRA
    'POLO IRAJÁ — SALA 1':              'ESTRADA CORONEL VIEIRA - IRAJÁ',

    # JACAREPAGUÁ — Polo Jacarepagua → mescla com RIO GRANDE
    'POLO JACAREPAGUÁ — SALA 1':        'RIO GRANDE - JACAREPAGUÁ',

    # ── CHARBEL: mesclagens de locais físicos ─────────────────────────────────

    'ALCIDES FRANCO - GUARATIBA':
        'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA',
    'CENTRAL SOCIAL ESTRELA DA MANHÃ':
        'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA',
    'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA':
        'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA',
    'RUA ALCIDES FRANCO, Nº 175':
        'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA',

    'HERVAL ROSSANO - COSMOS':
        'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL',
    'HERVAL ROSSANO - COSMOS - CEP.: 23.066-350':
        'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL',
    'RUA HERVAL ROSSANO, LT. 26, QD. 16':
        'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL',
    'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL':
        'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL',

    'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL — COSMOS':
        'IGREJA UNIÃO EVANGÉLICA PENTECOSTAL',

    'RUA DARCY VARGAS - MARÉ':          'REFORÇO ESCOLAR TIA DANI - MARÉ',
    'RUA DARCY VARGAS - MARÊ':          'REFORÇO ESCOLAR TIA DANI - MARÉ',

    'CENTRO CULTURAL LOTTUS - MÉIER':   'CENTRO CULTURAL LOTTUS - MEIER',
    'CENTRO CULTURAL LOTTUS — MÉIER':   'CENTRO CULTURAL LOTTUS - MEIER',
    'CENTRO CULTURAL LOTTUS — MEIER':   'CENTRO CULTURAL LOTTUS - MEIER',

    'SALÃO DE FESTAS (77) - PADRE MIGUEL':  'SALÃO DE FESTAS - PADRE MIGUEL',
    'SALÃO DE FESTAS (77) — PADRE MIGUEL':  'SALÃO DE FESTAS - PADRE MIGUEL',
    'SALÃO DE FESTA - PADRE MIGUEL':        'SALÃO DE FESTAS - PADRE MIGUEL',
    'SALÃO DE FESTAS — PADRE MIGUEL':       'SALÃO DE FESTAS - PADRE MIGUEL',

    'INHOAÍBA':     LOCAL_INHOAIBA,
    'INHOAIBA':     LOCAL_INHOAIBA,
    'COSMOS':       LOCAL_COSMOS,

    'IG. METODISTA EMBARCADOS COM CRISTO - RIO DA PRATA':
        'IGREJA METODISTA EMBARCADOS COM CRISTO - CAMPO GRANDE (RIO DA PRATA)',
    'IGREJA METODISTA EMBARCADOS COM CRISTO':
        'IGREJA METODISTA EMBARCADOS COM CRISTO - CAMPO GRANDE (RIO DA PRATA)',

    'ASSOC. DE MORADORES SÃO JORGE - INHOAÍBA':
        'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)',
    'ASSOCIAÇÃO DE MORADORES SÃO JORGE':
        'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)',
    'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE':
        'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)',
    'ASSOCIAÇÃO DE MORADORES SÃO JORGE (INHOAÍBA)':
        'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)',
    'ASSOCIAÇÃO DE MORADORES SÃO JORGE — INHOAIBA':
        'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)',
    'ASSOCIAÇÃO DE MORADORES SÃO JORGE — INHOAÍBA':
        'ASSOCIAÇÃO DE MORADORES SÃO JORGE - CAMPO GRANDE (INHOAÍBA)',

    'ASSOCIAÇÃO DE MORADORES VILAR CARIOCA':
        'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CARIOCA)',
    'CRECHE TIA ANINHA':
        'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CARIOCA)',
    'CRECHE TIA ANINHA - CAMPO GRANDE':
        'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CARIOCA)',
    'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CAICOCA)':
        'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CARIOCA)',
    'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CAIOCA)':
        'CRECHE TIA ANINHA - CAMPO GRANDE (VILAR CARIOCA)',

    'IG. BATISTA EBENEZER - INHOAÍBA':                   LOCAL_INHOAIBA_EBENEZER,
    'IGREJA BATISTA EBENEZER':                           LOCAL_INHOAIBA_EBENEZER,
    'IGREJA BATISTA EBENEZER - CAMPO GRANDE':            LOCAL_INHOAIBA_EBENEZER,
    'IGREJA BATISTA EBENEZER - CAMPO GRANDE (INHOAÍBA)': LOCAL_INHOAIBA_EBENEZER,
    'IGREJA BATISTA EBENEZER - INHOAÍBA':                LOCAL_INHOAIBA_EBENEZER,
    'IGREJA BATISTA EBENEZER — INHOAIBA':                LOCAL_INHOAIBA_EBENEZER,
    'IGREJA BATISTA EBENEZER — INHOAÍBA':                LOCAL_INHOAIBA_EBENEZER,

    'IGREJA BATISTA MAANAIM':                            LOCAL_MAANAIM,
    'IGREJA BATISTA MAANAIM - CAMPO GRANDE':             LOCAL_MAANAIM,
    'IGREJA BATISTA MAANAIM - MENDANHA':                 LOCAL_MAANAIM,
    'IGREJA BATISTA MAANAIM MENDANHA - ESTRADA DO MENDANHA': LOCAL_MAANAIM,
    'IGR. BATISTA MAANAIM MENDANHA - CAMPO GRANDE':      LOCAL_MAANAIM,
    'IGREJA BATISTA MAANAIM MENDANHA — CAMPO GRANDE':    LOCAL_MAANAIM,

    'IGREJA EVANGÉLICA PÃO DA VIDA':
        'IGREJA EVANGÉLICA PÃO DA VIDA - CURICICA',
    'IGREJA EVANGÉLICA PÃO DA VIDA — CURICICA':
        'IGREJA EVANGÉLICA PÃO DA VIDA - CURICICA',

    'CAMPO SOCYTE DE MANGUINHOS':
        'CAMPO SOCYTE DE MANGUINHOS - MANGUINHOS',
    'CAMPO SOCYTE DE MANGUINHOS — MANGUINHOS':
        'CAMPO SOCYTE DE MANGUINHOS - MANGUINHOS',
    'CAMPO SOCIETY DE MANGUINHOS':
        'CAMPO SOCYTE DE MANGUINHOS - MANGUINHOS',
    'CAMPO SOCIETY DE MANGUINHOS - MANGUINHOS':
        'CAMPO SOCYTE DE MANGUINHOS - MANGUINHOS',
    'CAMPO SOCIETY DE MANGUINHOS — MANGUINHOS':
        'CAMPO SOCYTE DE MANGUINHOS - MANGUINHOS',

    'QUADRA UNIDOS DE MANGUINHOS':
        'QUADRA UNIDOS DE MANGUINHOS - MANGUINHOS',
    'QUADRA UNIDOS DE MANGUINHOS — MANGUINHOS':
        'QUADRA UNIDOS DE MANGUINHOS - MANGUINHOS',

    'MINISTÉRIO APOSTÓLICO TENDA DO ENCONTRO':          LOCAL_COSMOS_TENDA,
    'MINISTÉRIO APOSTÓLICO TENDA DO ENCONTRO — COSMOS': LOCAL_COSMOS_TENDA,
    'ASSEMBLEIA DE DEUS NA PAVUNA':                     LOCAL_COSMOS_ASSEMBLEIA,
    'ASSEMBLEIA DE DEUS NA PAVUNA — COSMOS':            LOCAL_COSMOS_ASSEMBLEIA,

    'IGREJA BATISTA SÃO BENTO - SÃO BENTO-BANGU':
        'IGREJA BATISTA SÃO BENTO - BANGU (SÃO BENTO)',
    'IGREJA BATISTA SÃO BENTO - BANGU':
        'IGREJA BATISTA SÃO BENTO - BANGU (SÃO BENTO)',
    'IGREJA BATISTA SÃO BENTO — BANGU':
        'IGREJA BATISTA SÃO BENTO - BANGU (SÃO BENTO)',

    'ASSOCIAÇÃO DOS ARTESÃOS':
        'ASSOCIAÇÃO DOS ARTESÃOS - ANA GONZAGA',
    'ASSOCIAÇÃO DOS ARTESÃOS — ANA GONZAGA':
        'ASSOCIAÇÃO DOS ARTESÃOS - ANA GONZAGA',

    'VILA DO PINHEIRO - MARÊ':          'VILA DO PINHEIRO - MARÉ',
    'VILA DO PINHEIRO — MARÉ':          'VILA DO PINHEIRO - MARÉ',

    'IGREJA BATISTA DE COLÉGIO':        'IGREJA BATISTA DE COLÉGIO - COLÉGIO',

    'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE':
        'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE - SANTA CRUZ',
    'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE — SANTA CRUZ':
        'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE - SANTA CRUZ',
    'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE — SANTA CRUZZ':
        'ASSOCIAÇÃO MORADORES CONJUNTO LIBERDADE - SANTA CRUZ',

    'AMUBUA (ASSOCIAÇÃO)':              'AMUBUA (ASSOCIAÇÃO) - SANTA CRUZ',
    'AMUBUA (ASSOCIAÇÃO) — SANTA CRUZ': 'AMUBUA (ASSOCIAÇÃO) - SANTA CRUZ',

    'RESIDENCIAL RIO SAMBA (CONDOMINIOS) - MENDANHA':
        'RESIDENCIAL RIO SAMBA (CONDOMÍNIOS) - MENDANHA',
    'RESIDENCIAL RIO SAMBA (CONDOMÍNIO) - MENDANHA':
        'RESIDENCIAL RIO SAMBA (CONDOMÍNIOS) - MENDANHA',
    'RESIDENCIAL RIO SAMBA (CONDOMÍNIOS) — MENDANHA':
        'RESIDENCIAL RIO SAMBA (CONDOMÍNIOS) - MENDANHA',
    'RESIDENCIAL RIO SAMBA — CAMPO GRANDE':
        'RESIDENCIAL RIO SAMBA (CONDOMÍNIOS) - MENDANHA',

    'IG. ASS. DE DEUS RESG, VALORES - ARNALDO EUGÊNIO':
        'IG. ASS. DE DEUS RESG. VALORES - ARNALDO EUGÊNIO',
    'IGREJA ASSEMBLEIA DE DEUS RESGATANDO VALORES':
        'IG. ASS. DE DEUS RESG. VALORES - ARNALDO EUGÊNIO',
    'ASSEMBLEIA DE DEUS ADTS DE COLÉGIO — COLÉGIO':
        'ASSEMBLEIA DE DEUS ADTS DE COLÉGIO - COLÉGIO',

    'SALÃO DE FESTAS ENCANTOS MIL':     'SALÃO DE FESTAS ENCANTOS MIL - SANTA CRUZ',
    'SALÃO DE FESTAS':                  'SALÃO DE FESTAS ENCANTOS MIL - SANTA CRUZ',
    'SALÃO DE FESTAS - SANTA CRUZ':     'SALÃO DE FESTAS ENCANTOS MIL - SANTA CRUZ',

    'PREFEITURA - CENTRO':              'PREFEITURA - ALFONSO CAVALCANTI',
    'PREFEITURA — CENTRO':              'PREFEITURA - ALFONSO CAVALCANTI',

    'IGREJA BATISTA RIO DA PRAIA - BANGU': 'IGREJA BATISTA RIO DE PRATA - BANGU',
    'IGREJA BATISTA RIO DA PRATA - BANGU': 'IGREJA BATISTA RIO DE PRATA - BANGU',
    'IGREJA BATISTA RIO DA PRATA — BANGU': 'IGREJA BATISTA RIO DE PRATA - BANGU',

    'IGREJA BATISTA DO MANDELA - BENFICA':  'IGREJA BATISTA DO MANDELA - BENIFICA',
    'IGREJA BATISTA DO MANDELA — BENFICA':  'IGREJA BATISTA DO MANDELA - BENIFICA',
    'ASSEMBLEIA DE DEUS ADTS MANDELA - BENFICA': 'IGREJA BATISTA DO MANDELA - BENIFICA',
    'ASSEMBLEIA DE DEUS ADTS MANDELA — BENFICA': 'IGREJA BATISTA DO MANDELA - BENIFICA',

    'MINISTÉRIO APOSTÓLICO MOVER PROFÉTICO — SENADOR CAMARÁ':
        'MINISTÉRIO APOSTÓLICO MOVER PROFÉTICO - SENADOR CAMARÁ',

    'CENTRO SOCIAL ESTRELA DA MANHÃ — GUARATIBA':
        'CENTRO SOCIAL ESTRELA DA MANHÃ - GUARATIBA',
    'COZINHA COMUNITÁRIA — REALENGO':
        'COZINHA COMUNITÁRIA - REALENGO',
    'REFORÇO ESCOLAR TIA DANI — MARÉ':
        'REFORÇO ESCOLAR TIA DANI - MARÉ',

    'VILA CRUZEIRO — PENHA':            'VILA CRUZEIRO - PENHA',

    'ASSOCIAÇÃO AMIGOS DO BARATA — REALENGO':
        'ASSOCIAÇÃO AMIGOS DO BARATA - REALENGO',

    'IMMEC CHURCH - CAMPO GRANDE':       'IMMEC CHURCH - CAMPO GRANDE',
    'IMMEC CHURCH — CAMPO GRANDE':       'IMMEC CHURCH - CAMPO GRANDE',

    # ── CRISTIANE: variantes tipográficas ────────────────────────────────────

    'AUGUSTO VASCONCELOS - CAMPO GRANDE':   'CABLOCOS - CAMPO GRANDE',
    'CABOCLOS - CAMPO GRANDE':              'CABLOCOS - CAMPO GRANDE',

    'IARAQUA - CAMPO GRANDE':               'IARAQUÃ - CAMPO GRANDE',
    'IARAQUÃ — CAMPO GRANDE':               'IARAQUÃ - CAMPO GRANDE',

    'ASSEMBLEIA DE DEUS MINISTÉRIO TERRA RICA':
        'ASSEMBLEIA DE DEUS MINISTÉRIO TERRA RICA - GUARATIBA',

    'CORONEL VIEIRA - IRAJÁ':               'ESTRADA CORONEL VIEIRA - IRAJÁ',
    'ESTRADA CORONEL VIERA - IRAJÁ':        'ESTRADA CORONEL VIEIRA - IRAJÁ',
    'IRAJÁ':                                'ESTRADA CORONEL VIEIRA - IRAJÁ',

    'CONJUNTO HABITACIONAL/ ASSOCIAÇÃO DE MORADORES BENTO RIBEIRO DANTAS - MARÉ':
        'CONJUNTO HABITACIONAL/ASSOCIAÇÃO DE MORADORES BENTO RIBEIRO DANTAS - MARÉ',

    'URUCANIA - SANTA CRUZ':                'URUCÂNIA - SANTA CRUZ',
    'URUCÂNIA — SANTA CRUZ':               'URUCÂNIA - SANTA CRUZ',

    'PROESPV, PROJETO ESPERANÇA E VIDA':    'PROJETO ESPERANÇA E VIDA - CAMPO GRANDE',
    'PROJETO ESPERANÇA E VIDA':             'PROJETO ESPERANÇA E VIDA - CAMPO GRANDE',
    'PROESPV - CAMPO GRANDE':              'PROJETO ESPERANÇA E VIDA - CAMPO GRANDE',
    'PROESPV':                              'PROJETO ESPERANÇA E VIDA - CAMPO GRANDE',
    'PROESPV - PROJETO ESPERANÇA E VIDA':   'PROJETO ESPERANÇA E VIDA - CAMPO GRANDE',

    'COMUNIDADE EVANGÉLICA CHAMA DO AMOR - CAMPO GRANDE':
        'COMUNIDADE EVANGÉLICA CHAMA DO AMOR - CAMPO GRANDE',

    'ESTR. DO RIO GRANDE, 4985':            'RIO GRANDE - JACAREPAGUÁ',
    'MADUREIRA':                            'PADRE MANSO - MADUREIRA',
    'MOVIMENTA RIO — GUADALUPE':            'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',
    'NÚCLEO XIII - CAMPO GRANDE':           'CÂNDIDO MAGALHÃES - CAMPO GRANDE',
    'PRAÇA SECA':                           'NÚCLEO PRAÇA SECA - PRAÇA SECA',
    'R. JOAQUIM SARMENTO, 183':             'ASSEMBLEIA DE DEUS FILIAL MARECHAL HERMES - GUADALUPE',

    # ── ENCCEJA — variantes ───────────────────────────────────────────────────
    'CASA COSTA MATOS. - REALENGO':         'CASA COSTA MATOS - REALENGO',
    'CASA COSTA MATOS — REALENGO':          'CASA COSTA MATOS - REALENGO',
    'IGREJA ASSEMBLEIA DE DEUS - COLÉGIO':  'IGREJA ASSEMBLÉIA DE DEUS - COLÉGIO',
}


def normalize_local(local_name: str) -> str:
    """Retorna o nome canônico (ou chave interna de split) do local."""
    return NORMALIZACAO.get(local_name.strip(), local_name.strip())


def get_chave_aba(row: list) -> str:
    raw_local = row[COL_LOCAL].strip() if len(row) > COL_LOCAL else ''
    curso     = row[COL_CURSO].strip() if len(row) > COL_CURSO else ''
    canonical = normalize_local(raw_local)

    if canonical == LOCAL_MAANAIM:
        return LOCAL_MAANAIM_ENCCEJA if curso == CURSO_ENCCEJA else LOCAL_MAANAIM

    if canonical == LOCAL_INHOAIBA:
        return (LOCAL_INHOAIBA_EBENEZER
                if curso in CURSOS_INHOAIBA_EBENEZER
                else LOCAL_INHOAIBA_ASSOC)

    if canonical == LOCAL_COSMOS:
        return (LOCAL_COSMOS_TENDA
                if curso in CURSOS_COSMOS_TENDA
                else LOCAL_COSMOS_ASSEMBLEIA)

    return canonical


# =============================================================================
# Cores por responsável
# =============================================================================

RESP_COLORS = {
    "CHARBEL":   {"red": 0.678, "green": 0.847, "blue": 0.902},
    "CRISTIANE": {"red": 0.714, "green": 0.902, "blue": 0.714},
    "ENCCEJA":   {"red": 1.000, "green": 0.949, "blue": 0.667},
    "OUTRO":     {"red": 1.000, "green": 0.800, "blue": 0.800},
}

RESP_COLORS_ALT = {
    "CHARBEL":   {"red": 0.565, "green": 0.753, "blue": 0.820},
    "CRISTIANE": {"red": 0.596, "green": 0.800, "blue": 0.596},
    "ENCCEJA":   {"red": 0.961, "green": 0.878, "blue": 0.502},
    "OUTRO":     {"red": 0.961, "green": 0.678, "blue": 0.678},
}


# =============================================================================
# Helpers
# =============================================================================

def get_responsavel(chave_aba: str) -> str:
    key = chave_aba.strip().upper()
    if key in [l.upper() for l in ENCCEJA_LOCAIS]:
        return "ENCCEJA"
    if key in [l.upper() for l in CRISTIANE_LOCAIS]:
        return "CRISTIANE"
    if key in [l.upper() for l in CHARBEL_LOCAIS]:
        return "CHARBEL"
    return "OUTRO"


def get_gsheet_client():
    creds_path = os.environ.get(
        "GOOGLE_SHEETS_CREDS",
        r"C:/Users/lucas/OneDrive/Documentos/SITE-RIOELAS-TESTE/identificador-488615-c1ab55e9b31b.json"
    )
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]
    creds  = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    _set_timeout(client, 120)
    return client


def _set_timeout(client, seconds: int):
    for obj in (client, getattr(client, 'http_client', None)):
        if obj is None:
            continue
        session = getattr(obj, 'session', None)
        if session is not None and hasattr(session, 'timeout'):
            session.timeout = seconds
            return


def sanitize_sheet_name(name: str) -> str:
    if not name:
        return "Local_Sem_Nome"
    name = str(name)[:100]
    for char in ['\\', '/', '*', '?', ':', '[', ']']:
        name = name.replace(char, '_')
    return name.strip()


def retry_api_call(func, max_retries=8, base_delay=3):
    import requests.exceptions
    TRANSIENT = (
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
    )
    for attempt in range(max_retries):
        try:
            return func()
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                wait = base_delay * (2 ** attempt)
                print(f"⚠️  Rate limit — aguardando {wait}s... ({attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise
        except TRANSIENT as e:
            wait = base_delay * (2 ** attempt)
            print(f"⚠️  Erro de rede ({type(e).__name__}) — aguardando {wait}s... ({attempt+1}/{max_retries})")
            time.sleep(wait)
    return func()


def cleanup_sheets(spreadsheet):
    keep = {ORIGIN_SHEET_NAME.upper(), "DADOS"}
    to_delete = [
        ws for ws in spreadsheet.worksheets()
        if ws.title.strip().upper() not in keep
    ]
    for ws in to_delete:
        try:
            spreadsheet.del_worksheet(ws)
            print(f"  🗑️  Deletada: {ws.title}")
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️  Erro ao deletar '{ws.title}': {e}")
    print(f"✓ Limpeza concluída ({len(to_delete)} aba(s) removida(s))")


def get_or_create_sheet(spreadsheet, title: str):
    sanitized = sanitize_sheet_name(title)
    for ws in spreadsheet.worksheets():
        if ws.title.strip().upper() == sanitized.strip().upper():
            spreadsheet.del_worksheet(ws)
            time.sleep(1)
            break
    sheet = retry_api_call(
        lambda: spreadsheet.add_worksheet(title=sanitized, rows=1000, cols=11)
    )
    retry_api_call(lambda: sheet.update('A1:K1', [HEADERS]))
    return sheet


def parse_date(date_str: str):
    for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y']:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except Exception:
            pass
    return None


# =============================================================================
# Dashboard
# =============================================================================

def create_dashboard(spreadsheet, locals_dict: dict):
    try:
        spreadsheet.del_worksheet(spreadsheet.worksheet("DASHBOARD"))
        time.sleep(1)
    except Exception:
        pass

    sheet = retry_api_call(
        lambda: spreadsheet.add_worksheet(title="DASHBOARD", rows=2000, cols=8)
    )

    headers = ['RESPONSÁVEL', 'LOCAL', 'TOTAL', 'MÊS ATUAL', 'ONTEM', 'SEMANA', 'DATA DE INÍCIO', 'ÚLTIMA DATA']
    retry_api_call(lambda: sheet.update('A1:H1', [headers]))

    today       = datetime.now().date()
    yesterday   = today - timedelta(days=1)
    week_ago    = today - timedelta(days=6)
    month_start = today.replace(day=1)

    def build_row(chave_aba, registros):
        y_count = w_count = m_count = 0
        datas = []
        for row in registros:
            d = parse_date(row[COL_DATA])
            if d:
                datas.append(d.date())
                if d.date() == yesterday:             y_count += 1
                if week_ago <= d.date() <= today:     w_count += 1
                if month_start <= d.date() <= today:  m_count += 1
        responsavel = get_responsavel(chave_aba)
        primeira = DATAS_INICIO_FIXAS.get(chave_aba,
                   min(datas).strftime('%d/%m/%Y') if datas else '')
        ultima   = max(datas).strftime('%d/%m/%Y') if datas else ''
        return [responsavel, chave_aba, len(registros), m_count, y_count, w_count, primeira, ultima]

    dashboard_data = []
    processed = set()

    # Locais que devem ser EXCLUÍDOS do dashboard
    EXCLUIR_DASHBOARD = {'CAMPO GRANDE'}

    for chave_aba, registros in locals_dict.items():
        if chave_aba.strip().upper() in [x.upper() for x in EXCLUIR_DASHBOARD]:
            continue
        dashboard_data.append(build_row(chave_aba, registros))
        processed.add(chave_aba.strip().upper())

    for locais_list in [CHARBEL_LOCAIS, CRISTIANE_LOCAIS, ENCCEJA_LOCAIS]:
        seen = set()
        for local_name in locais_list:
            key = local_name.strip().upper()
            if key in [x.upper() for x in EXCLUIR_DASHBOARD]:
                continue
            if key not in processed and key not in seen:
                responsavel = get_responsavel(local_name)
                primeira = DATAS_INICIO_FIXAS.get(local_name, '')
                dashboard_data.append([responsavel, local_name, 0, 0, 0, 0, primeira, ''])
                seen.add(key)
                processed.add(key)

    dashboard_data.sort(key=lambda x: (x[0], x[1].upper()))

    if dashboard_data:
        retry_api_call(lambda: sheet.update(f"A2:H{len(dashboard_data)+1}", dashboard_data))

    total_row = len(dashboard_data) + 2
    totals = [
        'TOTAL:',
        f'=COUNTA(B2:B{total_row-1})',
        f'=SUM(C2:C{total_row-1})',
        f'=SUM(D2:D{total_row-1})',
        f'=SUM(E2:E{total_row-1})',
        f'=SUM(F2:F{total_row-1})',
        '', '',
    ]
    retry_api_call(lambda: sheet.update(f"A{total_row}:H{total_row}", [totals]))

    time.sleep(2)

    formatting_requests = [
        {
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1,
                           "startColumnIndex": 0, "endColumnIndex": 8},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0},
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                            "bold": True, "fontSize": 10, "fontFamily": "Arial"
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": total_row - 1, "endRowIndex": total_row,
                           "startColumnIndex": 0, "endColumnIndex": 8},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0},
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                            "bold": True, "fontSize": 10, "fontFamily": "Arial"
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": total_row - 1,
                           "startColumnIndex": 0, "endColumnIndex": 8},
                "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 10, "fontFamily": "Arial"}}},
                "fields": "userEnteredFormat(textFormat)"
            }
        },
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount"
            }
        },
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 110}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 400}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3}, "properties": {"pixelSize": 70},  "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 90},  "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5}, "properties": {"pixelSize": 70},  "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 5, "endIndex": 6}, "properties": {"pixelSize": 80},  "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 6, "endIndex": 7}, "properties": {"pixelSize": 110}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 7, "endIndex": 8}, "properties": {"pixelSize": 110}, "fields": "pixelSize"}},
    ]

    resp_counter = {}
    for i, row_data in enumerate(dashboard_data):
        row_index = i + 1
        responsavel = row_data[0]
        resp_counter[responsavel] = resp_counter.get(responsavel, 0) + 1
        use_alt = (resp_counter[responsavel] % 2 == 0)
        bg = (RESP_COLORS_ALT if use_alt else RESP_COLORS).get(
            responsavel, {"red": 1.0, "green": 1.0, "blue": 1.0}
        )
        formatting_requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": row_index, "endRowIndex": row_index + 1,
                           "startColumnIndex": 0, "endColumnIndex": 8},
                "cell": {"userEnteredFormat": {"backgroundColor": bg}},
                "fields": "userEnteredFormat(backgroundColor)"
            }
        })

    retry_api_call(lambda: spreadsheet.batch_update({"requests": formatting_requests}))

    retry_api_call(lambda: spreadsheet.batch_update({"requests": [
        {
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": total_row - 1,
                           "startColumnIndex": 0, "endColumnIndex": 1},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat(textFormat)"
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": total_row,
                           "startColumnIndex": 2, "endColumnIndex": 8},
                "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER"}},
                "fields": "userEnteredFormat(horizontalAlignment)"
            }
        },
    ]}))

    print("✓ Dashboard criado e formatado")


# =============================================================================
# Main
# =============================================================================

def main():
    client = get_gsheet_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    origin = spreadsheet.worksheet(ORIGIN_SHEET_NAME)

    cleanup_sheets(spreadsheet)

    data = origin.get_all_values()
    rows = data[1:]

    locals_dict: dict[str, list] = {}
    for row in rows:
        if len(row) > COL_LOCAL:
            chave = get_chave_aba(row)
            if chave:
                locals_dict.setdefault(chave, []).append(row)

    for chave, registros in locals_dict.items():
        sheet = get_or_create_sheet(spreadsheet, chave)

        new_rows = []
        for r in registros:
            while len(r) < 11:
                r.append('')
            new_rows.append([r[0], r[1], r[2], r[3], r[4],
                              r[5], r[6], r[7], r[8], r[9], r[10]])

        if new_rows:
            retry_api_call(lambda rows=new_rows, s=sheet: s.update(f"A2:K{len(rows)+1}", rows))
            time.sleep(1)

        print(f"✓ {chave} ({len(registros)} inscrição/ões)")

    create_dashboard(spreadsheet, locals_dict)
    print("\n✅ Concluído!")


if __name__ == "__main__":
    main()
