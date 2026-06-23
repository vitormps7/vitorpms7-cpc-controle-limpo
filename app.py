# -*- coding: utf-8 -*-
"""CPC — Controle Pessoal de Cálculos e Recebimentos.
Versão de demonstração sem banco de dados e sem dependências externas.
"""
from __future__ import annotations

from datetime import date, timedelta
import streamlit as st

st.set_page_config(
    page_title="CPC — Controle Pessoal de Cálculos e Recebimentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- Dados demonstrativos -------------------------
if "pagina" not in st.session_state:
    st.session_state.pagina = "Painel"

PROCESSOS = [
    {"processo": "0001234-45.2024.8.26.0100", "cliente": "João da Silva", "servico": "Cálculo Trabalhista", "situacao": "Em andamento", "valor": 8500.00, "recebido": 5300.00, "saldo": 3200.00, "atualizacao": "23/06/2026"},
    {"processo": "1005678-12.2024.8.26.0050", "cliente": "Maria Oliveira", "servico": "Liquidação de Sentença", "situacao": "Entregue", "valor": 6200.00, "recebido": 6200.00, "saldo": 0.00, "atualizacao": "22/06/2026"},
    {"processo": "1011121-33.2023.8.26.0704", "cliente": "Carlos Pereira", "servico": "Revisão de Cálculos", "situacao": "Aguardando cobrança", "valor": 5800.00, "recebido": 0.00, "saldo": 5800.00, "atualizacao": "21/06/2026"},
    {"processo": "0009876-54.2024.8.26.0100", "cliente": "Fernanda Costa", "servico": "Impugnação de Cálculos", "situacao": "Em revisão", "valor": 4750.00, "recebido": 2600.00, "saldo": 2150.00, "atualizacao": "20/06/2026"},
    {"processo": "2002468-79.2023.8.26.0002", "cliente": "Empresa XYZ Ltda.", "servico": "Cálculo de Alvará", "situacao": "Quitado", "valor": 3600.00, "recebido": 3600.00, "saldo": 0.00, "atualizacao": "18/06/2026"},
]


def moeda(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def badge_class(status: str) -> str:
    return {
        "Em andamento": "blue",
        "Entregue": "teal",
        "Aguardando cobrança": "orange",
        "Em revisão": "purple",
        "Quitado": "green",
    }.get(status, "gray")


# ------------------------- Estilo -------------------------
st.markdown(
    """
<style>
:root{
  --navy:#0E3159; --navy2:#123D69; --teal:#0AA09C; --tealDark:#008580;
  --bg:#F5F8FC; --line:#E4EBF4; --muted:#71829A; --card:#FFFFFF;
}
html, body, [class*="css"] { font-family: Inter, Arial, sans-serif; }
.stApp { background: var(--bg); color:var(--navy); }
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] { background:transparent; }
.block-container{ max-width:1540px; padding: 0.35rem 2.0rem 2.5rem 2.0rem; }

/* Sidebar: a posição é nativa do Streamlit; NÃO há bottom/fixed personalizado. */
[data-testid="stSidebar"] { min-width:272px !important; max-width:272px !important; background:#fff !important; border-right:1px solid var(--line); }
[data-testid="stSidebar"] > div:first-child { padding: 16px 12px 26px 12px; }
[data-testid="stSidebar"] .stButton { margin:0 0 6px 0; }
[data-testid="stSidebar"] .stButton>button{
  height:46px; width:100%; border:0!important; border-radius:10px!important; background:transparent!important;
  color:#294B70!important; box-shadow:none!important; justify-content:flex-start!important; padding-left:14px!important;
  font-weight:650!important; font-size:14px!important;
}
[data-testid="stSidebar"] .stButton>button:hover { background:#EEF9F8!important; color:#008D88!important; }
[data-testid="stSidebar"] .stButton>button[kind="primary"] { background:#EAF8F7!important; color:#008F8A!important; position:relative; }
[data-testid="stSidebar"] .stButton>button[kind="primary"]:before { content:""; position:absolute; left:0; top:9px; bottom:9px; width:4px; border-radius:5px; background:#0AA09C; }

.brand-wrap{margin:6px 8px 22px; display:flex; align-items:center; gap:11px;}
.brand-icon{width:52px;height:52px;border-radius:14px; background:linear-gradient(145deg,#0E3159,#0AA09C); color:#fff; display:flex; align-items:center; justify-content:center; font-size:27px; box-shadow:0 5px 16px rgba(14,49,89,.18)}
.brand-name{font-weight:850;color:#0E3159;font-size:27px;line-height:1;letter-spacing:-1.3px}
.brand-sub{font-size:9.5px;color:#647791;line-height:1.25;margin-top:4px;font-weight:600}
.side-section{font-size:10px;letter-spacing:1.2px;color:#8997AA;font-weight:800;margin:10px 12px 7px}
.user-box{border-top:1px solid var(--line);margin:24px 8px 0;padding:18px 4px 0;display:flex;align-items:center;gap:10px;color:#355271}
.user-avatar{width:36px;height:36px;border-radius:50%;background:#123E6B;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px}
.user-name{font-size:12px;font-weight:800;line-height:1.1}.user-role{font-size:11px;color:#7C8BA0;margin-top:3px}

.topbar{background:#fff;border-bottom:1px solid var(--line);margin:0 -2rem 26px -2rem;padding:0 2rem;height:88px;display:flex;align-items:center;justify-content:space-between;}
.top-title{font-size:30px;font-weight:850;letter-spacing:-1px;color:var(--navy);}
.tools{display:flex;align-items:center;gap:14px}.search{width:340px;border:1px solid #D7E2ED;border-radius:11px;padding:12px 14px;color:#8290A4;font-size:13px;background:#fff}.bell{font-size:20px;color:#123D69;position:relative}.dot{position:absolute;background:#0AA09C;color:#fff;border-radius:20px;font-size:10px;line-height:17px;text-align:center;width:17px;height:17px;right:-9px;top:-7px;font-weight:800}.head-avatar{width:34px;height:34px;border-radius:50%;background:#123D69;color:#fff;display:flex;justify-content:center;align-items:center;font-weight:800;font-size:11px}

.metric{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 17px;min-height:112px;box-shadow:0 3px 13px rgba(28,63,108,.055);display:flex;gap:13px}.metric-icon{height:48px;width:48px;border-radius:11px;background:#E7EFF7;display:flex;align-items:center;justify-content:center;font-size:24px;flex:none}.tealbg{background:#DDF7F4}.greenbg{background:#E0F8F1}.yellowbg{background:#FFF2DA}.metric-label{font-size:12px;font-weight:750;color:#546883;line-height:1.25}.metric-value{font-size:23px;font-weight:850;color:var(--navy);margin-top:6px;letter-spacing:-.5px}.metric-help{font-size:11px;font-weight:700;color:#009894;margin-top:6px}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:15px 17px;box-shadow:0 3px 13px rgba(28,63,108,.045);height:100%}.card-title{font-size:14px;font-weight:850;color:var(--navy);margin-bottom:10px}.panel-note{font-size:11px;color:#7B8CA1}

.chart-wrap{height:240px;display:flex;align-items:end;gap:20px;padding:20px 10px 10px;border-bottom:1px solid #EDF1F6}.bar-col{height:100%;display:flex;flex-direction:column;justify-content:end;align-items:center;gap:7px;flex:1}.bar{width:100%;max-width:62px;border-radius:8px 8px 2px 2px;background:linear-gradient(180deg,#BCEDEA,#0AA09C)}.bar-label{font-size:10px;color:#73839A}.legend{font-size:11px;color:#009894;text-align:center;margin-top:10px;font-weight:700}
.status-row{display:flex;gap:9px;align-items:center;margin:13px 0}.status-dot{height:9px;width:9px;border-radius:50%;background:#0AA09C}.status-bar{height:8px;flex:1;background:#EAF0F5;border-radius:6px;overflow:hidden}.fill{height:100%;border-radius:6px;background:#0AA09C}.donut-wrap{display:flex;align-items:center;gap:19px}.donut{width:125px;height:125px;border-radius:50%;background:conic-gradient(#0E3159 0 38%,#0AA09C 38% 60%,#FFB33F 60% 78%,#8099C7 78% 90%,#D3DCE8 90% 100%);position:relative;flex:none}.donut:after{content:"5\A total";white-space:pre;text-align:center;font-size:25px;font-weight:850;line-height:1.2;color:#0E3159;display:flex;align-items:center;justify-content:center;position:absolute;inset:24px;background:#fff;border-radius:50%}.status-list{flex:1;font-size:11px;color:#637690}.status-list div{margin:8px 0}.small-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}
.action{display:grid;grid-template-columns:38px 1fr 40px 52px;gap:8px;align-items:center;padding:10px 0;border-bottom:1px solid #EEF2F6}.action:last-child{border-bottom:0}.action-icon{height:34px;width:34px;border-radius:8px;background:#E5F8F4;color:#089A90;display:flex;align-items:center;justify-content:center;font-size:18px}.action-title{font-size:11px;font-weight:800;color:#1D405F}.action-sub{font-size:10px;color:#8390A2;margin-top:3px}.action-time{font-size:10px;color:#789}.priority{font-size:10px;font-weight:800;padding:5px 7px;text-align:center;border-radius:7px}.p-high{background:#FFE5E7;color:#C84B54}.p-med{background:#FFF0D8;color:#B56A10}.p-low{background:#E0F7EB;color:#168956}
.table-card{margin-top:18px}.table-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}.table-button{border:1px solid #DCE5EF;border-radius:9px;padding:7px 12px;font-size:11px;font-weight:800;color:#2863A1;background:#fff}.tag{font-size:10px;padding:5px 7px;border-radius:6px;font-weight:800}.blue{background:#E7EFFF;color:#3267C2}.teal{background:#DDF8F2;color:#078674}.orange{background:#FFF0D6;color:#BE7415}.purple{background:#ECE8FF;color:#6A58B7}.green{background:#DFF6E9;color:#168355}.gray{background:#EFF2F5;color:#748296}
.footer{text-align:center;color:#8997A9;font-size:11px;padding:21px 0 0}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}

@media(max-width: 960px){.block-container{padding:0.2rem 1rem 2rem}.topbar{margin:0 -1rem 20px;padding:0 1rem;height:74px}.search{width:220px}.top-title{font-size:24px}}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------- Menu lateral nativo -------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap"><div class="brand-icon">▦</div><div><div class="brand-name">CPC</div><div class="brand-sub">Controle Pessoal de<br>Cálculos e Recebimentos</div></div></div>
        <div class="side-section">NAVEGAÇÃO</div>
        """,
        unsafe_allow_html=True,
    )
    nav = [
        ("Painel", "⌂"),
        ("Processos e Cálculos", "▤"),
        ("Financeiro", "◉"),
        ("Cobranças", "✉"),
        ("Relatórios", "▧"),
        ("Documentos", "▱"),
        ("Configurações", "⚙"),
    ]
    for nome, ico in nav:
        if st.button(f"{ico}  {nome}", key=f"nav_{nome}", use_container_width=True, type="primary" if st.session_state.pagina == nome else "secondary"):
            st.session_state.pagina = nome
            st.rerun()
    st.markdown(
        """
        <div class="user-box"><div class="user-avatar">VS</div><div><div class="user-name">Vítor Soares</div><div class="user-role">Administrador</div></div></div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------- Componentes -------------------------
def topbar(titulo: str) -> None:
    st.markdown(
        f"""
        <div class="topbar"><div class="top-title">{titulo}</div>
        <div class="tools"><div class="search">⌕ &nbsp; Buscar processos, clientes, recibos...</div><div class="bell">♧<span class="dot">3</span></div><div class="head-avatar">VS</div><div style="font-size:12px;color:#64758B">⌄</div></div></div>
        """,
        unsafe_allow_html=True,
    )


def metric(col, icon: str, label: str, value: str, note: str, theme: str = "") -> None:
    with col:
        st.markdown(
            f"""<div class="metric"><div class="metric-icon {theme}">{icon}</div><div><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-help">{note}</div></div></div>""",
            unsafe_allow_html=True,
        )


def render_dashboard() -> None:
    topbar("Painel Geral")
    a, b, c, d, e = st.columns(5, gap="small")
    metric(a, "▤", "Cálculos em andamento", "1", "+2 desde ontem")
    metric(b, "$", "Honorários previstos no mês", moeda(28850), "+12% vs. mês anterior", "tealbg")
    metric(c, "↗", "Valores recebidos no mês", moeda(17700), "+8% vs. mês anterior", "greenbg")
    metric(d, "▣", "Saldo pendente", moeda(11150), "3 processos")
    metric(e, "▦", "Cobranças próximas", "3", "próximos 7 dias", "yellowbg")
    st.write("")

    left, middle, right = st.columns([1.4, .88, .95], gap="small")
    with left:
        bars = [(42, "Jan"), (59, "Fev"), (39, "Mar"), (84, "Abr"), (68, "Mai"), (88, "Jun")]
        bar_html = "".join(f'<div class="bar-col"><div class="bar" style="height:{h}%"></div><div class="bar-label">{m}</div></div>' for h, m in bars)
        st.markdown(f'<div class="card"><div class="card-title">Recebimentos nos últimos 6 meses</div><div class="chart-wrap">{bar_html}</div><div class="legend">● Recebimentos</div></div>', unsafe_allow_html=True)
    with middle:
        st.markdown(
            """
            <div class="card"><div class="card-title">Status dos processos</div>
            <div class="donut-wrap"><div class="donut"></div><div class="status-list">
              <div><span class="small-dot" style="background:#0E3159"></span>1 &nbsp; Em andamento</div>
              <div><span class="small-dot" style="background:#0AA09C"></span>1 &nbsp; Entregue</div>
              <div><span class="small-dot" style="background:#FFB33F"></span>1 &nbsp; Aguardando cobrança</div>
              <div><span class="small-dot" style="background:#8099C7"></span>1 &nbsp; Em revisão</div>
              <div><span class="small-dot" style="background:#D3DCE8"></span>1 &nbsp; Quitado</div>
            </div></div></div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        actions = [
            ("☑", "Enviar cálculo para revisão", "0001234-45.2024.8.26.0100", "09:30", "Alta", "p-high"),
            ("✉", "Enviar cobrança", "3 processos", "11:00", "Média", "p-med"),
            ("☎", "Ligar para cliente", "João da Silva", "14:00", "Média", "p-med"),
            ("▱", "Revisar documentos", "2 documentos", "16:30", "Baixa", "p-low"),
        ]
        action_html = "".join(f'<div class="action"><div class="action-icon">{ico}</div><div><div class="action-title">{title}</div><div class="action-sub">{sub}</div></div><div class="action-time">{hora}</div><div class="priority {css}">{prio}</div></div>' for ico, title, sub, hora, prio, css in actions)
        st.markdown(f'<div class="card"><div class="card-title">Ações de hoje</div>{action_html}<div style="font-size:11px;font-weight:800;color:#1574B9;margin-top:12px">Ver todas as ações →</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="card table-card"><div class="table-head"><div class="card-title" style="margin:0">Processos recentes</div><div class="table-button">Ver todos os processos →</div></div></div>', unsafe_allow_html=True)
    rows = []
    for p in PROCESSOS:
        rows.append({
            "Processo": p["processo"], "Cliente": p["cliente"], "Tipo de serviço": p["servico"], "Situação": p["situacao"],
            "Valor": moeda(p["valor"]), "Recebido": moeda(p["recebido"]), "Saldo": moeda(p["saldo"]), "Última atualização": p["atualizacao"],
        })
    st.dataframe(rows, use_container_width=True, hide_index=True, height=250)
    st.markdown('<div class="footer">CPC — Controle Pessoal de Cálculos e Recebimentos &nbsp; • &nbsp; Todos os direitos reservados &nbsp;&nbsp;&nbsp; Versão 1.1.0</div>', unsafe_allow_html=True)


def generic_page(title: str, text: str) -> None:
    topbar(title)
    st.markdown(f'<div class="card"><div class="card-title">{title}</div><div class="panel-note">{text}</div></div>', unsafe_allow_html=True)
    if title == "Processos e Cálculos":
        x, y = st.columns([1, 3])
        with x:
            if st.button("➕ Novo cálculo", type="primary", use_container_width=True):
                st.success("Tela de cadastro pronta para a próxima etapa com banco de dados.")
        with y:
            st.text_input("Busca rápida", placeholder="Número do processo, parte, cliente, advogado ou serviço")
        st.dataframe(PROCESSOS, use_container_width=True, hide_index=True)
    elif title == "Financeiro":
        st.metric("Saldo total a receber", moeda(sum(p["saldo"] for p in PROCESSOS)))
        st.dataframe([{k: v for k, v in p.items() if k in ("processo", "cliente", "valor", "recebido", "saldo")} for p in PROCESSOS], use_container_width=True, hide_index=True)
    elif title == "Cobranças":
        st.text_area("Mensagem sugerida", value="Prezado(a), conforme o trabalho técnico realizado, permanece pendente o saldo de honorários. Permaneço à disposição para esclarecimentos.", height=160)
        st.button("Registrar contato", type="primary")
    elif title == "Relatórios":
        st.selectbox("Modelo de relatório", ["Financeiro geral", "Por cliente / escritório", "Ficha por processo"])
        st.button("📄 Gerar relatório", type="primary")
    elif title == "Documentos":
        st.file_uploader("Selecionar documento", type=["pdf", "xlsx", "docx", "png", "jpg"])
    elif title == "Configurações":
        st.info("Modo demonstração: a persistência definitiva será conectada ao banco de dados sem alterar este visual.")


if st.session_state.pagina == "Painel":
    render_dashboard()
else:
    texts = {
        "Processos e Cálculos": "Cadastre, acompanhe e revise o histórico técnico e financeiro de cada demanda.",
        "Financeiro": "Acompanhe honorários previstos, recebimentos, pagamentos parciais e saldos.",
        "Cobranças": "Organize contatos, negociações e promessas de pagamento.",
        "Relatórios": "Gere relatórios financeiros, por cliente e por processo.",
        "Documentos": "Catalogue cálculos, relatórios, propostas, recibos e comprovantes.",
        "Configurações": "Defina referências do sistema e prepare a transição para persistência em banco.",
    }
    generic_page(st.session_state.pagina, texts.get(st.session_state.pagina, ""))
