from langchain_groq import ChatGroq
from react_graph import AgentGraph
# from dotenv import load_dotenv
from logzero import logger
import streamlit as st
import os
import uuid

# load_dotenv() 
# os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# give title to the page
st.title('Coffee Sales Chatbot')

# create sidebar to adjust parameters
st.sidebar.title('Model Parameters')
model_selected=st.sidebar.selectbox('Select LLM Model', ["meta-llama/llama-4-scout-17b-16e-instruct", "deepseek-r1-distill-llama-70b", "meta-llama/llama-4-maverick-17b-128e-instruct"])
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=0.1, value=0.01, step=0.01)
max_tokens = st.sidebar.slider('Max Tokens', min_value=1, max_value=1000, value=512)

# initialize session variables at the start once
if 'model' not in st.session_state:
    st.session_state['model'] = ChatGroq(
    model=model_selected,
    temperature=temperature,
    max_tokens=max_tokens,
    timeout=None,
    max_retries=2,
)

react_graph_object = AgentGraph(st.session_state['model'])
react_graph=react_graph_object.get_graph()
config = {"configurable": {"thread_id": f"{uuid.uuid4()}"}}

if 'messages' not in st.session_state:
    st.session_state['messages'] = []


# update the interface with the previous messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# create the chat interface
if prompt := st.chat_input("Enter your query"):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # get response from the model
    with st.chat_message('assistant'):
        # Proper message conversion
        response=react_graph.invoke({"messages": st.session_state['messages']}, config)
        temp_response=response.get("messages", [])
        temp_response=temp_response[-1].content
        st.write(temp_response)
        try:
            st.image("graph_images/test_image.jpg")
            os.remove("graph_images/test_image.jpg")
        except:
            pass
        if temp_response:
            st.session_state['messages'].append({"role": "assistant", "content": temp_response})
