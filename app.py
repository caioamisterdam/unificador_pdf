import streamlit as st
from PyPDF2 import PdfMerger, PdfReader
from streamlit_sortables import sort_items
import io
import os
import re

# Configuração da página padrão do Streamlit
st.set_page_config(page_title="Unificador de PDFs", page_icon="⚖️", layout="centered")

st.title("📄 Unificador de PDFs")

# Componente de upload
uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
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
                # Captura formatos numéricos após o termo "Processo"
                match_texto = re.search(r'Processo\s*(?:nº|n°|n\.|º|°|:)?\s*([\d\.\-]+)', texto_primeira_pagina, re.IGNORECASE)
                if match_texto:
                    numero_extraido = match_texto.group(1).strip().rstrip('.-')
                    # Valida se o que foi extraído tem tamanho de processo
                    if sum(c.isdigit() for c in numero_extraido) >= 10:
                        sugestao_nome = numero_extraido
    except Exception:
        pass

    # 2. TENTATIVA B (Filtro Anti-Sufixo): Se o texto falhou (ex: PDF escaneado),
    # vasculha os NOMES dos arquivos procurando pelo formato CNJ puro para eliminar o "-minuta"
    if not sugestao_nome:
        for f in uploaded_files:
            match_nome = re.search(padrao_cnj, f.name)
            if match_nome:
                sugestao_nome = match_nome.group(0) # Captura APENAS o número padrão CNJ
                break

    # 3. TENTATIVA C (Caso não haja formato CNJ padrão): Pega o nome do menor e limpa textos conhecidos
    if not sugestao_nome:
        arquivo_menor = min(uploaded_files, key=lambda f: f.size)
        nome_base = os.path.splitext(arquivo_menor.name)[0].strip()
        # Remove palavras comuns de sufixo judiciais
        nome_base = re.sub(r'[-_ ]*(minuta|peticao|inicial|contestacao|procuracao|substabelecimento).*$', '', nome_base, flags=re.IGNORECASE)
        sugestao_nome = nome_base.strip().rstrip('.-')
        
    # Campo interativo para confirmar ou digitar o número do processo
    nome_processo = st.text_input(
        "Número do Processo capturado:", 
        value=sugestao_nome,
        help="O sistema limpa automaticamente termos como '-minuta' para deixar apenas o número limpo."
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
                
                # Botão de download com o nome limpo
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
