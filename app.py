import streamlit as st
import openai
import json

st.title("🍽️ Restaurant AI Assistant")
st.markdown("Upload your menu and ask questions about dietary needs, substitutions, and more!")

# 🔐 Secure API key input
openai_api_key = st.text_input("🔐 Enter your OpenAI API Key:", type="password")
if not openai_api_key:
    st.warning("Please enter your API key to continue.")
    st.stop()

# Step 1: Upload Menu
uploaded_file = st.file_uploader("📄 Upload your `menu.json`", type="json")

if uploaded_file:
    menu = json.load(uploaded_file)
    st.success("✅ Menu uploaded successfully!")

    # Step 2: Ask a Question
    user_question = st.text_input("👤 Ask a question about your menu:")

    if user_question:
        # Step 3: Build relevant prompt
        def find_relevant_dishes(question):
            relevant = []
            for item in menu:
                if item['dish_name'].lower() in question.lower():
                    relevant.append(item)
                elif any(word.lower() in question.lower() for word in item['dish_name'].lower().split()):
                    relevant.append(item)
            return relevant or menu  # fallback to full menu if nothing matched

        def build_prompt(dishes, question):
            prompt = (
                "You are a helpful restaurant assistant. Use the following menu to answer the customer question. "
                "Mention substitutions, allergens, cross-contamination risks, and policy details when relevant. "
                "End with: 'Would you like to know more about this?'\n\n"
            )
            for dish in dishes:
                prompt += f"Dish: {dish['dish_name']}\n"
                prompt += f"Description: {dish.get('description', 'No description.')}\n"
                prompt += f"Ingredients: {', '.join(dish.get('ingredients', [])).strip()}\n"
                prompt += f"Dietary Info: {json.dumps(dish.get('dietary_info', {}))}\n"
                prompt += f"Substitutions: {json.dumps(dish.get('substitutions', {}))}\n"
                prompt += f"Policies: {json.dumps(dish.get('policies', {}))}\n\n"
            prompt += f"Customer Question: {question}\nAnswer:"
            return prompt

        relevant_dishes = find_relevant_dishes(user_question)
        prompt = build_prompt(relevant_dishes, user_question)

        # Step 4: Query GPT
        with st.spinner("Thinking..."):
            try:
                client = openai.OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful restaurant assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                answer = response.choices[0].message.content
                st.markdown(f"### 🤖 AI Response:\n{answer}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
