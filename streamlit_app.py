import streamlit as st
import io
from crewai import Agent, Task, Crew, Process, LLM

st.set_page_config(page_title="Экспертиза документов студенческих объединений", layout="wide")

# Проверка ключа
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("❌ Добавьте GOOGLE_API_KEY в Secrets Streamlit Cloud")
    st.stop()

# Модель Gemini
llm = LLM(
    model="gemini-1.5-flash",
    api_key=st.secrets["GOOGLE_API_KEY"],
    temperature=0.3
)

st.title("📄 Система экспертизы документов студенческих объединений")
st.markdown("---")

st.header("1. Настройка агентов")

col1, col2 = st.columns(2)

with col1:
    role1 = st.text_input("Role", "Эксперт по анализу документов")
    goal1 = st.text_area("Goal", "Проверить документы студенческих организаций и выявить ошибки.")
    backstory1 = st.text_area("Backstory", "Специалист по университетскому документообороту.")

with col2:
    role2 = st.text_input("Role 2", "Аналитик образовательных процессов")
    goal2 = st.text_area("Goal 2", "Подготовить аналитический отчет для администрации.")
    backstory2 = st.text_area("Backstory 2", "Эксперт по подготовке отчетов.")

st.markdown("---")

st.header("2. Загрузка CSV файла")

uploaded_file = st.file_uploader("Загрузите CSV файл", type=["csv"])

csv_data = ""

if uploaded_file:
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    csv_data = stringio.read()

csv_data = st.text_area("Данные CSV", value=csv_data, height=200)

st.markdown("---")

st.header("3. Выполнение анализа")

if st.button("🚀 Запустить экспертизу документов", type="primary"):

    if not csv_data.strip():
        st.error("Загрузите CSV файл")
    else:

        agent1 = Agent(
            role=role1,
            goal=goal1,
            backstory=backstory1,
            llm=llm
        )

        agent2 = Agent(
            role=role2,
            goal=goal2,
            backstory=backstory2,
            llm=llm
        )

        task1 = Task(
            description=f"""
Проанализируй CSV данные документов студенческих организаций.

Найди ошибки, проблемы и рекомендации.

Сделай таблицу:

Документ | Проблема | Рекомендация

ДАННЫЕ:
{csv_data}
""",
            agent=agent1,
            expected_output="Таблица анализа документов"
        )

        task2 = Task(
            description="""
Сделай аналитический отчет.

Включи:
1. Исполнительное резюме
2. Таблицу анализа
3. Основные проблемы
4. Рекомендации
""",
            agent=agent2,
            expected_output="Финальный отчет"
        )

        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=True
        )

        with st.status("🤖 Выполняется анализ...", expanded=True):
            result = crew.kickoff()

        st.subheader("📊 Результат анализа")
        st.markdown(result)

        st.download_button(
            "📥 Скачать отчет",
            data=str(result),
            file_name="document_analysis_report.md"
        )
