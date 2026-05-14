import streamlit as st
from PyPDF2 import PdfMerger
from streamlit_sortables import sort_items
import io
import os

# Configuração da página e título
st.set_page_config(page_title="Unificador de PDFs", page_icon="⚖️", layout="centered")

# --- CSS PARA NÚMEROS FIXOS E VISUAL AZUL CLARO ---
st.markdown("""
    <style>
    /* Container da lista para criar o efeito de linhas fixas */
    .stSortableList {
        counter-reset: linha-pdf; 
        padding-left: 40px; /* Espaço para o número fixo do lado de fora */
    }
    
    /* Estilização do item (a 'linha' onde o arquivo entra) */
    .stSortableList div[data-testid="stMarkdownContainer"] {
        background-color: #e3f2fd !important; /* Azul clarinho */
        color: #0d47a1 !important; /* Texto em azul escuro */
        border-radius: 4px;
        padding: 10px 15px;
        margin-bottom: 8px;
        border: 1px solid #bbdefb;
        position: relative;
        cursor: grab;
    }

    /* O número fixo que fica à esquerda do card */
    .stSortableList div[data-testid="stMarkdownContainer"]::before {
        counter-increment: linha-pdf;
        content: counter(linha-pdf); /* Apenas o número */
        position: absolute;
        left: -35px; /* Joga o número para fora do box azul */
        top: 50%;
        transform: translateY(-50%);
        font-weight: bold;
        color: #555;
        font-size: 1.1em;
        width: 25px;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Unificador de PDFs")
st.markdown("Arraste os arquivos para as linhas numeradas abaixo para definir a sequência.")

# Upload de arquivos
uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    # Mapeamento para processamento
    arquivos_dict = {f.name: f for f in uploaded_files}
    nomes_arquivos = list(arquivos_dict.keys())

    st.write("---")
    st.subheader("Ordem de União")
    
    # Interface de arrastar (Vertical) com a numeração fixa via CSS
    ordem_final = sort_items(nomes_arquivos, direction="vertical")

    st.write("---")
    
    if st.button("🚀 Unir PDFs nas Linhas Definidas", type="primary"):
        merger = PdfMerger()
        
        try:
            with st.spinner("Unindo documentos..."):
                for nome in ordem_final:
                    merger.append(arquivos_dict[nome])
                
                # Regra de nome: Primeiro arquivo + _unificado
                primeiro_nome = ordem_final[0]
                nome_base = os.path.splitext(primeiro_nome)[0]
                nome_final = f"{nome_base}_unificado.pdf"
                
                # Processamento em memória para segurança
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                # Tamanho com vírgula conforme sua preferência
                tamanho_final = f"{len(output.getvalue()) / (1024 * 1024):.2f}".replace('.', ',')
                
                st.success(f"União concluída! Arquivo: **{nome_final}** ({tamanho_final} MB)")
                
                st.download_button(
                    label="📥 Baixar PDF Final",
                    data=output.getvalue(),
                    file_name=nome_final,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
else:
    st.info("Por favor, carregue os arquivos para começar.")
