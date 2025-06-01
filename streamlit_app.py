
import streamlit as st
import os
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="البحث في قاعدة بيانات الأحكام", layout="wide")

st.title("🔍 البحث في قاعدة بيانات الأحكام حسب الدائرة القضائية")

# مجلد قاعدة البيانات الثابتة
BASE_DIR = "qa3idat_ahkam"

# الحصول على أسماء الدوائر تلقائيًا من المجلد
if not os.path.exists(BASE_DIR):
    st.error(f"📁 المجلد '{BASE_DIR}' غير موجود. الرجاء إنشاؤه ووضع الأحكام بداخله.")
    st.stop()

circles = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])
selected_circles = st.multiselect("اختر دائرة أو أكثر", circles, default=circles)

query = st.text_input("🔎 أدخل وصف القضية أو الكلمات المفتاحية للبحث")

if query and selected_circles:
    docs = []
    filenames = []

    for circle in selected_circles:
        dir_path = os.path.join(BASE_DIR, circle)
        for filename in os.listdir(dir_path):
            if filename.endswith(".docx"):
                file_path = os.path.join(dir_path, filename)
                try:
                    text = docx2txt.process(file_path)
                    docs.append(text)
                    filenames.append(f"{circle} - {filename}")
                except:
                    continue

    if not docs:
        st.warning("لم يتم العثور على أي ملفات قابلة للقراءة في الدوائر المحددة.")
        st.stop()

    vectorizer = TfidfVectorizer().fit_transform([query] + docs)
    similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()

    results = sorted(zip(similarity, filenames, docs), reverse=True)
    filtered_results = [(score, name, doc) for score, name, doc in results if score > 0.1]

    st.markdown(f"### ✅ عدد النتائج المطابقة: {len(filtered_results)}")

    for score, name, doc in filtered_results:
        st.markdown(f"**📄 الملف:** `{name}`")
        st.markdown(f"**🎯 نسبة التطابق:** {round(score*100, 2)}%")
        st.markdown("---")
        st.markdown(doc[:1500] + ("..." if len(doc) > 1500 else ""), unsafe_allow_html=True)
        st.markdown("------")
