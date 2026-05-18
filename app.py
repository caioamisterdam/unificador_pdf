import streamlit as st
from PyPDF2 import PdfMerger, PdfReader
import io
import os
import re

# Configuração da página padrão do Streamlit
st.set_page_config(page_title="Unificador de PDFs", page_icon="⚖️", layout="centered")

st.title("📄 Unificador de PDFs")
st.markdown("Arraste os arquivos para cima ou para baixo para definir a ordem final na vertical.")

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
    
    # Componente padrão de arrastar na vertical
    from streamlit_sortables import sort_items
    ordem_final = sort_items(nomes_arquivos, direction="vertical")

    st.write("---")
    st.subheader("Nome do Arquivo de Saída")
    
    # --- LÓGICA DE LEITURA INTERNA DO MENOR ARQUIVO ---
    sugestao_nome = ""
    
    try:
        # 1. Encontra o menor arquivo por tamanho em bytes
        arquivo_menor = min(uploaded_files, key=lambda f: f.size)
        
        # 2. Lê a primeira página do menor arquivo
        reader = PdfReader(arquivo_menor)
        if len(reader.pages) > 0:
            texto_primeira_pagina = reader.pages[0].extract_text()
            
            if texto_primeira_pagina:
                # 3. Procura por "Processo nº" seguido por números, pontos ou traços
                # Captura formatos como "Processo nº 1005058-94.2026.8.26.0053"
                match = re.search(r'Processo\s*(?:nº|n°|n\.|º|°|:)?\s*([\d\.\-]+)', texto_primeira_pagina, re.IGNORECASE)
                if match:
                    sugestao_nome = match.group(1).strip()
                    # Remove pontuações que possam ter ficado presas no final do número
                    sugestao_nome = sugestao_nome.rstrip('.-')
    except Exception as e:
        # Se o PDF for protegido ou houver erro na leitura, ignora e usa o plano B
        pass

    # Plano B: Caso não encontre o texto ou o PDF seja uma imagem escaneada sem OCR
    if not sugestao_nome:
        arquivo_menor = min(uploaded_files, key=lambda f: f.size)
        sugestao_nome = os.path.splitext(arquivo_menor.name)[0].strip()
        
    # Campo interativo para confirmar ou digitar o número do processo
    nome_processo = st.text_input(
        "Número do Processo capturado internamente:", 
        value=sugestao_nome,
        help="O sistema leu a 1ª página do menor arquivo e extraiu o número após 'Processo nº'."
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
                
                # Botão de download com o nome capturado do texto
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
