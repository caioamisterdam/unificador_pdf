import streamlit as st
from PyPDF2 import PdfMerger
from streamlit_sortables import sort_items
import io
import os

# Configuração da página
st.set_page_config(page_title="Unificador de PDFs", page_icon="⚖️", layout="centered")

# --- CSS PARA NÚMEROS FIXOS E VISUAL AZUL ---
st.markdown("""
    <style>
    /* Container principal da lista */
    .stSortableList {
        counter-reset: linha-pdf; 
        padding-left: 45px; /* Espaço para os números fixos à esquerda */
    }
    
    /* Estilização de cada barra (card) de arquivo */
    .stSortableList div[data-testid="stMarkdownContainer"] {
        background-color: #e3f2fd !important; /* Azul claro suave */
        color: #0d47a1 !important; /* Texto em azul escuro para leitura */
        border-radius: 6px;
        padding: 12px 18px;
        margin-bottom: 10px;
        border: 1px solid #bbdefb;
        position: relative;
        cursor: grab;
        transition: transform 0.2s;
    }

    /* O número fixo que fica à esquerda, fora da barra azul */
    .stSortableList div[data-testid="stMarkdownContainer"]::before {
        counter-increment: linha-pdf;
        content: counter(linha-pdf); 
        position: absolute;
        left: -40px; /* Posiciona o número fora do box */
        top: 50%;
        transform: translateY(-50%);
        font-weight: bold;
        color: #455a64;
        font-size: 1.2em;
        width: 30px;
        text-align: right;
    }
    
    /* Efeito visual ao arrastar */
    .stSortableList div[data-testid="stMarkdownContainer"]:active {
        cursor: grabbing;
        background-color: #bbdefb !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Unificador de PDFs")
st.markdown("Arraste os arquivos para as linhas numeradas abaixo para definir a sequência.")

# 1. Upload de arquivos
uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    # Mapeamento para garantir que o conteúdo siga o nome
    arquivos_dict = {f.name: f for f in uploaded_files}
    nomes_arquivos = list(arquivos_dict.keys())

    st.write("---")
    st.subheader("Defina a Ordem de União")
    
    # 2. Interface de arrastar (Vertical)
    ordem_final = sort_items(nomes_arquivos, direction="vertical")

    st.write("---")
    
    # 3. Botão para processar
    if st.button("🚀 Gerar PDF Unificado", type="primary"):
        merger = PdfMerger()
        
        try:
            with st.spinner("Unindo documentos..."):
                for nome in ordem_final:
                    merger.append(arquivos_dict[nome])
                
                # Regra de nome: Primeiro arquivo da lista ordenada + _unificado
                primeiro_nome = ordem_final[0]
                nome_base = os.path.splitext(primeiro_nome)[0]
                nome_final = f"{nome_base}_unificado.pdf"
                
                # Gera o PDF em memória (segurança e performance)
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                # Formatação do tamanho com vírgula (padrão brasileiro)
                tamanho_final = f"{len(output.getvalue()) / (1024 * 1024):.2f}".replace('.', ',')
                
                st.success(f"União concluída! Arquivo: **{nome_final}** ({tamanho_final} MB)")
                
                st.download_button(
                    label="📥 Baixar PDF Final",
                    data=output.getvalue(),
                    file_name=nome_final,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar os arquivos: {e}")

else:
    st.info("Aguardando o upload de documentos para começar.")
