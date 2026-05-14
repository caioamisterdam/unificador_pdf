import streamlit as st
from PyPDF2 import PdfMerger
from streamlit_sortables import sort_items
import io
import os

# Configuração da página
st.set_page_config(page_title="Unificador de PDFs", page_icon="📄", layout="centered")

# --- CUSTOMIZAÇÃO VISUAL (CSS) ---
# Aqui mudamos a cor para azul claro e garantimos o layout vertical
st.markdown("""
    <style>
    /* Estiliza os itens do sortable para azul claro e margem vertical */
    .stSortableList div[data-testid="stMarkdownContainer"] {
        background-color: #e1f5fe !important; /* Azul clarinho */
        color: #01579b !important; /* Texto azul escuro para contraste */
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 8px; /* Força um abaixo do outro */
        border: 1px solid #b3e5fc;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Unificador de PDFs")
st.markdown("Arraste os arquivos para baixo ou para cima para definir a ordem final.")

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
    
    # O componente de arrastar e soltar
    # Agora formatado via CSS acima para ser azul e vertical
    ordem_final = sort_items(nomes_arquivos, direction="vertical")

    st.write("---")
    
    if st.button("🚀 Gerar PDF Unificado", type="primary"):
        merger = PdfMerger()
        
        try:
            with st.spinner("Unindo arquivos..."):
                for nome in ordem_final:
                    merger.append(arquivos_dict[nome])
                
                # Lógica do nome: Primeiro arquivo da lista + _unificado
                primeiro_nome = ordem_final[0]
                nome_base = os.path.splitext(primeiro_nome)[0]
                nome_final = f"{nome_base}_unificado.pdf"
                
                # Gera o arquivo em memória
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                # Formata o tamanho final com vírgula (padrão brasileiro)
                tamanho_final = f"{len(output.getvalue()) / (1024 * 1024):.2f}".replace('.', ',')
                
                st.success(f"Tudo pronto! Arquivo: **{nome_final}** ({tamanho_final} MB)")
                
                st.download_button(
                    label="📥 Baixar Agora",
                    data=output.getvalue(),
                    file_name=nome_final,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

else:
    st.info("Aguardando o upload de arquivos.")
