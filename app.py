import streamlit as st
from PyPDF2 import PdfMerger, PdfReader
from streamlit_sortables import sort_items
import io
import os
import re

# Configuração da página padrão do Streamlit
st.set_page_config(page_title="Unificador de PDFs", page_icon="⚖️", layout="centered")

st.title("📄 Unificador de PDFs")


# --- CONTROLE DE MEMÓRIA PARA RESETAR O UPLOADER ---
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# O 'key' dinâmico garante que o uploader limpe quando o botão for clicado
uploaded_files = st.file_uploader(
    "Arraste os arquivos PDF aqui ou clique em 'Upload' para selecionar", 
    type="pdf", 
    accept_multiple_files=True,
    key=f"pdf_uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    # Botão de Limpar posicionado logo após o upload para conveniência
    if st.button("🧹 Limpar Arquivos", type="secondary"):
        st.session_state.uploader_key += 1
        st.rerun()

    # Mapeia o nome do arquivo ao objeto real
    arquivos_dict = {f.name: f for f in uploaded_files}
    nomes_arquivos = list(arquivos_dict.keys())

    st.write("---")
    st.subheader("Defina a Ordem de União")
    st.markdown("Arraste os arquivos para cima ou para baixo para definir a ordem final. A minuta deve ficar embaixo.")
   
    # Componente padrão de arrastar na vertical
    ordem_final = sort_items(nomes_arquivos, direction="vertical")

    st.write("---")
    st.subheader("Nome do Arquivo de Saída")
    
    # --- LÓGICA DE IDENTIFICAÇÃO DO PROCESSO REFORÇADA ---
    sugestao_nome = ""
    padrao_cnj = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
    
    # 1. TENTATIVA A: Ler a primeira página do menor arquivo procurando por "Processo nº"
    try:
        arquivo_menor = min(uploaded_files, key=lambda f: f.size)
        reader = PdfReader(arquivo_menor)
        if len(reader.pages) > 0:
            texto_primeira_pagina = reader.pages[0].extract_text()
            
            if texto_primeira_pagina:
                match_texto = re.search(r'Processo\s*(?:nº|n°|n\.|º|°|:)?\s*([\d\.\-]+)', texto_primeira_pagina, re.IGNORECASE)
                if match_texto:
                    numero_extraido = match_texto.group(1).strip().rstrip('.-')
                    if sum(c.isdigit() for c in numero_extraido) >= 10:
                        sugestao_nome = numero_extraido
    except Exception:
        pass

    # 2. TENTATIVA B (Filtro Anti-Sufixo/Prefixos): Isola o CNJ puro do nome do arquivo
    if not sugestao_nome:
        for f in uploaded_files:
            match_nome = re.search(padrao_cnj, f.name)
            if match_nome:
                sugestao_nome = match_nome.group(0) 
                break

    # 3. TENTATIVA C: Caso não haja formato CNJ padrão, limpa termos comuns
    if not sugestao_nome:
        arquivo_menor = min(uploaded_files, key=lambda f: f.size)
        nome_base = os.path.splitext(arquivo_menor.name)[0].strip()
        nome_base = re.sub(r'[-_ ]*(minuta|peticao|inicial|contestacao|procuracao|substabelecimento).*$', '', nome_base, flags=re.IGNORECASE)
        sugestao_nome = nome_base.strip().rstrip('.-')
        
    # Campo interativo para confirmar ou digitar o número do processo
    nome_processo = st.text_input(
        "Número do Processo capturado (Nome do arquivo final):", 
        value=sugestao_nome,
        help="O sistema remove automaticamente prefixos ou sufixos para deixar apenas o número limpo."
    )
    
    # Garante a extensão .pdf no final do nome escolhido
    if not nome_processo.lower().endswith('.pdf'):
        nome_final = f"{nome_processo}.pdf"
    else:
        nome_final = nome_processo

    st.write("---")
    
    if st.button("🚀 Gerar PDF Unificado", type="primary"):
        merger = PdfMerger()
        
        try:
            with st.spinner("Unindo documentos..."):
                for nome in ordem_final:
                    merger.append(arquivos_dict[nome])
                
                # Gera o arquivo em memória para segurança
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                # Formata o tamanho final com a vírgula brasileira
                tamanho_mb = len(output.getvalue()) / (1024 * 1024)
                tamanho_final = f"{tamanho_mb:.2f}".replace('.', ',')
                
                st.success(f"União concluída! Arquivo pronto: **{nome_final}** ({tamanho_final} MB)")
                
                # Botão de download
                st.download_button(
                    label="📥 Baixar PDF Final",
                    data=output.getvalue(),
                    file_name=nome_final,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar os arquivos: {e}")
else:
    st.info("Aguardando o upload de arquivos para começar.")
