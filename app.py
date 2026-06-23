# -*- coding: utf-8 -*-
"""CPC — Controle Pessoal de Cálculos e Recebimentos.
Versão Streamlit de arquivo único, sem dependências externas.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime
from uuid import uuid4

import streamlit as st

st.set_page_config(
    page_title="CPC — Controle Pessoal de Cálculos e Recebimentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------- Dados e cálculos ---------------------------
def moeda(valor: float | int | None) -> str:
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def recebido(item: dict) -> float:
    return round(sum(float(p.get("valor", 0) or 0) for p in item.get("pagamentos", [])), 2)


def saldo(item: dict) -> float:
    return max(round(float(item.get("honorario", 0) or 0) - recebido(item), 2), 0)


def situacao_financeira(item: dict) -> str:
    if float(item.get("honorario", 0) or 0) <= 0:
        return "Sem cobrança"
    if saldo(item) <= 0.01:
        return "Quitado"
    if recebido(item) > 0:
        return "Parcial"
    return "Em aberto"


def dados_iniciais() -> list[dict]:
    return [
        {
            "id": "cpc001", "processo": "0001234-45.2024.8.26.0100", "cliente": "João da Silva",
            "reclamante": "João da Silva", "reclamado": "Empresa Alfa Ltda.",
            "servico": "Cálculo Trabalhista", "status": "Em andamento", "honorario": 8500.0,
            "entrega": "2026-06-18", "atualizacao": "2026-06-23", "prazo": "2026-06-26",
            "proxima_cobranca": "2026-06-27", "observacoes": "Aguardando documentos complementares.",
            "pagamentos": [{"data": "2026-06-20", "valor": 5300.0, "meio": "PIX"}], "cobrancas": [],
        },
        {
            "id": "cpc002", "processo": "1005678-12.2024.8.26.0050", "cliente": "Maria Oliveira",
            "reclamante": "Maria Oliveira", "reclamado": "Construtora Horizonte S.A.",
            "servico": "Liquidação de Sentença", "status": "Entregue", "honorario": 6200.0,
            "entrega": "2026-06-17", "atualizacao": "2026-06-22", "prazo": "2026-06-17",
            "proxima_cobranca": "", "observacoes": "Trabalho entregue e quitado.",
            "pagamentos": [{"data": "2026-06-22", "valor": 6200.0, "meio": "Transferência"}], "cobrancas": [],
        },
        {
            "id": "cpc003", "processo": "1011121-33.2023.8.26.0704", "cliente": "Carlos Pereira",
            "reclamante": "Carlos Pereira", "reclamado": "Serviços Delta Ltda.",
            "servico": "Revisão de Cálculos", "status": "Aguardando cobrança", "honorario": 5800.0,
            "entrega": "2026-06-15", "atualizacao": "2026-06-21", "prazo": "2026-06-15",
            "proxima_cobranca": "2026-06-24", "observacoes": "Mensagem de cobrança pronta.",
            "pagamentos": [], "cobrancas": [],
        },
        {
            "id": "cpc004", "processo": "0009876-54.2024.8.26.0100", "cliente": "Fernanda Costa",
            "reclamante": "Fernanda Costa", "reclamado": "Comercial Beta Ltda.",
            "servico": "Impugnação de Cálculos", "status": "Em revisão", "honorario": 4750.0,
            "entrega": "2026-06-14", "atualizacao": "2026-06-20", "prazo": "2026-06-25",
            "proxima_cobranca": "2026-07-01", "observacoes": "Revisar memória de cálculo antes da entrega.",
            "pagamentos": [{"data": "2026-06-19", "valor": 2600.0, "meio": "PIX"}], "cobrancas": [],
        },
        {
            "id": "cpc005", "processo": "2002468-79.2023.8.26.0002", "cliente": "Empresa XYZ Ltda.",
            "reclamante": "Ana Souza", "reclamado": "Empresa XYZ Ltda.",
            "servico": "Cálculo de Alvará", "status": "Quitado", "honorario": 3600.0,
            "entrega": "2026-06-12", "atualizacao": "2026-06-18", "prazo": "2026-06-12",
            "proxima_cobranca": "", "observacoes": "Finalizado.",
            "pagamentos": [{"data": "2026-06-18", "valor": 3600.0, "meio": "PIX"}], "cobrancas": [],
        },
    ]


def iniciar() -> None:
    if "calculos" not in st.session_state:
        st.session_state.calculos = dados_iniciais()
    if "pagina" not in st.session_state:
        st.session_state.pagina = "Painel"


def tabela_linhas(items: list[dict]) -> list[dict]:
    return [
        {
            "Processo": c["processo"],
            "Cliente": c["cliente"],
            "Tipo de serviço": c["servico"],
            "Situação": c["status"],
            "Valor": moeda(c["honorario"]),
            "Recebido": moeda(recebido(c)),
            "Saldo": moeda(saldo(c)),
            "Última atualização": c["atualizacao"],
        }
        for c in items
    ]


# --------------------------- Ícones vetoriais ---------------------------
def icon(nome: str, cor: str = "#0D3158", tamanho: int = 22) -> str:
    paths = {
        "home": '<path d="M3 10.8 12 3l9 7.8v9.3a1.9 1.9 0 0 1-1.9 1.9H4.9A1.9 1.9 0 0 1 3 20.1v-9.3Z"/><path d="M9 22v-6h6v6"/>',
        "calc": '<rect x="5" y="2.7" width="14" height="18.6" rx="2.2"/><path d="M8.2 6.5h7.6M8.3 10.4h1M12 10.4h1M15.7 10.4h.1M8.3 14h1M12 14h1M15.7 14h.1M8.3 17.6h1M12 17.6h1M15.7 17.6h.1"/>',
        "money": '<circle cx="12" cy="12" r="8.8"/><path d="M12 5.4v13.2M15.6 8.2c-.7-.9-1.9-1.4-3.6-1.4-2.2 0-3.6 1.1-3.6 2.7 0 1.8 1.8 2.4 3.6 2.8 1.8.5 3.6 1.1 3.6 2.9 0 1.7-1.5 2.9-3.8 2.9-1.6 0-3-.6-3.8-1.6"/>',
        "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/><path d="m15 8 3-3 3 3M18 5v7"/>',
        "wallet": '<path d="M4 7.2h15.8A2.2 2.2 0 0 1 22 9.4v8.4a2.2 2.2 0 0 1-2.2 2.2H4.2A2.2 2.2 0 0 1 2 17.8V6.2A2.2 2.2 0 0 1 4.2 4H18"/><path d="M16 13h6M16 13a1.6 1.6 0 1 0 3.2 0"/>',
        "calendar": '<rect x="3" y="5" width="18" height="16" rx="2.2"/><path d="M7 3v4M17 3v4M3 10h18M8 14h.1M12 14h.1M16 14h.1M8 17h.1M12 17h.1M16 17h.1"/>',
        "file": '<path d="M6 2.8h8l4 4v14.4H6z"/><path d="M14 2.8v4h4M9 12h6M9 15.5h6M9 19h4"/>',
        "send": '<path d="m3 11.5 18-8-7 18-2.5-7.5z"/><path d="M11.5 14.5 21 3.5"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
        "phone": '<path d="M6.5 3.5 9.4 7l-1.9 2.2c1.1 2.5 3.1 4.5 5.6 5.6l2.2-1.9 3.5 2.9-1 3.8c-.2.9-1.1 1.5-2 1.4C8.7 20.2 3.8 15.3 3 8.2c-.1-.9.5-1.8 1.4-2z"/>',
        "document": '<path d="M6 2.8h8l4 4v14.4H6z"/><path d="M14 2.8v4h4M9 12h6M9 15.5h6M9 19h4"/>',
        "report": '<path d="M4 21V4h16v17z"/><path d="M8 17v-3M12 17V9M16 17v-6"/>',
        "gear": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.8 1.8 0 0 0 .36 1.98l.06.06-2.1 2.1-.06-.06A1.8 1.8 0 0 0 15.72 18.7a1.8 1.8 0 0 0-1.1 1.65V20.5h-3v-.15a1.8 1.8 0 0 0-1.1-1.65 1.8 1.8 0 0 0-1.98.36l-.06.06-2.1-2.1.06-.06A1.8 1.8 0 0 0 6.8 15a1.8 1.8 0 0 0-1.65-1.1H5v-3h.15A1.8 1.8 0 0 0 6.8 9.8a1.8 1.8 0 0 0-.36-1.98l-.06-.06 2.1-2.1.06.06a1.8 1.8 0 0 0 1.98.36 1.8 1.8 0 0 0 1.1-1.65V4.3h3v.15a1.8 1.8 0 0 0 1.1 1.65 1.8 1.8 0 0 0 1.98-.36l.06-.06 2.1 2.1-.06.06a1.8 1.8 0 0 0-.36 1.98 1.8 1.8 0 0 0 1.65 1.1h.15v3h-.15A1.8 1.8 0 0 0 19.4 15Z"/>',
        "search": '<circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 5 5"/>',
        "bell": '<path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 22h4"/>',
        "check": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="m8 12 2.5 2.5L16.5 8.5"/>',
    }
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="1.9" '
        f'stroke-linecap="round" stroke-linejoin="round">{paths.get(nome, paths["file"])}</svg>'
    )


# --------------------------- Estilo ---------------------------
def estilo() -> None:
    st.markdown(
        """
        <style>
        :root { --navy:#0D3158; --teal:#0B9E9A; --bg:#F6F9FD; --border:#E5ECF4; --muted:#72829A; }
        .stApp { background: var(--bg); color: var(--navy); }
        #MainMenu, footer, header[data-testid="stHeader"], [data-testid="stSidebar"] { display:none !important; }
        .block-container { max-width: 1780px; padding: 0.8rem 1.1rem 2rem 1.1rem; }
        .nav-pane { background:#fff; border:1px solid var(--border); border-radius:14px; padding:14px 10px 10px; min-height:calc(100vh - 44px); box-shadow:0 3px 16px rgba(30,66,105,.04); position:sticky; top:14px; }
        .brand { display:flex; align-items:center; gap:10px; padding:8px 10px 17px; border-bottom:1px solid var(--border); margin-bottom:13px; }
        .brand-mark { width:52px; height:52px; border-radius:14px; background:linear-gradient(145deg,#0D3158,#0B9E9A); display:flex; align-items:center; justify-content:center; flex:0 0 auto; }
        .brand-title { font-size:28px; line-height:1; font-weight:900; letter-spacing:.5px; color:#0D3158; } .brand-title span{color:#0B9E9A}
        .brand-sub { font-size:10.5px; line-height:1.28; color:#5F7690; font-weight:700; margin-top:5px; }
        .nav-caption { font-size:11px; color:#7A899B; padding:7px 11px 4px; font-weight:800; text-transform:uppercase; letter-spacing:.07em; }
        .nav-pane .stButton { margin:0 0 4px; }
        .nav-pane .stButton > button { border:0!important; background:transparent!important; box-shadow:none!important; color:#173B61!important; justify-content:flex-start!important; min-height:45px!important; padding:0 12px!important; border-radius:10px!important; font-weight:750!important; font-size:14px!important; }
        .nav-pane .stButton > button:hover {background:#F0F8F8!important;color:#0A918E!important;}
        .nav-pane .stButton > button[kind="primary"] {background:#EAF8F7!important;color:#0B8F90!important; border-left:4px solid #11A7A2!important; padding-left:8px!important;}
        .profile { margin-top:36px; border-top:1px solid var(--border); padding:15px 9px 4px; display:flex; align-items:center; gap:9px; }
        .profile-avatar { width:34px;height:34px;border-radius:50%;background:#0E3A65;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:12px; }
        .profile-name {font-weight:800;font-size:12px;color:#173B61}.profile-role{font-size:10.5px;color:#8190A2;margin-top:2px}
        .app-header {height:84px;display:flex;align-items:center;justify-content:space-between;background:#fff;border:1px solid var(--border);border-radius:14px;padding:0 25px;margin-bottom:20px;box-shadow:0 3px 14px rgba(30,66,105,.03)}
        .app-header h1 {font-size:29px;letter-spacing:-.9px;line-height:1;margin:0;color:#10365F;font-weight:900}.header-sub {margin-top:5px;font-size:12px;color:#7B8B9E}
        .search-box {display:flex;align-items:center;gap:9px;border:1px solid #D8E2ED;border-radius:11px;height:43px;padding:0 13px;color:#8A99AC;font-size:13px;min-width:330px}.notif {position:relative;display:inline-flex;margin-left:13px;vertical-align:middle}.notif-badge{position:absolute;right:-8px;top:-8px;width:17px;height:17px;border-radius:50%;background:#0B9E9A;color:#fff;font-size:10px;font-weight:900;display:flex;align-items:center;justify-content:center}.user-badge{display:inline-flex;align-items:center;justify-content:center;width:33px;height:33px;border-radius:50%;background:#0D3158;color:#fff;font-size:11px;font-weight:900;margin-left:15px}
        .metric {background:#fff;border:1px solid var(--border);border-radius:13px;padding:16px;min-height:105px;box-shadow:0 3px 13px rgba(32,66,105,.06);display:flex;gap:13px;align-items:flex-start}.metric-icon{width:47px;height:47px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:#EAF1F7;flex:0 0 auto}.metric-icon.teal{background:#DDF6F4}.metric-icon.green{background:#E0F7F1}.metric-icon.orange{background:#FFF3DF}.metric-label{font-size:12.5px;color:#4E627C;font-weight:750;line-height:1.25}.metric-value{font-size:22px;color:#0E345E;font-weight:900;line-height:1.2;margin-top:5px;letter-spacing:-.4px}.metric-help{font-size:11.5px;color:#099A98;font-weight:750;margin-top:6px}
        .card{background:#fff;border:1px solid var(--border);border-radius:13px;padding:15px 16px;box-shadow:0 3px 13px rgba(32,66,105,.05)}.card h3{font-size:14px;color:#14385F;margin:0 0 10px;font-weight:900}.card-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}.card-link{font-size:12px;color:#0D6EB4;font-weight:850}.filter-pill{font-size:11px;border:1px solid #DCE5ED;border-radius:7px;padding:6px 8px;color:#597089;font-weight:700}
        .tag{padding:4px 8px;border-radius:6px;font-size:10.5px;font-weight:850;display:inline-block;white-space:nowrap}.blue{background:#E6EFFF;color:#2964C6}.teal{background:#DCF7F2;color:#078570}.orange{background:#FFF0D7;color:#C47713}.green{background:#DFF6E9;color:#198355}.purple{background:#ECE8FF;color:#6552B0}.gray{background:#EEF2F6;color:#667588}.red{background:#FFE5E6;color:#C0343A}
        .line-chart{height:220px;padding:15px 0 0;position:relative;background:linear-gradient(180deg,transparent 0%,#FBFDFE 100%);overflow:hidden}.line-grid{position:absolute;left:0;right:0;height:1px;background:#EDF2F7}.line-poly{position:absolute;left:6%;right:5%;top:23px;bottom:40px}.line-poly svg{width:100%;height:100%;overflow:visible}.months{display:flex;justify-content:space-around;font-size:10px;color:#71839A;margin-top:2px}.chart-legend{text-align:center;color:#0B9E9A;font-size:11px;font-weight:700;margin-top:9px}
        .donut-wrap{display:flex;align-items:center;gap:14px;padding:6px 0 1px}.donut{width:134px;height:134px;border-radius:50%;background:conic-gradient(#0D3158 0deg 72deg,#0B9E9A 72deg 144deg,#FFB438 144deg 216deg,#7B94C5 216deg 288deg,#CDD7E4 288deg 360deg);position:relative;flex:0 0 auto}.donut::after{content:"5\A total";white-space:pre;position:absolute;inset:26px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;text-align:center;color:#0D3158;font-size:27px;line-height:1.05;font-weight:900}.donut::after{font-size:25px}.legend-row{display:flex;align-items:center;gap:8px;font-size:10.5px;color:#63768E;margin:6px 0}.legend-dot{width:8px;height:8px;border-radius:50%;flex:0 0 auto}
        .action{display:grid;grid-template-columns:36px 1fr 44px 50px;gap:9px;align-items:center;padding:10px 0;border-bottom:1px solid #EDF1F6}.action-icon{width:34px;height:34px;background:#E5F8F5;border-radius:7px;display:flex;align-items:center;justify-content:center}.action-title{font-weight:850;font-size:11.5px;color:#1C405F}.action-sub{font-size:10.5px;color:#78879A;margin-top:2px}.action-time{font-size:10.5px;color:#728298;text-align:right}
        .bar-label{display:flex;justify-content:space-between;font-size:12px;color:#60718A;margin:12px 0 5px}.bar{height:10px;background:#EDF3F7;border-radius:99px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#0B9E9A,#1AB7B2);border-radius:99px}.footer{text-align:center;color:#8491A3;font-size:11.5px;padding:22px 0 0}
        .stButton > button {border-radius:9px;font-weight:800}.stButton > button[kind="primary"] {background:#0B9B99;border-color:#0B9B99}.stDataFrame{border-radius:12px;overflow:hidden;border:1px solid var(--border)}
        @media(max-width:1050px){.nav-pane{position:static;min-height:unset}.brand-title{font-size:22px}.brand-mark{width:42px;height:42px}.search-box{min-width:190px}.app-header{padding:0 15px}.app-header h1{font-size:24px}.block-container{padding:.5rem}.profile{margin-top:16px}}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------- Componentes visuais ---------------------------
def tag(status: str) -> str:
    mapa = {
        "Em andamento": "blue", "Entregue": "teal", "Aguardando cobrança": "orange",
        "Em revisão": "purple", "Quitado": "green", "Em aberto": "orange", "Parcial": "orange",
        "Alta": "red", "Média": "orange", "Baixa": "green",
    }
    return f"<span class='tag {mapa.get(status, 'gray')}'>{status}</span>"


def cabecalho(titulo: str, subtitulo: str = "") -> None:
    st.markdown(
        f"""
        <div class="app-header">
          <div><h1>{titulo}</h1><div class="header-sub">{subtitulo}</div></div>
          <div class="search-box">{icon('search','#667B94',19)} <span>Buscar processos, clientes, recibos...</span>
            <span class="notif">{icon('bell','#0D3158',21)}<span class="notif-badge">3</span></span>
            <span class="user-badge">VS</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(col, ico: str, titulo: str, valor: str, apoio: str, classe: str = "") -> None:
    with col:
        st.markdown(
            f"""<div class="metric"><div class="metric-icon {classe}">{icon(ico, '#0D3158' if not classe else '#078D8B', 24)}</div>
            <div><div class="metric-label">{titulo}</div><div class="metric-value">{valor}</div><div class="metric-help">{apoio}</div></div></div>""",
            unsafe_allow_html=True,
        )


def logo_html() -> str:
    return f"""
      <div class="brand">
        <div class="brand-mark">{icon('calc','#FFFFFF',29)}</div>
        <div><div class="brand-title">C<span>P</span>C</div><div class="brand-sub">Controle Pessoal de<br>Cálculos e Recebimentos</div></div>
      </div>
    """


def render_nav() -> None:
    st.markdown(logo_html(), unsafe_allow_html=True)
    st.markdown("<div class='nav-caption'>Navegação</div>", unsafe_allow_html=True)
    opcoes = [
        ("Painel", "home"),
        ("Processos e Cálculos", "calc"),
        ("Financeiro", "money"),
        ("Cobranças", "mail"),
        ("Relatórios", "report"),
        ("Documentos", "document"),
        ("Configurações", "gear"),
    ]
    for nome, ico in opcoes:
        # O símbolo é apenas reserva acessível; o CSS/estrutura fixa mantém o menu sempre visível.
        texto = f"{ {'Painel':'⌂','Processos e Cálculos':'▤','Financeiro':'◉','Cobranças':'✉','Relatórios':'▧','Documentos':'▱','Configurações':'⚙'}[nome] }  {nome}"
        if st.button(texto, key=f"menu_{nome}", type="primary" if st.session_state.pagina == nome else "secondary", use_container_width=True):
            st.session_state.pagina = nome
            st.rerun()
    st.markdown(
        """<div class="profile"><div class="profile-avatar">VS</div><div><div class="profile-name">Vítor Soares</div><div class="profile-role">Administrador</div></div></div>""",
        unsafe_allow_html=True,
    )


# --------------------------- Páginas ---------------------------
def pagina_painel() -> None:
    cabecalho("Painel Geral", "Visão integrada dos cálculos, honorários, recebimentos e cobranças.")
    itens = st.session_state.calculos
    previsto = sum(float(x.get("honorario", 0)) for x in itens)
    rec = sum(recebido(x) for x in itens)
    pend = sum(saldo(x) for x in itens)
    andamento = sum(1 for x in itens if x.get("status") == "Em andamento")
    cobrancas = sum(1 for x in itens if saldo(x) > 0.01)

    cols = st.columns(5, gap="small")
    card(cols[0], "calc", "Cálculos em andamento", str(andamento), "+2 desde ontem")
    card(cols[1], "money", "Honorários previstos no mês", moeda(previsto), "+12% vs. mês anterior", "teal")
    card(cols[2], "chart", "Valores recebidos no mês", moeda(rec), "+8% vs. mês anterior", "green")
    card(cols[3], "wallet", "Saldo pendente", moeda(pend), f"{cobrancas} processos")
    card(cols[4], "calendar", "Cobranças próximas", str(cobrancas), "próximos 7 dias", "orange")

    st.write("")
    left, middle, right = st.columns([1.45, 1.00, 1.05], gap="small")
    with left:
        st.markdown(
            """
            <div class="card"><div class="card-head"><h3>Recebimentos nos últimos 6 meses</h3><span class="filter-pill">Últimos 6 meses⌄</span></div>
            <div class="line-chart">
              <div class="line-grid" style="top:28%"></div><div class="line-grid" style="top:52%"></div><div class="line-grid" style="top:76%"></div>
              <div class="line-poly"><svg viewBox="0 0 100 100" preserveAspectRatio="none">
              <defs><linearGradient id="fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#0B9E9A" stop-opacity=".25"/><stop offset="100%" stop-color="#0B9E9A" stop-opacity="0"/></linearGradient></defs>
              <path d="M2,72 L19,52 L36,71 L53,22 L70,42 L88,22 L88,100 L2,100 Z" fill="url(#fill)"/>
              <path d="M2,72 L19,52 L36,71 L53,22 L70,42 L88,22" fill="none" stroke="#0B9E9A" stroke-width="2.6" vector-effect="non-scaling-stroke"/>
              <g fill="#fff" stroke="#0B9E9A" stroke-width="2" vector-effect="non-scaling-stroke"><circle cx="2" cy="72" r="2.2"/><circle cx="19" cy="52" r="2.2"/><circle cx="36" cy="71" r="2.2"/><circle cx="53" cy="22" r="2.2"/><circle cx="70" cy="42" r="2.2"/><circle cx="88" cy="22" r="2.2"/></g>
              </svg></div></div><div class="months"><span>Jan</span><span>Fev</span><span>Mar</span><span>Abr</span><span>Mai</span><span>Jun</span></div><div class="chart-legend">● Recebimentos</div></div>
            """,
            unsafe_allow_html=True,
        )
    with middle:
        st.markdown("<div class='card'><h3>Status dos processos</h3><div class='donut-wrap'><div class='donut'></div><div>" +
                    "<div class='legend-row'><span class='legend-dot' style='background:#0D3158'></span>1&nbsp; Em andamento</div>" +
                    "<div class='legend-row'><span class='legend-dot' style='background:#0B9E9A'></span>1&nbsp; Entregue</div>" +
                    "<div class='legend-row'><span class='legend-dot' style='background:#FFB438'></span>1&nbsp; Aguardando cobrança</div>" +
                    "<div class='legend-row'><span class='legend-dot' style='background:#7B94C5'></span>1&nbsp; Em revisão</div>" +
                    "<div class='legend-row'><span class='legend-dot' style='background:#CDD7E4'></span>1&nbsp; Quitado</div>" +
                    "</div></div></div>", unsafe_allow_html=True)
    with right:
        acoes = [
            ("check", "Enviar cálculo para revisão", itens[0]["processo"], "09:30", "Alta"),
            ("mail", "Enviar cobrança", "3 processos", "11:00", "Média"),
            ("phone", "Ligar para cliente", "João da Silva", "14:00", "Média"),
            ("document", "Revisar documentos", "2 documentos", "16:30", "Baixa"),
        ]
        html = "<div class='card'><h3>Ações de hoje</h3>"
        for ico, titulo, sub, hora, prioridade in acoes:
            html += f"<div class='action'><div class='action-icon'>{icon(ico,'#0B9E9A',18)}</div><div><div class='action-title'>{titulo}</div><div class='action-sub'>{sub}</div></div><div class='action-time'>{hora}</div><div>{tag(prioridade)}</div></div>"
        html += "<div class='card-link' style='padding-top:10px'>Ver todas as ações &nbsp;→</div></div>"
        st.markdown(html, unsafe_allow_html=True)

    st.write("")
    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown("<div class='card' style='padding-bottom:5px'><h3>Processos recentes</h3>", unsafe_allow_html=True)
    with h2:
        if st.button("Ver todos →", key="ver_processos", use_container_width=True):
            st.session_state.pagina = "Processos e Cálculos"
            st.rerun()
    st.dataframe(tabela_linhas(itens), use_container_width=True, hide_index=True, height=255)
    st.markdown("<div class='footer'>CPC — Controle Pessoal de Cálculos e Recebimentos &nbsp; • &nbsp; Todos os direitos reservados &nbsp;&nbsp;&nbsp; Versão 1.0.0</div>", unsafe_allow_html=True)


def pagina_processos() -> None:
    cabecalho("Processos e Cálculos", "Cadastre, acompanhe e revise o histórico técnico e financeiro de cada demanda.")
    col1, col2 = st.columns([1, 3])
    with col1:
        mostrar = st.button("＋ Novo cálculo", type="primary", use_container_width=True)
    with col2:
        busca = st.text_input("Busca rápida", placeholder="Número do processo, parte, cliente ou serviço")
    if mostrar:
        with st.form("novo_calculo", clear_on_submit=True):
            st.subheader("Novo cálculo / processo")
            a, b, c = st.columns(3)
            processo = a.text_input("Número do processo *")
            cliente = b.text_input("Cliente / escritório")
            servico = c.selectbox("Tipo de serviço", ["Cálculo Trabalhista", "Liquidação de Sentença", "Revisão de Cálculos", "Impugnação de Cálculos", "Cálculo de Alvará", "Outro"])
            reclamante = a.text_input("Reclamante")
            reclamado = b.text_input("Reclamado")
            status = c.selectbox("Situação", ["Em andamento", "Entregue", "Aguardando cobrança", "Em revisão", "Quitado"])
            honorario = a.number_input("Honorário previsto (R$)", min_value=0.0, step=50.0)
            entrega = b.date_input("Data de entrega", value=date.today())
            prazo = c.date_input("Prazo", value=date.today())
            obs = st.text_area("Observações")
            if st.form_submit_button("Salvar cálculo", type="primary"):
                if not processo.strip():
                    st.error("Informe o número do processo.")
                else:
                    st.session_state.calculos.append({"id": uuid4().hex, "processo": processo, "cliente": cliente or reclamante or "Sem cliente", "reclamante": reclamante, "reclamado": reclamado, "servico": servico, "status": status, "honorario": honorario, "entrega": entrega.isoformat(), "atualizacao": date.today().isoformat(), "prazo": prazo.isoformat(), "proxima_cobranca": "", "observacoes": obs, "pagamentos": [], "cobrancas": []})
                    st.success("Cálculo registrado nesta sessão.")
                    st.rerun()
    itens = st.session_state.calculos
    if busca:
        termo = busca.casefold()
        itens = [x for x in itens if termo in " ".join(str(v) for v in x.values()).casefold()]
    st.dataframe(tabela_linhas(itens), use_container_width=True, hide_index=True)
    escolha = st.selectbox("Ficha do processo", [x["processo"] for x in itens] if itens else [])
    if escolha:
        x = next(i for i in itens if i["processo"] == escolha)
        a, b, c, d = st.columns(4)
        a.metric("Honorário previsto", moeda(x["honorario"]))
        b.metric("Recebido", moeda(recebido(x)))
        c.metric("Saldo", moeda(saldo(x)))
        d.metric("Situação", x["status"])
        st.write(f"**Partes:** {x.get('reclamante','-')} × {x.get('reclamado','-')}")
        st.write(f"**Observações:** {x.get('observacoes') or 'Não registradas.'}")


def pagina_financeiro() -> None:
    cabecalho("Financeiro", "Acompanhe valores previstos, recebimentos, pagamentos parciais e saldos por processo.")
    itens = st.session_state.calculos
    a, b, c, d = st.columns(4)
    a.metric("Honorários previstos", moeda(sum(x["honorario"] for x in itens)))
    b.metric("Total recebido", moeda(sum(recebido(x) for x in itens)))
    c.metric("A receber", moeda(sum(saldo(x) for x in itens)))
    d.metric("Processos pendentes", sum(1 for x in itens if saldo(x) > .01))
    pendentes = [x for x in itens if saldo(x) > .01]
    alvo = st.selectbox("Selecionar cálculo para pagamento", [x["processo"] for x in pendentes]) if pendentes else None
    if alvo:
        x = next(i for i in itens if i["processo"] == alvo)
        st.info(f"Saldo atual: {moeda(saldo(x))}")
        with st.form("pagamento", clear_on_submit=True):
            a, b, c = st.columns(3)
            data_pag = a.date_input("Data", value=date.today())
            valor = b.number_input("Valor recebido (R$)", min_value=0.01, max_value=max(saldo(x), 0.01), step=50.0)
            meio = c.selectbox("Meio", ["PIX", "Transferência", "Boleto", "Dinheiro", "Outro"])
            if st.form_submit_button("Registrar pagamento", type="primary"):
                x["pagamentos"].append({"data": data_pag.isoformat(), "valor": valor, "meio": meio})
                x["atualizacao"] = date.today().isoformat()
                if saldo(x) <= .01:
                    x["status"] = "Quitado"
                st.success("Pagamento registrado nesta sessão.")
                st.rerun()
    st.dataframe(tabela_linhas(itens), use_container_width=True, hide_index=True)


def pagina_cobrancas() -> None:
    cabecalho("Cobranças", "Organize os contatos, registre negociações e mantenha o histórico de cada processo.")
    pendentes = [x for x in st.session_state.calculos if saldo(x) > .01]
    st.metric("Saldo total a cobrar", moeda(sum(saldo(x) for x in pendentes)))
    if not pendentes:
        st.success("Não há cobranças pendentes.")
        return
    escolha = st.selectbox("Selecione o processo", [x["processo"] for x in pendentes])
    x = next(i for i in pendentes if i["processo"] == escolha)
    texto = f"Prezado(a),\n\nConforme o trabalho técnico realizado no processo nº {x['processo']}, permanece pendente o saldo de honorários no valor de {moeda(saldo(x))}.\n\nPeço a gentileza de verificar a possibilidade de pagamento ou retornar para alinharmos a melhor forma de regularização.\n\nAtenciosamente,\nVítor Soares"
    a, b = st.columns([1.2, .8])
    with a:
        st.text_area("Mensagem sugerida para WhatsApp ou e-mail", texto, height=220)
    with b:
        with st.form("contato", clear_on_submit=True):
            canal = st.selectbox("Canal", ["WhatsApp", "E-mail", "Telefone", "Outro"])
            resultado = st.selectbox("Resultado", ["Cobrança enviada", "Em negociação", "Promessa de pagamento", "Sem resposta", "Suspensa"])
            proximo = st.date_input("Próximo contato", value=date.today())
            if st.form_submit_button("Registrar contato", type="primary"):
                x["cobrancas"].append({"data": date.today().isoformat(), "canal": canal, "resultado": resultado, "proximo": proximo.isoformat()})
                st.success("Contato registrado nesta sessão.")
    st.write("**Histórico de cobranças**")
    st.json(x["cobrancas"] or [{"aviso": "Nenhum contato registrado."}])


def pagina_relatorios() -> None:
    cabecalho("Relatórios", "Aplique filtros e gere relatórios financeiros por processo e por cliente.")
    itens = st.session_state.calculos
    a, b, c = st.columns(3)
    processo = a.multiselect("Processo", [x["processo"] for x in itens])
    cliente = b.multiselect("Cliente", sorted({x["cliente"] for x in itens}))
    status = c.multiselect("Situação", sorted({x["status"] for x in itens}))
    filtrado = itens[:]
    if processo:
        filtrado = [x for x in filtrado if x["processo"] in processo]
    if cliente:
        filtrado = [x for x in filtrado if x["cliente"] in cliente]
    if status:
        filtrado = [x for x in filtrado if x["status"] in status]
    a, b, c, d = st.columns(4)
    a.metric("Registros", len(filtrado))
    b.metric("Previsto", moeda(sum(x["honorario"] for x in filtrado)))
    c.metric("Recebido", moeda(sum(recebido(x) for x in filtrado)))
    d.metric("Saldo", moeda(sum(saldo(x) for x in filtrado)))
    linhas = tabela_linhas(filtrado)
    st.dataframe(linhas, use_container_width=True, hide_index=True)
    buffer = io.StringIO()
    if linhas:
        writer = csv.DictWriter(buffer, fieldnames=linhas[0].keys())
        writer.writeheader()
        writer.writerows(linhas)
    st.download_button("⬇ Baixar relatório em CSV", buffer.getvalue().encode("utf-8-sig"), "relatorio_cpc.csv", "text/csv", type="primary")
    resumo = {"emitido_em": datetime.now().isoformat(), "registros": filtrado, "previsto": sum(x["honorario"] for x in filtrado), "recebido": sum(recebido(x) for x in filtrado), "saldo": sum(saldo(x) for x in filtrado)}
    st.download_button("⬇ Baixar backup JSON", json.dumps(resumo, ensure_ascii=False, indent=2).encode("utf-8"), "relatorio_cpc.json", "application/json")


def pagina_documentos() -> None:
    cabecalho("Documentos", "Catalogue cálculos, relatórios, propostas, recibos, comprovantes e peças vinculadas a cada processo.")
    st.info("Modo demonstração: a tela de documentos será persistida quando o banco de dados for conectado.")
    arq = st.file_uploader("Selecionar documento", type=["pdf", "docx", "xlsx", "png", "jpg"])
    if arq:
        st.success(f"Documento selecionado: {arq.name}. Nesta demonstração ele não é armazenado permanentemente.")


def pagina_configuracoes() -> None:
    cabecalho("Configurações", "Dados de demonstração, backup e preferências do sistema.")
    a, b = st.columns(2)
    with a:
        if st.button("↩ Restaurar base inicial", use_container_width=True):
            st.session_state.calculos = dados_iniciais()
            st.rerun()
    with b:
        backup = json.dumps(st.session_state.calculos, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button("⬇ Baixar backup JSON", backup, "backup_cpc.json", "application/json", use_container_width=True)
    st.write("**Regra de honorários prevista para a versão definitiva:** percentual, valor fixo, modelo misto e ajuste manual.")
    st.write("**Próxima etapa recomendada:** conectar banco persistente para preservar processos, pagamentos, documentos e cobranças.")


# --------------------------- Aplicação ---------------------------
iniciar()
estilo()

menu_col, content_col = st.columns([1.06, 6.0], gap="medium")
with menu_col:
    st.markdown("<div class='nav-pane'>", unsafe_allow_html=True)
    render_nav()
    st.markdown("</div>", unsafe_allow_html=True)

with content_col:
    pagina = st.session_state.pagina
    if pagina == "Painel":
        pagina_painel()
    elif pagina == "Processos e Cálculos":
        pagina_processos()
    elif pagina == "Financeiro":
        pagina_financeiro()
    elif pagina == "Cobranças":
        pagina_cobrancas()
    elif pagina == "Relatórios":
        pagina_relatorios()
    elif pagina == "Documentos":
        pagina_documentos()
    else:
        pagina_configuracoes()
