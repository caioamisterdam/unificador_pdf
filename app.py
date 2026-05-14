import streamlit as st
from PyPDF2 import PdfMerger
from streamlit_sortables import sort_items
import io
import os

# Configuração da página
st.set_page_config(page_title="Unificador de PDFs", page_icon="⚖️", layout="centered")

# --- CSS REFORÇADO PARA NÚMEROS FIXOS E COR AZUL ---
st.markdown("""
    <style>
    /* 1. Remove o vermelho e aplica o azul claro em cada item */
    div[data-testid="stMarkdownContainer"] > div[style*="background-color: rgb(255, 75, 75)"], 
    div[style*="background-color: #ff4b4b"],
    .stSortableList div {
        background-color: #e3f2fd !important; /* Azul claro */
        color: #0d47a1 !important; /* Texto azul escuro */
        border: 1px solid #bbdefb !important;
        border-radius: 8px !important;
    }

    /* 2. Cria o espaço para os números fixos à esquerda */
    .stSortableList {
        counter-reset: pdf-row;
        padding-left: 40px !important;
    }

    /* 3. Adiciona os números fixos (eles não se movem com o arquivo) */
    .stSortableList > div {
        position: relative;
        margin-bottom: 12px !important;
    }

    .stSortableList > div::before {
        counter-increment: pdf-row;
        content: counter(pdf-row);
        position: absolute;
        left: -35px;
        top: 50%;
        transform: translateY(-50%);
        font-weight: bold;
        color: #1e88e5;
        font-size: 1.1rem;
        width: 25px;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Unificador de PDFs")
st.markdown("Arraste os arquivos para as posições numeradas abaixo.")

# Upload de arquivos
uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    # Mapeia nome ao arquivo real
    arquivos_dict = {f.name: f for f in uploaded_files}
    nomes_arquivos = list(arquivos_dict.keys())

    st.write("---")
    st.subheader("Ordem de União")
    
    # Componente de arrastar (Vertical)
    # Os números fixos são injetados via CSS acima
    ordem_final = sort_items(nomes_arquivos, direction="vertical")

    st.write("---")
    
    if st.button("🚀 Gerar PDF Unificado", type="primary"):
        merger = PdfMerger()
        
        try:
            with st.spinner("Processando documentos..."):
                for nome in ordem_final:
                    merger.append(arquivos_dict[nome])
                
                # Nome: Primeiro da lista + _unificado
                primeiro_nome = ordem_final[0]
                nome_base = os.path.splitext(primeiro_nome)[0]
                nome_final = f"{nome_base}_unificado.pdf"
                
                # Saída em memória
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                # Formata tamanho com vírgula (padrão brasileiro)
                tamanho_bytes = len(output.getvalue())
                tamanho_final = f"{tamanho_bytes / (1024 * 1024):.2f}".replace('.', ',')
                
                st.success(f"União concluída! Arquivo: **{nome_final}** ({tamanho_final} MB)")
                
                st.download_button(
                    label="📥 Baixar PDF Final",
                    data=output.getvalue(),
                    file_name=nome_final,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
else:
    st.info("Carregue os PDFs para definir a ordem.")
