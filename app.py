import streamlit as st
import pandas as pd
from PyPDF2 import PdfMerger
import io
import os

# Configuração da página
st.set_page_config(page_title="Unificador de PDFs", page_icon="⚖️", layout="centered")

st.title("📄 Unificador de PDFs")
st.markdown("""
1. Faça o **upload** de todos os arquivos PDFs.
2. Na tabela abaixo, **digite a numeração na coluna 'Ordem'** para definir a sequência final.
3. Clique em **Unir Documentos** para gerar o arquivo.
""")

# 1. Upload de múltiplos arquivos
uploaded_files = st.file_uploader(
    "Arraste os arquivos PDFs aqui", 
    type="pdf", 
    accept_multiple_files=True,
    help="Você pode selecionar vários arquivos de uma vez segurando Ctrl ou Shift."
)

if uploaded_files:
    # Criamos um DataFrame para mostrar na tabela, já sugerindo uma ordem sequencial
    arquivos_data = []
    for i, f in enumerate(uploaded_files):
        tamanho_mb = f"{f.size / (1024 * 1024):.2f}".replace('.', ',')
        arquivos_data.append({
            "Arquivo": f.name,
            "Tamanho (MB)": tamanho_mb,
            "Ordem": i + 1  # Sugere uma ordem inicial automática
        })
    
    df = pd.DataFrame(arquivos_data)

    st.write("---")
    st.subheader("Defina a Ordem de União")
    st.info("💡 Digite o número correspondente à posição desejada para cada arquivo:")

    # 2. Tabela Editável Nativa (Vertical e Azul por padrão)
    # O usuário pode alterar os números na coluna 'Ordem'
    # Esta tabela atende aos requisitos de layout vertical e sem cor vermelha forte
    edited_df = st.data_editor(
        df,
        column_config={
            "Ordem": st.column_config.NumberColumn(
                "Ordem",
                help="Defina a prioridade de união (1 é o primeiro)",
                min_value=1,
                step=1,
                width="small"
            ),
            "Arquivo": st.column_config.Column(width="large", disabled=True),
            "Tamanho (MB)": st.column_config.Column(width="small", disabled=True),
        },
        hide_index=True,
        use_container_width=True
    )

    st.write("---")

    # 3. Botão para processar a união
    if st.button("🚀 Unir Documentos agora", type="primary"):
        # Ordena o DataFrame com base no que o usuário digitou
        df_ordenado = edited_df.sort_values(by="Ordem")
        
        merger = PdfMerger()
        
        try:
            with st.spinner("Processando..."):
                # Busca o arquivo original pelo nome usando o DataFrame ordenado
                for nome_arquivo in df_ordenado["Arquivo"]:
                    arquivo_original = next(f for f in uploaded_files if f.name == nome_arquivo)
                    merger.append(arquivo_original)
                
                # Gera o arquivo em memória
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                # Lógica do nome do arquivo (nome do primeiro + _unificado)
                primeiro_nome = df_ordenado.iloc[0]["Arquivo"]
                nome_base = os.path.splitext(primeiro_nome)[0]
                nome_final = f"{nome_base}_unificado.pdf"
                
                # Formatação de tamanho com padrão brasileiro (vírgula)
                tamanho_final = f"{len(output.getvalue()) / (1024 * 1024):.2f}".replace('.', ',')
                
                st.success(f"Concluído! Arquivo gerado: **{nome_final}** ({tamanho_final} MB)")
                
                # Botão para download do arquivo final
                st.download_button(
                    label="📥 Baixar PDF Unificado",
                    data=output.getvalue(),
                    file_name=nome_final,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

else:
    st.info("Aguardando upload de arquivos para começar...")
