import streamlit as st
from PyPDF2 import PdfMerger
from streamlit_sortables import sort_items
import io
import os

st.set_page_config(page_title="Unificador de PDFs", page_icon="📄", layout="centered")

st.title("📄 Unificador de PDFs")
st.markdown("Arraste os nomes para definir a ordem. O primeiro da lista dará nome ao novo arquivo.")

uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    arquivos_dict = {f.name: f for f in uploaded_files}
    nomes_arquivos = list(arquivos_dict.keys())

    st.write("---")
    st.subheader("Defina a Ordem de União")
    ordem_final = sort_items(nomes_arquivos)

    st.write("---")
    
    if st.button("🚀 Unir Documentos", type="primary"):
        merger = PdfMerger()
        
        try:
            with st.spinner("Processando..."):
                for nome in ordem_final:
                    merger.append(arquivos_dict[nome])
                
                # Lógica do nome do arquivo:
                # Pegamos o primeiro nome da lista ordenada
                primeiro_nome = ordem_final[0]
                # Removemos a extensão .pdf (se houver) e adicionamos o sufixo
                nome_base = os.path.splitext(primeiro_nome)[0]
                nome_final = f"{nome_base}_unificado.pdf"
                
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                # Formatação de tamanho com padrão de vírgula
                tamanho_final = f"{len(output.getvalue()) / (1024 * 1024):.2f}".replace('.', ',')
                
                st.success(f"Concluído! Arquivo gerado: **{nome_final}** ({tamanho_final} MB)")
                
                st.download_button(
                    label="📥 Baixar PDF Unificado",
                    data=output.getvalue(),
                    file_name=nome_final, # Nome dinâmico aqui
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

else:
    st.info("Aguardando upload...")