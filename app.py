import os
import time
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from groq import Groq

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from htmlTemplates import css, bot_template, user_template


# ---------------- CONFIG ----------------

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ---------------- FILE READER ----------------

def get_documents_text(files):

    text = ""

    for file in files:

        filename = file.name.lower()

        try:

            if filename.endswith(".pdf"):

                pdf_reader = PdfReader(file)

                for page in pdf_reader.pages:

                    page_text = page.extract_text()

                    if page_text:

                        text += page_text + "\n"


            elif filename.endswith(".txt"):

                text += file.read().decode("utf-8")


            elif filename.endswith(".md"):

                text += file.read().decode("utf-8")


            elif filename.endswith(".docx"):

                doc = Document(file)

                for para in doc.paragraphs:

                    text += para.text + "\n"


            elif filename.endswith(".csv"):

                df = pd.read_csv(file)

                text += df.to_string(index=False)

        except Exception:

            continue

    return text


# ---------------- CHUNKING ----------------

def get_text_chunks(text):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=800,

        chunk_overlap=150,

        separators=[

            "\n\n",

            "\n",

            ". ",

            " ",

            ""

        ]

    )

    chunks = splitter.split_text(text)

    return chunks


# ---------------- VECTOR DB ----------------

def get_vectorstore(chunks):

    embeddings = HuggingFaceEmbeddings(

        model_name="BAAI/bge-base-en-v1.5"

    )

    vectorstore = Chroma.from_texts(

        texts=chunks,

        embedding=embeddings

    )

    return vectorstore

# ---------------- LLM ----------------

def answer_question(question):

    if st.session_state.vectorstore is None:

        return "⚠️ Please process documents first."
    

    retriever = st.session_state.vectorstore.as_retriever(

          search_type="mmr",

          search_kwargs={

             "k": 6,

             "fetch_k": 15

            }

           )

    docs = retriever.invoke(question)


    if len(docs) == 0:

        return "I couldn't find this information in the documents."

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
               You are an intelligent document assistant.

               Use ONLY the provided context.

               Rules:

               1. Answer accurately.
               2. If information is partially available, provide the partial answer.
               3. Combine information from multiple sections.
               4. If unavailable, say:

               "I couldn't find enough information in the documents."

                Context:{context}

                Question:{question}

                Answer:
           """
    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0

    )

    return response.choices[0].message.content


# ---------------- CHAT ----------------

def handle_userinput(question):

    placeholder = st.empty()

    for i in range(3):

        placeholder.info(

            "🤖 Thinking" + "." * (i+1)

        )

        time.sleep(0.2)

    answer = answer_question(

        question

    )

    placeholder.empty()

    st.session_state.chat_history.append(

        ("user", question)

    )

    st.session_state.chat_history.append(

        ("bot", answer)

    )


# ---------------- MAIN ----------------

def main():

    st.set_page_config(

        page_title="AskMyDocs",

        page_icon="📚",

        layout="wide"

    )

    st.markdown(

        css,

        unsafe_allow_html=True

    )

    if "vectorstore" not in st.session_state:

        st.session_state.vectorstore = None

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []


    st.title(

        "📚 AskMyDocs"

    )


    # ---------- SIDEBAR ----------

    with st.sidebar:

        st.header(

            "📂 Upload Documents"

        )

        uploaded_files = st.file_uploader(

            "Choose files",

            type=[

                "pdf",

                "txt",

                "docx",

                "md",

                "csv"

            ],

            accept_multiple_files=True

        )


        if st.button(

            "⚙️ Process Documents",

            use_container_width=True

        ):

            if not uploaded_files:

                st.warning(

                    "Upload files first."

                )

            else:

                with st.spinner(

                    "Processing..."

                ):

                    text = get_documents_text(

                        uploaded_files

                    )

                    chunks = get_text_chunks(

                        text

                    )

                    st.session_state.vectorstore = get_vectorstore(

                        chunks

                    )

                st.success(

                    "Done."

                )


        if st.button(

            "🗑️ Clear Chat",

            use_container_width=True

        ):

            st.session_state.chat_history=[]

            st.rerun()


        conversation = ""

        for role,msg in st.session_state.chat_history:

            conversation += (

                f"{role.upper()}:\n"

                f"{msg}\n\n"

            )


        st.download_button(

            label="⬇️ Download Chat",

            data=conversation,

            file_name="conversation.txt",

            mime="text/plain",

            use_container_width=True

        )


   

   # ---------- CHAT ----------

    with st.form(

       "chat_form",

       clear_on_submit=True

   ):

      question = st.text_input(
            label="Ask a question",
            placeholder="Ask anything...",
            label_visibility="collapsed"
                )

      send = st.form_submit_button(

          "🚀 Search",

          use_container_width=True

       )


    if send:

      if not question:

        st.warning(

            "Please enter a question."

        )

      elif st.session_state.vectorstore is None:

          st.warning(

            "Please upload and process documents first."

         )

      else:

          handle_userinput(

            question

          )

    for role, message in st.session_state.chat_history:

        if role == "user":

           st.write(
              user_template.replace(
                "{{MSG}}",
                message
               ),
               unsafe_allow_html=True
            )

        else:

           st.write(
               bot_template.replace(
                "{{MSG}}",
                message
               ),
               unsafe_allow_html=True
            )      


if __name__ == "__main__":

    main()