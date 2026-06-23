# -*- coding: utf-8 -*-
"""CPC — Controle Pessoal de Cálculos e Recebimentos.
Versão sem dependências externas além do Streamlit já fornecido pelo Community Cloud.
"""
from __future__ import annotations

import base64
import csv
import io
import json
from datetime import date
from pathlib import Path
from uuid import uuid4

import streamlit as st

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "data" / "dados_demo.json"
LOGO_FILE = APP_DIR / "assets" / "logo_cpc.png"

st.set_page_config(page_title="CPC — Controle Pessoal de Cálculos e Recebimentos", page_icon="📊", layout="wide", initial_sidebar_state="expanded")


def money(value: float) -> str:
    return f"R$ {float(value or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def load_base() -> dict:
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"calculos": []}


def init_state() -> None:
    if "base" not in st.session_state:
        st.session_state.base = load_base()
    if "page" not in st.session_state:
        st.session_state.page = "Painel"
    if "new_calc" not in st.session_state:
        st.session_state.new_calc = False


def records() -> list[dict]:
    return st.session_state.base.setdefault("calculos", [])


def balance(item: dict) -> float:
    return max(float(item.get("honorario", 0)) - float(item.get("recebido", 0)), 0.0)


def status_class(status: str) -> str:
    return {
        "Em andamento": "blue", "Entregue": "teal", "Aguardando cobrança": "orange",
        "Em revisão": "purple", "Quitado": "green", "Cancelado": "red"
    }.get(status, "gray")


def app_css() -> None:
    st.markdown("""
<style>
:root{--navy:#0D3158;--teal:#0B9E9A;--bg:#F8FAFD;--border:#E6ECF4;--muted:#72829A;}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden}
.stApp{background:var(--bg);color:var(--navy)}
.block-container{padding:0 2rem 2rem 2rem;max-width:1600px}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--border);min-width:264px;max-width:264px}
[data-testid="stSidebar"]>div:first-child{padding:0 14px}
[data-testid="stSidebar"] .stButton>button{border:0!important;background:transparent!important;box-shadow:none!important;color:#17345A!important;justify-content:flex-start!important;min-height:46px;padding:0 14px!important;border-radius:10px!important;font-weight:600!important;font-size:15px!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:#EAF8F7!important;color:#0B8F90!important;position:relative}
[data-testid="stSidebar"] .stButton>button[kind="primary"]:before{content:"";position:absolute;left:0;top:9px;bottom:9px;width:4px;border-radius:6px;background:#11A7A2}
.topbar{height:84px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);margin:0 -2rem 24px -2rem;padding:0 2rem;background:#fff}
.top-title{font-size:31px;font-weight:800;color:#10365F;letter-spacing:-1px;margin:0}.top-sub{color:#718198;font-size:13px;margin-top:3px}
.header-tools{display:flex;align-items:center;gap:16px}.search-mock{border:1px solid #D7E1ED;border-radius:12px;height:45px;width:315px;padding:0 14px;display:flex;align-items:center;color:#91A0B3;font-size:13px}.bell{font-size:22px;position:relative}.bell span{position:absolute;right:-10px;top:-8px;background:#0A9A95;color:#fff;width:18px;height:18px;line-height:18px;text-align:center;border-radius:50%;font-size:11px;font-weight:800}.avatar{display:inline-flex;width:34px;height:34px;border-radius:50%;background:#103C68;color:#fff;align-items:center;justify-content:center;font-weight:800;font-size:12px}
.metric{background:#fff;border:1px solid var(--border);border-radius:13px;padding:17px;min-height:116px;box-shadow:0 3px 12px rgba(32,66,105,.06);display:flex;gap:14px}.mi{width:48px;height:48px;border-radius:10px;background:#EAF1F7;display:flex;align-items:center;justify-content:center;color:#123E6B;font-size:25px;flex:0 0 auto}.mi.teal{background:#DDF6F4;color:#098E8B}.mi.green{background:#E0F7F1;color:#039C85}.mi.gray{background:#EEF2F7;color:#173E66}.mi.aqua{background:#E7F8F5;color:#069B83}.ml{color:#4E627C;font-size:13px;font-weight:600;margin-top:1px}.mv{color:#0E345E;font-size:23px;font-weight:800;line-height:1.2;margin-top:5px}.mh{color:#099A98;font-size:12px;margin-top:7px;font-weight:600}
.card{background:#fff;border:1px solid var(--border);border-radius:13px;padding:14px 16px;box-shadow:0 3px 12px rgba(32,66,105,.05);height:100%}.card h3{font-size:14px;font-weight:800;color:#14385F;margin:0 0 10px}.chart{height:220px;position:relative;border-bottom:1px solid #E7EDF4;background:repeating-linear-gradient(to bottom,#fff 0,#fff 42px,#EAF0F6 43px,#fff 44px)}.line{position:absolute;left:4%;right:4%;top:30px;height:150px;background:linear-gradient(145deg,transparent 0 7%,rgba(11,158,154,.12) 8% 100%);clip-path:polygon(0 70%,18% 48%,36% 72%,55% 23%,75% 42%,100% 18%,100% 100%,0 100%)}.line:after{content:"";position:absolute;inset:0;background:#0B9E9A;clip-path:polygon(0 69%,18% 47%,36% 71%,55% 22%,75% 41%,100% 17%,100% 20%,75% 44%,55% 25%,36% 74%,18% 50%,0 72%)}.chart-labels{display:flex;justify-content:space-between;color:#7A8A9D;font-size:11px;margin-top:10px}
.donut-wrap{display:flex;align-items:center;gap:18px}.donut{width:145px;height:145px;border-radius:50%;background:conic-gradient(#0D3158 0 34%,#0B9E9A 34% 56%,#FFB438 56% 73%,#5581E9 73% 87%,#B7C2D0 87% 95%,#E1E7EF 95% 100%);position:relative}.donut:after{content:"36\A total";white-space:pre;position:absolute;inset:28px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;text-align:center;color:#14385F;font-weight:800;line-height:1.2}.legend{font-size:11px;color:#52657D;line-height:1.9}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}.action{display:grid;grid-template-columns:36px 1fr 46px 48px;gap:8px;align-items:center;padding:10px 0;border-bottom:1px solid #EDF1F6}.aico{width:32px;height:32px;border-radius:7px;background:#E5F8F5;color:#0B978A;display:flex;align-items:center;justify-content:center}.at{font-size:12px;font-weight:800;color:#1C405F}.as{font-size:11px;color:#78879A;margin-top:2px}.time{font-size:11px;color:#728298;text-align:right}.tag{padding:4px 7px;border-radius:6px;font-size:10px;font-weight:700;text-align:center}.orange{background:#FFF0D7;color:#C47713}.red{background:#FFE7E7;color:#B93838}.green{background:#DFF6E9;color:#198355}.blue{background:#E6EFFF;color:#2964C6}.teal{background:#DCF7F2;color:#078570}.purple{background:#ECE8FF;color:#6552B0}.gray{background:#EEF2F6;color:#667588}
.table-wrap{background:#fff;border:1px solid var(--border);border-radius:13px;padding:14px 16px;box-shadow:0 3px 12px rgba(32,66,105,.05)}table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;color:#405773;padding:11px;border-bottom:1px solid #E8EEF4}td{padding:11px;border-bottom:1px solid #EEF2F6;color:#34506E}.proc{color:#2D6BC7;font-weight:700}.right{text-align:right}.side-user{border-top:1px solid #E6ECF4;margin:25px 8px 0;padding:15px 0;color:#6C7D91;font-size:12px}.stButton>button,.stDownloadButton>button{border-radius:9px;font-weight:700;border-color:#D8E3EF;color:#143B63;min-height:38px}.stButton>button[kind="primary"]{background:#0B9B99;border-color:#0B9B99;color:#fff}
</style>
""", unsafe_allow_html=True)


def title(name: str, subtitle: str) -> None:
    st.markdown(f"""<div class='topbar'><div><div class='top-title'>{name}</div><div class='top-sub'>{subtitle}</div></div><div class='header-tools'><div class='search-mock'>⌕ &nbsp; Buscar processos, clientes, recibos...</div><div class='bell'>♧<span>3</span></div><div class='avatar'>VS</div>⌄</div></div>""", unsafe_allow_html=True)


def metric(col, icon: str, label: str, value: str, help_text: str, theme: str="") -> None:
    with col:
        st.markdown(f"<div class='metric'><div class='mi {theme}'>{icon}</div><div><div class='ml'>{label}</div><div class='mv'>{value}</div><div class='mh'>{help_text}</div></div></div>", unsafe_allow_html=True)


def panel() -> None:
    title("Painel Geral", "Visão integrada dos cálculos, honorários, recebimentos e cobranças.")
    data = records()
    total = sum(float(x.get("honorario",0)) for x in data)
    paid = sum(float(x.get("recebido",0)) for x in data)
    pending = sum(balance(x) for x in data)
    active = sum(1 for x in data if x.get("situacao") == "Em andamento")
    cols = st.columns(5, gap="small")
    metric(cols[0], "▤", "Cálculos em andamento", str(active), "+2 desde ontem")
    metric(cols[1], "$", "Honorários previstos no mês", money(total), "+12% vs. mês anterior", "teal")
    metric(cols[2], "↗", "Valores recebidos no mês", money(paid), "+8% vs. mês anterior", "green")
    metric(cols[3], "▣", "Saldo pendente", money(pending), f"{sum(1 for x in data if balance(x)>0)} processos", "gray")
    metric(cols[4], "▦", "Cobranças próximas", "7", "próximos 7 dias", "aqua")
    st.write("")
    c1,c2,c3 = st.columns([1.4,.9,.95], gap="small")
    with c1:
        st.markdown("<div class='card'><h3>Recebimentos nos últimos 6 meses <span style='float:right;color:#6B7E96;font-weight:600'>Últimos 6 meses⌄</span></h3><div class='chart'><div class='line'></div></div><div class='chart-labels'><span>Jan/26</span><span>Fev/26</span><span>Mar/26</span><span>Abr/26</span><span>Mai/26</span><span>Jun/26</span></div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class='card'><h3>Status dos processos</h3><div class='donut-wrap'><div class='donut'></div><div class='legend'><span class='dot' style='background:#0D3158'></span>12 &nbsp; Em andamento<br><span class='dot' style='background:#0B9E9A'></span>8 &nbsp; Entregue<br><span class='dot' style='background:#FFB438'></span>6 &nbsp; Aguardando cobrança<br><span class='dot' style='background:#5581E9'></span>5 &nbsp; Em revisão<br><span class='dot' style='background:#B7C2D0'></span>3 &nbsp; Cancelado<br><span class='dot' style='background:#E1E7EF'></span>2 &nbsp; Finalizado</div></div></div>""", unsafe_allow_html=True)
    with c3:
        actions = [("▤","Enviar cálculo para revisão","Proc. 0001234-45.2024.5.05.0001","09:30","Alta","red"),("✉","Enviar cobrança","3 processos","11:00","Média","orange"),("☎","Ligar para cliente","João da Silva","14:00","Média","orange"),("▱","Revisar documentos","2 documentos","16:30","Baixa","green")]
        html = "<div class='card'><h3>Ações de hoje</h3>"
        for ico,txt,sub,t,prio,css in actions:
            html += f"<div class='action'><div class='aico'>{ico}</div><div><div class='at'>{txt}</div><div class='as'>{sub}</div></div><div class='time'>{t}</div><div class='tag {css}'>{prio}</div></div>"
        html += "<div style='padding-top:12px;color:#2D6BC7;font-size:12px;font-weight:700'>Ver todas as ações &nbsp; →</div></div>"
        st.markdown(html, unsafe_allow_html=True)
    st.write("")
    header,button = st.columns([5,1])
    with header: st.markdown("<h3 style='margin:0;color:#14385F;font-size:14px'>Processos recentes</h3>", unsafe_allow_html=True)
    with button:
        if st.button("Ver todos os processos →", use_container_width=True):
            st.session_state.page = "Processos e Cálculos"; st.rerun()
    rows = ""
    for item in data:
        tag = status_class(item.get("situacao",""))
        rows += f"<tr><td class='proc'>{item.get('processo','')}</td><td>{item.get('cliente','')}</td><td>{item.get('servico','')}</td><td><span class='tag {tag}'>{item.get('situacao','')}</span></td><td>{money(item.get('honorario',0))}</td><td class='right'>{money(balance(item))}</td><td>{item.get('atualizacao','')}</td><td>⋮</td></tr>"
    st.markdown(f"<div class='table-wrap'><table><thead><tr><th>Processo</th><th>Cliente</th><th>Tipo de serviço</th><th>Situação</th><th>Valor</th><th class='right'>Saldo</th><th>Última atualização</th><th></th></tr></thead><tbody>{rows}</tbody></table></div><div style='text-align:center;color:#8491A3;font-size:12px;padding:22px 0 0'>CPC — Controle Pessoal de Cálculos e Recebimentos &nbsp; • &nbsp; Todos os direitos reservados &nbsp;&nbsp; Versão 3.0.0</div>", unsafe_allow_html=True)


def processes() -> None:
    title("Processos e Cálculos", "Cadastre, acompanhe e revise o histórico técnico e financeiro de cada demanda.")
    a,b = st.columns([1,3])
    with a:
        if st.button("➕ Novo cálculo", type="primary", use_container_width=True):
            st.session_state.new_calc = not st.session_state.new_calc
    with b: query = st.text_input("Busca rápida", placeholder="Número do processo, parte, cliente, advogado ou serviço")
    if st.session_state.new_calc:
        with st.form("novo_calculo", clear_on_submit=True):
            st.subheader("Novo cálculo / processo")
            c1,c2,c3 = st.columns(3)
            process_no = c1.text_input("Número do processo *")
            client = c2.text_input("Cliente / escritório")
            service = c3.selectbox("Tipo de serviço", ["Cálculo Trabalhista","Liquidação de Sentença","Revisão de Cálculos","Impugnação de Cálculos","Cálculo Complementar"])
            claimant = c1.text_input("Reclamante")
            respondent = c2.text_input("Reclamado")
            status = c3.selectbox("Situação", ["Em andamento","Entregue","Aguardando cobrança","Em revisão","Quitado","Cancelado"])
            value = c1.number_input("Honorário previsto (R$)", min_value=0.0, step=100.0)
            received = c2.number_input("Valor recebido (R$)", min_value=0.0, step=100.0)
            delivery = c3.date_input("Data de entrega", value=date.today())
            submit = st.form_submit_button("Salvar cálculo", type="primary")
            if submit:
                if not process_no.strip(): st.error("Informe o número do processo.")
                else:
                    records().append({"id":uuid4().hex[:10],"processo":process_no.strip(),"cliente":client,"reclamante":claimant,"reclamado":respondent,"servico":service,"situacao":status,"honorario":value,"recebido":received,"entrega":delivery.isoformat(),"atualizacao":date.today().isoformat()})
                    st.session_state.new_calc = False; st.success("Cálculo registrado nesta sessão."); st.rerun()
    shown = records()
    if query.strip():
        q=query.casefold().strip()
        shown=[x for x in shown if q in " ".join(str(v) for v in x.values()).casefold()]
    st.write("")
    st.dataframe([{**x,"saldo":balance(x)} for x in shown], use_container_width=True, hide_index=True)


def finance() -> None:
    title("Financeiro", "Acompanhe valores previstos, recebimentos, pagamentos parciais e saldos por processo.")
    data=records(); total=sum(float(x.get("honorario",0)) for x in data); paid=sum(float(x.get("recebido",0)) for x in data); pending=sum(balance(x) for x in data)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Honorários previstos",money(total)); c2.metric("Total recebido",money(paid)); c3.metric("A receber",money(pending)); c4.metric("Processos pendentes",sum(1 for x in data if balance(x)>0))
    options={f"{x['processo']} — saldo {money(balance(x))}":x for x in data if balance(x)>0}
    if options:
        st.subheader("Lançar pagamento")
        sel=st.selectbox("Selecione o cálculo",list(options)); item=options[sel]
        with st.form("pagamento"):
            amount=st.number_input("Valor recebido (R$)",min_value=0.01,max_value=balance(item),step=50.0)
            when=st.date_input("Data do recebimento",value=date.today())
            method=st.selectbox("Meio de pagamento",["PIX","Transferência","Boleto","Dinheiro","Outro"])
            if st.form_submit_button("Registrar pagamento",type="primary"):
                item["recebido"]=float(item.get("recebido",0))+amount; item["atualizacao"]=when.isoformat()
                if balance(item)<=0.01: item["situacao"]="Quitado"
                st.success(f"Pagamento de {money(amount)} registrado."); st.rerun()
    else: st.success("Não há saldos pendentes.")


def charges() -> None:
    title("Cobranças", "Organize os contatos, registre negociações e mantenha o histórico de cada processo.")
    debt=[x for x in records() if balance(x)>0]
    if not debt: st.success("Não há cobranças em aberto."); return
    options={f"{x['processo']} — saldo {money(balance(x))}":x for x in debt}; selected=st.selectbox("Selecione o processo",list(options)); item=options[selected]
    msg=f"Prezado(a),\n\nConforme o trabalho técnico realizado no processo nº {item['processo']}, permanece pendente o saldo de honorários no valor de {money(balance(item))}.\n\nPeço a gentileza de verificar a possibilidade de pagamento.\n\nAtenciosamente,\nVítor Soares"
    st.text_area("Mensagem para WhatsApp ou e-mail",value=msg,height=210)
    st.caption("A mensagem é gerada para copiar e enviar. Esta demonstração não envia comunicações automaticamente.")


def pdf_bytes(title_text: str, lines: list[str]) -> bytes:
    # PDF mínimo em padrão básico, produzido apenas com biblioteca nativa.
    text="\\n".join(line.replace("(","[").replace(")","]") for line in lines)
    stream=f"BT /F1 12 Tf 50 790 Td ({title_text}) Tj 0 -22 Td ({text.replace(chr(10), ') Tj 0 -16 Td (')}) Tj ET"
    objs=["<< /Type /Catalog /Pages 2 0 R >>","<< /Type /Pages /Kids [3 0 R] /Count 1 >>","<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>","<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",f"<< /Length {len(stream.encode('latin-1','replace'))} >>\nstream\n{stream}\nendstream"]
    out=io.BytesIO(); out.write(b"%PDF-1.4\n"); offsets=[0]
    for idx,obj in enumerate(objs,1): offsets.append(out.tell()); out.write(f"{idx} 0 obj\n{obj}\nendobj\n".encode("latin-1","replace"))
    xref=out.tell(); out.write(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode());
    for off in offsets[1:]: out.write(f"{off:010} 00000 n \n".encode())
    out.write(f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()); return out.getvalue()


def reports() -> None:
    title("Relatórios", "Aplique filtros e gere relatórios financeiros, por cliente ou por processo.")
    data=records(); process_opts=[x["processo"] for x in data]; selected=st.multiselect("Processos",process_opts)
    shown=[x for x in data if not selected or x["processo"] in selected]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Registros",len(shown)); c2.metric("Previsto",money(sum(float(x.get('honorario',0)) for x in shown))); c3.metric("Recebido",money(sum(float(x.get('recebido',0)) for x in shown))); c4.metric("Saldo",money(sum(balance(x) for x in shown)))
    st.dataframe([{**x,"saldo":balance(x)} for x in shown],use_container_width=True,hide_index=True)
    lines=[f"{x['processo']} | {x.get('cliente','')} | Previsto {money(x.get('honorario',0))} | Recebido {money(x.get('recebido',0))} | Saldo {money(balance(x))}" for x in shown]
    st.download_button("📄 Baixar relatório em PDF",pdf_bytes("Relatorio CPC",lines),"relatorio_cpc.pdf","application/pdf",type="primary")
    sio=io.StringIO(); writer=csv.DictWriter(sio,fieldnames=["processo","cliente","reclamante","reclamado","servico","situacao","honorario","recebido","entrega","atualizacao"]); writer.writeheader(); writer.writerows(shown)
    st.download_button("⬇️ Baixar relatório em CSV",sio.getvalue().encode("utf-8-sig"),"relatorio_cpc.csv","text/csv")


def documents() -> None:
    title("Documentos", "Catalogue cálculos, relatórios, propostas, recibos, comprovantes e peças vinculadas a cada processo.")
    st.info("Modo de demonstração: os documentos podem ser organizados aqui, mas ainda não são armazenados em servidor.")
    st.file_uploader("Selecionar documento",type=["pdf","docx","xlsx","png","jpg"])
    st.text_input("Descrição do documento")
    st.button("Catalogar documento",type="primary")


def settings() -> None:
    title("Configurações", "Defina tipos de serviço, regras de honorários, modelos de cobrança e backup da demonstração.")
    st.subheader("Backup e restauração")
    st.download_button("⬇️ Baixar backup JSON",json.dumps(st.session_state.base,ensure_ascii=False,indent=2).encode("utf-8"),"backup_cpc.json","application/json")
    if st.button("↩️ Restaurar dados iniciais"):
        st.session_state.base=load_base(); st.success("Base inicial restaurada."); st.rerun()


init_state(); app_css()
with st.sidebar:
    if LOGO_FILE.exists(): st.image(str(LOGO_FILE),use_container_width=True)
    else: st.markdown("## CPC\nControle Pessoal de Cálculos e Recebimentos")
    st.caption("Controle pessoal de cálculos, honorários e recebimentos.")
    pages=[("⌂","Painel"),("▤","Processos e Cálculos"),("◉","Financeiro"),("✉","Cobranças"),("▧","Relatórios"),("▱","Documentos"),("⚙","Configurações")]
    for icon,name in pages:
        if st.button(f"{icon}  {name}",key=f"nav_{name}",type="primary" if st.session_state.page==name else "secondary",use_container_width=True): st.session_state.page=name; st.rerun()
    st.markdown("<div class='side-user'><span class='avatar'>VS</span><b>Vítor Soares</b><br><span style='margin-left:44px'>Administrador</span></div>",unsafe_allow_html=True)

{"Painel":panel,"Processos e Cálculos":processes,"Financeiro":finance,"Cobranças":charges,"Relatórios":reports,"Documentos":documents,"Configurações":settings}[st.session_state.page]()
