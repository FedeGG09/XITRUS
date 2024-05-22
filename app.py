import streamlit as st
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import CTransformers
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
import streamlit.components.v1 as components
from templatesStreamlit import *
import tempfile
import os

# Funcion para leer los documentos
def load_documents(uploaded_files):
    docs = []
    temp_dir = tempfile.TemporaryDirectory()
    for file in uploaded_files:
        temp_filepath = os.path.join(temp_dir.name, file.name)
        with open(temp_filepath, "wb") as f:
            f.write(file.getvalue())
        loader = PyPDFLoader(temp_filepath)
        docs.extend(loader.load())

    # loader = DirectoryLoader('data/', glob="*.pdf", loader_cls=PyPDFLoader)
    # documents = loader.load()
    return docs

# Funcion para convertir el texto en chunks
def split_text_into_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunks = text_splitter.split_documents(documents)
    return text_chunks

def get_vectorstore(text_chunks):
    embbedings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': "cpu"})
    vector_store = FAISS.from_documents(text_chunks, embbedings)
    return vector_store

# def create_llms_model():
#     llm = CTransformers(model="mistral-7b-instruct-v0.1.Q4_K_M.gguf", config={'max_new_tokens': 512, 'temperature': 0.01})
#     return llm

def get_conversation_chain(vector_store):

    llm = CTransformers(model="mistral-7b-instruct-v0.1.Q4_K_M.gguf", config={'max_new_tokens': 128, 'temperature': 0.01})
    
    #Creamos la memoria
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Create chain (lANGCHAIN)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                                retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
                                                memory=memory)
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template2.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template2.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    url_logo = "https://github.com/FedeGG09/XITRUS/blob/main/xitrus_ai_logo.png.jpg?raw=true"
    st.set_page_config(page_title="LLM-RAG", page_icon=url_logo)
    st.write(css, unsafe_allow_html=True)


titulo = f"""
 <div class="btn-neon">
   <span class="icon"><img src=https://github.com/FedeGG09/XITRUS/blob/main/xitrus_ai_logo.png.jpg?raw=true></span>
    Welcome to XITRUS
    <span class="icon"><img src=https://github.com/FedeGG09/XITRUS/blob/main/xitrus_ai_cover.png.jpg?raw=true></span>
 </div>
"""
    st.markdown(titulo, unsafe_allow_html=True)

    presentacion = """
            <div class="skill">
                <div class="skill-content">
                    <div class="skill-detail">
                        <h2 class="skill-title">By Anonymous</h2>
                        <p>Welcome to XITRUS</p>
                        <div class="skill-progress">
                            <div class="progress progress-1"></div>
                        </div>
                    </div>
                </div>
            </div>
"""
    st.markdown(presentacion, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Hazle preguntas a tus documentos PDFs :books:")


    with st.sidebar:
        st.subheader("Tus Documentos")
        pdf_docs = st.file_uploader(
            "Sube tus PDFs aquí y pulsa 'Procesar PDF'", accept_multiple_files=True)
        if not pdf_docs:
            st.info("Sube tus pdfs para continuar.")
            st.stop()
            
        if st.button("Procesar PDF"):
            with st.spinner("Procesando"):
                # get pdf text
                documents = load_documents(pdf_docs)
                print(documents)
                text_chunks = split_text_into_chunks(documents)
                # create vector store
                vectorstore = get_vectorstore(text_chunks)
                # create conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore)
    
    user_question = st.text_input("Adelante pregunta")
    if user_question:
        with st.spinner("Procesando respuesta"):
            handle_userinput(user_question)




if __name__ == '__main__':
    main()
