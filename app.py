# -*- coding: utf-8 -*-
"""CPC — Controle Pessoal de Cálculos e Recebimentos.
Versão de arquivo único: usa apenas Streamlit e biblioteca padrão do Python.
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
    initial_sidebar_state="expanded",
)


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


def estilo() -> None:
    st.markdown(
        """
        <style>
        :root { --navy:#0D3158; --teal:#0B9E9A; --bg:#F8FAFD; --border:#E6ECF4; --muted:#72829A; }
        .stApp { background:var(--bg); color:var(--navy); }
        #MainMenu, footer, header { visibility:hidden; }
        .block-container { max-width:1600px; padding:0 2.0rem 2rem 2rem; }
        [data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid var(--border); min-width:265px; }
        [data-testid="stSidebar"] .stButton > button { border:0; background:transparent; color:#17345A; justify-content:flex-start; font-weight:700; border-radius:10px; min-height:44px; }
        [data-testid="stSidebar"] .stButton > button[kind="primary"] { background:#EAF8F7; color:#0B8F90; }
        .top {display:flex; justify-content:space-between; align-items:center; background:#fff; margin:0 -2rem 22px; padding:18px 2rem; border-bottom:1px solid var(--border);}
        .top h1 {font-size:31px; margin:0; color:#10365F; letter-spacing:-1px;}
        .top .tools {color:#74839A; font-size:14px; border:1px solid #D9E2EC; border-radius:10px; padding:11px 15px; min-width:300px;}
        .logo {font-size:32px; font-weight:900; letter-spacing:2px; color:#0D3158; margin:8px 8px 0;}
        .logo span {color:#0B9E9A;}
        .logo-sub {font-size:11px; color:#53708C; margin:0 8px 18px; font-weight:700; line-height:1.3;}
        .metric {background:#fff; border:1px solid var(--border); border-radius:13px; padding:16px; min-height:105px; box-shadow:0 3px 12px rgba(32,66,105,.06); display:flex; gap:13px;}
        .metric-icon {width:46px; height:46px; border-radius:10px; display:flex; align-items:center; justify-content:center; background:#EAF1F7; font-size:23px;}
        .metric-icon.teal {background:#DDF6F4;} .metric-icon.green {background:#E0F7F1;} .metric-icon.orange {background:#FFF3DF;}
        .metric-label {font-size:13px; color:#4E627C; font-weight:700;}.metric-value{font-size:24px; color:#0E345E; font-weight:900; margin-top:4px;}.metric-help{font-size:12px; color:#099A98; font-weight:700; margin-top:5px;}
        .card {background:#fff; border:1px solid var(--border); border-radius:13px; padding:15px; box-shadow:0 3px 12px rgba(32,66,105,.05);}
        .card h3 {font-size:14px; color:#14385F; margin:0 0 10px;}.tag{padding:4px 8px;border-radius:6px;font-size:11px;font-weight:800;display:inline-block}.blue{background:#E6EFFF;color:#2964C6}.teal{background:#DCF7F2;color:#078570}.orange{background:#FFF0D7;color:#C47713}.green{background:#DFF6E9;color:#198355}.purple{background:#ECE8FF;color:#6552B0}.gray{background:#EEF2F6;color:#667588}
        .action {display:grid; grid-template-columns:36px 1fr 48px 54px; gap:9px; align-items:center; padding:10px 0; border-bottom:1px solid #EDF1F6;}.action-icon{background:#E5F8F5;border-radius:7px;padding:8px;text-align:center}.action-title{font-weight:800;font-size:12px;color:#1C405F}.action-sub{font-size:11px;color:#78879A}.action-time{font-size:11px;color:#728298;text-align:right}
        .bar-label{display:flex;justify-content:space-between;font-size:12px;color:#60718A;margin:12px 0 5px}.bar{height:10px;background:#EDF3F7;border-radius:99px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#0B9E9A,#1AB7B2);border-radius:99px}.footer{text-align:center;color:#8491A3;font-size:12px;padding:22px 0 0}
        .stButton > button {border-radius:9px; font-weight:800;}.stButton > button[kind="primary"] {background:#0B9B99; border-color:#0B9B99;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def tag(status: str) -> str:
    mapa = {
        "Em andamento": "blue", "Entregue": "teal", "Aguardando cobrança": "orange",
        "Em revisão": "purple", "Quitado": "green", "Em aberto": "orange", "Parcial": "orange",
    }
    return f"<span class='tag {mapa.get(status, 'gray')}'>{status}</span>"


def tabela_linhas(items: list[dict]) -> list[dict]:
    return [{
        "Processo": c["processo"], "Cliente": c["cliente"], "Tipo de serviço": c["servico"],
        "Situação": c["status"], "Valor": moeda(c["honorario"]), "Recebido": moeda(recebido(c)),
        "Saldo": moeda(saldo(c)), "Última atualização": c["atualizacao"],
    } for c in items]


def sidebar() -> None:
    with st.sidebar:
        st.markdown("<div class='logo'>C<span>P</span>C</div><div class='logo-sub'>Controle Pessoal de<br>Cálculos e Recebimentos</div>", unsafe_allow_html=True)
        opcoes = [
            ("🏠", "Painel"), ("▤", "Processos e Cálculos"), ("💲", "Financeiro"),
            ("✉", "Cobranças"), ("▧", "Relatórios"), ("▱", "Documentos"), ("⚙", "Configurações"),
        ]
        for icon, nome in opcoes:
            if st.button(f"{icon}  {nome}", type="primary" if st.session_state.pagina == nome else "secondary", use_container_width=True):
                st.session_state.pagina = nome
                st.rerun()
        st.markdown("<br><br><hr><div style='font-size:13px;color:#17345A'><b>VS &nbsp; Vítor Soares</b><br><span style='color:#78879A'>Administrador</span></div>", unsafe_allow_html=True)


def cabecalho(titulo: str) -> None:
    st.markdown(f"<div class='top'><div><h1>{titulo}</h1></div><div class='tools'>⌕ &nbsp; Buscar processos, clientes, recibos... &nbsp; 🔔 3 &nbsp; <b>VS</b></div></div>", unsafe_allow_html=True)


def card(col, icon: str, titulo: str, valor: str, apoio: str, cls: str = "") -> None:
    with col:
        st.markdown(f"<div class='metric'><div class='metric-icon {cls}'>{icon}</div><div><div class='metric-label'>{titulo}</div><div class='metric-value'>{valor}</div><div class='metric-help'>{apoio}</div></div></div>", unsafe_allow_html=True)


def pagina_painel() -> None:
    cabecalho("Painel Geral")
    itens = st.session_state.calculos
    previsto = sum(float(x.get("honorario", 0)) for x in itens)
    rec = sum(recebido(x) for x in itens)
    pend = sum(saldo(x) for x in itens)
    andamento = sum(1 for x in itens if x.get("status") == "Em andamento")
    cobrancas = sum(1 for x in itens if saldo(x) > 0.01)
    cols = st.columns(5, gap="small")
    card(cols[0], "▤", "Cálculos em andamento", str(andamento), "+2 desde ontem")
    card(cols[1], "💲", "Honorários previstos no mês", moeda(previsto), "+12% vs. mês anterior", "teal")
    card(cols[2], "↗", "Valores recebidos no mês", moeda(rec), "+8% vs. mês anterior", "green")
    card(cols[3], "▣", "Saldo pendente", moeda(pend), f"{cobrancas} processos")
    card(cols[4], "▦", "Cobranças próximas", str(cobrancas), "próximos 7 dias", "orange")
    st.write("")
    a, b, c = st.columns([1.35, .8, .95], gap="small")
    with a:
        st.markdown("<div class='card'><h3>Recebimentos nos últimos 6 meses</h3><div style='height:200px;display:flex;align-items:end;gap:10px;padding:12px 8px 0'>" + "".join(f"<div style='flex:1;text-align:center'><div style='height:{h}px;background:linear-gradient(180deg,#CFF3F0,#0B9E9A);border-radius:8px 8px 2px 2px'></div><div style='font-size:10px;color:#6D7E93;margin-top:6px'>{m}</div></div>" for h,m in [(82,'Jan'),(112,'Fev'),(76,'Mar'),(158,'Abr'),(133,'Mai'),(166,'Jun')]) + "</div><div style='font-size:11px;color:#0B9E9A;text-align:center;margin-top:10px'>● Recebimentos</div></div>", unsafe_allow_html=True)
    with b:
        status = {}
        for x in itens:
            status[x["status"]] = status.get(x["status"], 0) + 1
        total = max(len(itens), 1)
        linhas = "".join(f"<div class='bar-label'><span>{k}</span><span>{v}</span></div><div class='bar'><div class='fill' style='width:{int(v/total*100)}%'></div></div>" for k,v in status.items())
        st.markdown(f"<div class='card'><h3>Status dos processos</h3><div style='text-align:center;font-size:36px;font-weight:900;color:#0D3158;padding:8px'>{len(itens)}<div style='font-size:11px;color:#72829A;font-weight:700'>total</div></div>{linhas}</div>", unsafe_allow_html=True)
    with c:
        acoes = [
            ("☑", "Enviar cálculo para revisão", itens[0]["processo"], "09:30", "Alta", "orange"),
            ("✉", "Enviar cobrança", "3 processos", "11:00", "Média", "orange"),
            ("☎", "Ligar para cliente", "João da Silva", "14:00", "Média", "orange"),
            ("▱", "Revisar documentos", "2 documentos", "16:30", "Baixa", "green"),
        ]
        html = "<div class='card'><h3>Ações de hoje</h3>"
        for icon, title, sub, hora, prior, cor in acoes:
            html += f"<div class='action'><div class='action-icon'>{icon}</div><div><div class='action-title'>{title}</div><div class='action-sub'>{sub}</div></div><div class='action-time'>{hora}</div><div>{tag(prior)}</div></div>"
        html += "<div style='font-size:12px;color:#0D6EB4;font-weight:800;padding-top:10px'>Ver todas as ações →</div></div>"
        st.markdown(html, unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='card'><h3>Processos recentes</h3></div>", unsafe_allow_html=True)
    st.dataframe(tabela_linhas(itens), use_container_width=True, hide_index=True, height=270)
    st.markdown("<div class='footer'>CPC — Controle Pessoal de Cálculos e Recebimentos &nbsp; • &nbsp; Todos os direitos reservados &nbsp;&nbsp;&nbsp; Versão 1.0.0</div>", unsafe_allow_html=True)


def pagina_processos() -> None:
    cabecalho("Processos e Cálculos")
    col1, col2 = st.columns([1, 3])
    with col1:
        mostrar = st.button("➕ Novo cálculo", type="primary", use_container_width=True)
    with col2:
        busca = st.text_input("Busca rápida", placeholder="Número do processo, parte, cliente ou serviço")
    if mostrar:
        with st.form("novo_calculo", clear_on_submit=True):
            st.subheader("Novo cálculo / processo")
            a,b,c = st.columns(3)
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
                    st.session_state.calculos.append({"id":uuid4().hex, "processo":processo, "cliente":cliente or reclamante or "Sem cliente", "reclamante":reclamante, "reclamado":reclamado, "servico":servico, "status":status, "honorario":honorario, "entrega":entrega.isoformat(), "atualizacao":date.today().isoformat(), "prazo":prazo.isoformat(), "proxima_cobranca":"", "observacoes":obs, "pagamentos":[], "cobrancas":[]})
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
        a,b,c,d = st.columns(4)
        a.metric("Honorário previsto", moeda(x["honorario"]))
        b.metric("Recebido", moeda(recebido(x)))
        c.metric("Saldo", moeda(saldo(x)))
        d.metric("Situação", x["status"])
        st.write(f"**Partes:** {x.get('reclamante','-')} × {x.get('reclamado','-')}")
        st.write(f"**Observações:** {x.get('observacoes') or 'Não registradas.'}")


def pagina_financeiro() -> None:
    cabecalho("Financeiro")
    itens = st.session_state.calculos
    a,b,c,d = st.columns(4)
    a.metric("Honorários previstos", moeda(sum(x["honorario"] for x in itens)))
    b.metric("Total recebido", moeda(sum(recebido(x) for x in itens)))
    c.metric("A receber", moeda(sum(saldo(x) for x in itens)))
    d.metric("Processos pendentes", sum(1 for x in itens if saldo(x) > .01))
    alvo = st.selectbox("Selecionar cálculo para pagamento", [x["processo"] for x in itens if saldo(x) > .01])
    if alvo:
        x = next(i for i in itens if i["processo"] == alvo)
        st.info(f"Saldo atual: {moeda(saldo(x))}")
        with st.form("pagamento", clear_on_submit=True):
            a,b,c = st.columns(3)
            data_pag = a.date_input("Data", value=date.today())
            valor = b.number_input("Valor recebido (R$)", min_value=0.01, max_value=max(saldo(x), 0.01), step=50.0)
            meio = c.selectbox("Meio", ["PIX", "Transferência", "Boleto", "Dinheiro", "Outro"])
            if st.form_submit_button("Registrar pagamento", type="primary"):
                x["pagamentos"].append({"data":data_pag.isoformat(), "valor":valor, "meio":meio})
                x["atualizacao"] = date.today().isoformat()
                if saldo(x) <= .01:
                    x["status"] = "Quitado"
                st.success("Pagamento registrado nesta sessão.")
                st.rerun()
    st.dataframe(tabela_linhas(itens), use_container_width=True, hide_index=True)


def pagina_cobrancas() -> None:
    cabecalho("Cobranças")
    pendentes = [x for x in st.session_state.calculos if saldo(x) > .01]
    st.metric("Saldo total a cobrar", moeda(sum(saldo(x) for x in pendentes)))
    if not pendentes:
        st.success("Não há cobranças pendentes.")
        return
    escolha = st.selectbox("Selecione o processo", [x["processo"] for x in pendentes])
    x = next(i for i in pendentes if i["processo"] == escolha)
    texto = f"Prezado(a),\n\nConforme o trabalho técnico realizado no processo nº {x['processo']}, permanece pendente o saldo de honorários no valor de {moeda(saldo(x))}.\n\nPeço a gentileza de verificar a possibilidade de pagamento ou retornar para alinharmos a melhor forma de regularização.\n\nAtenciosamente,\nVítor Soares"
    a,b = st.columns([1.2,.8])
    with a:
        st.text_area("Mensagem sugerida para WhatsApp ou e-mail", texto, height=220)
    with b:
        with st.form("contato", clear_on_submit=True):
            canal = st.selectbox("Canal", ["WhatsApp", "E-mail", "Telefone", "Outro"])
            resultado = st.selectbox("Resultado", ["Cobrança enviada", "Em negociação", "Promessa de pagamento", "Sem resposta", "Suspensa"])
            proximo = st.date_input("Próximo contato", value=date.today())
            if st.form_submit_button("Registrar contato", type="primary"):
                x["cobrancas"].append({"data":date.today().isoformat(), "canal":canal, "resultado":resultado, "proximo":proximo.isoformat()})
                st.success("Contato registrado nesta sessão.")
    st.write("**Histórico de cobranças**")
    st.json(x["cobrancas"] or [{"aviso":"Nenhum contato registrado."}])


def pagina_relatorios() -> None:
    cabecalho("Relatórios")
    itens = st.session_state.calculos
    a,b,c = st.columns(3)
    processo = a.multiselect("Processo", [x["processo"] for x in itens])
    cliente = b.multiselect("Cliente", sorted({x["cliente"] for x in itens}))
    status = c.multiselect("Situação", sorted({x["status"] for x in itens}))
    filtrado = itens[:]
    if processo: filtrado = [x for x in filtrado if x["processo"] in processo]
    if cliente: filtrado = [x for x in filtrado if x["cliente"] in cliente]
    if status: filtrado = [x for x in filtrado if x["status"] in status]
    a,b,c,d = st.columns(4)
    a.metric("Registros", len(filtrado)); b.metric("Previsto", moeda(sum(x["honorario"] for x in filtrado))); c.metric("Recebido", moeda(sum(recebido(x) for x in filtrado))); d.metric("Saldo", moeda(sum(saldo(x) for x in filtrado)))
    linhas = tabela_linhas(filtrado)
    st.dataframe(linhas, use_container_width=True, hide_index=True)
    buffer = io.StringIO()
    if linhas:
        writer = csv.DictWriter(buffer, fieldnames=linhas[0].keys())
        writer.writeheader(); writer.writerows(linhas)
    st.download_button("⬇️ Baixar relatório em CSV", buffer.getvalue().encode("utf-8-sig"), "relatorio_cpc.csv", "text/csv", type="primary")
    resumo = {"emitido_em": datetime.now().isoformat(), "registros": filtrado, "previsto":sum(x["honorario"] for x in filtrado), "recebido":sum(recebido(x) for x in filtrado), "saldo":sum(saldo(x) for x in filtrado)}
    st.download_button("⬇️ Baixar backup JSON", json.dumps(resumo, ensure_ascii=False, indent=2).encode("utf-8"), "relatorio_cpc.json", "application/json")
    st.caption("Nesta versão de arquivo único, o relatório é exportado em CSV e JSON. O PDF será recolocado quando conectarmos um banco ou uma biblioteca de geração de PDF estável.")


def pagina_documentos() -> None:
    cabecalho("Documentos")
    st.info("Modo demonstração: a tela de documentos será persistida quando o banco de dados for conectado.")
    arq = st.file_uploader("Selecionar documento", type=["pdf", "docx", "xlsx", "png", "jpg"])
    if arq:
        st.success(f"Documento selecionado: {arq.name}. Nesta demonstração ele não é armazenado permanentemente.")


def pagina_configuracoes() -> None:
    cabecalho("Configurações")
    st.subheader("Dados de demonstração")
    a,b = st.columns(2)
    with a:
        if st.button("↩️ Restaurar base inicial", use_container_width=True):
            st.session_state.calculos = dados_iniciais(); st.rerun()
    with b:
        backup = json.dumps(st.session_state.calculos, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button("⬇️ Baixar backup JSON", backup, "backup_cpc.json", "application/json", use_container_width=True)
    st.write("**Regra de honorários prevista para a versão definitiva:** percentual, valor fixo, modelo misto e ajuste manual.")
    st.write("**Próxima etapa recomendada:** conectar Supabase ou Neon para preservar processos, pagamentos, documentos e cobranças.")


iniciar()
estilo()
sidebar()

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
