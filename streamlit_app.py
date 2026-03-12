import streamlit as st
import pandas as pd
import io
import os
from crewai import Agent, Task, Crew, Process, LLM

st.set_page_config(page_title="Экспертиза документов студенческих объединений", layout="wide")

# Проверка API ключа
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("❌ Добавьте GOOGLE_API_KEY в Secrets Streamlit Cloud")
    st.stop()

llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=st.secrets["GOOGLE_API_KEY"],
    temperature=0.3
)

st.title("📄 Система экспертизы документов студенческих объединений")
st.markdown("---")

# --- Агенты ---
st.header("1. Настройка агентов")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Агент-эксперт документов")
    doc_role = st.text_input("Role", "Эксперт по анализу документов")
    doc_goal = st.text_area(
        "Goal",
        "Проверить документы студенческих организаций и выявить ошибки."
    )
    doc_backstory = st.text_area(
        "Backstory",
        "Специалист по университетскому документообороту."
    )

with col2:
    st.subheader("Агент-аналитик отчётов")
    analyst_role = st.text_input("Role 2", "Аналитик образовательных процессов")
    analyst_goal = st.text_area(
        "Goal 2",
        "Сформировать итоговый аналитический отчёт."
    )
    analyst_backstory = st.text_area(
        "Backstory 2",
        "Эксперт по подготовке аналитических отчётов для администрации."
    )

st.markdown("---")

# --- Загрузка данных ---
st.header("2. Загрузка CSV файла")

uploaded_file = st.file_uploader("Загрузите CSV файл с документами", type=["csv"])

csv_text = ""

if uploaded_file:
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    csv_text = stringio.read()

csv_text = st.text_area(
    "Данные для анализа",
    value=csv_text,
    height=200
)

st.markdown("---")

# --- Анализ ---
st.header("3. Выполнение анализа")

if st.button("🚀 Запустить экспертизу документов", type="primary"):

    if not csv_text.strip():
        st.error("Загрузите CSV файл")
    else:

        doc_agent = Agent(
            role=doc_role,
            goal=doc_goal,
            backstory=doc_backstory,
            llm=llm
        )

        analyst_agent = Agent(
            role=analyst_role,
            goal=analyst_goal,
            backstory=analyst_backstory,
            llm=llm
        )

        task1 = Task(
            description=f"""
Проанализируй CSV данные документов студенческих организаций.

Найди:
- ошибки
- несоответствия
- рекомендации

Сделай таблицу:

Документ | Проблема | Рекомендация

ДАННЫЕ:
{csv_text}
""",
            agent=doc_agent,
            expected_output="Таблица анализа документов"
        )

        task2 = Task(
            description="""
Подготовь итоговый аналитический отчёт для администрации университета.
Включи:

1. Резюме
2. Основные проблемы
3. Таблицу анализа
4. Рекомендации
""",
            agent=analyst_agent,
            expected_output="Аналитический отчет"
        )

        crew = Crew(
            agents=[doc_agent, analyst_agent],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=True
        )

        with st.status("🤖 Выполняется анализ документов...", expanded=True):
            result = crew.kickoff()

        st.subheader("📊 Результат анализа")
        st.markdown(result)

        st.download_button(
            "📥 Скачать отчет",
            data=str(result),
            file_name="document_analysis_report.md"
        )
