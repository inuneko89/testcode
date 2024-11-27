import streamlit as st
<<<<<<< HEAD
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv
import hashlib
from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account

service_account_file = "/workspaces/testcode/test-pipeline-company-af4bb08adc36.json"

if os.path.exists(service_account_file):
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_file
    print("Service Account Loaded")
else:
    print("ไม่พบไฟล์ Service Account")
## สร้าง BigQuery Client
bigquery_client = bigquery.Client(credentials=credentials, project="test-pipeline-company")

# สร้าง Google Cloud Storage Client
storage_client = storage.Client(credentials=credentials, project="test-pipeline-company")
# ตัวอย่างการใช้ Google Cloud Storage
bucket_name = "workwork_bucket"
bucket = storage_client.bucket(bucket_name)  # This is the correct method for Storage Client

# โหลด API Key และตั้งค่า
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
project_id = "test-pipeline-company"
bucket_name = "workwork_bucket"
dataset_id = "chatbot"  # Dataset ที่จะใช้งาน
client = bigquery.Client(credentials=credentials, project="test-pipeline-company")

genai.configure(api_key=GOOGLE_API_KEY)
# ฟังก์ชันโหลดข้อมูลจาก BigQuery
def load_hr_data_from_bigquery():
    try:
        if "hr_data" not in st.session_state:  # ตรวจสอบว่าโหลดข้อมูลแล้วหรือยัง
            tables = list(bigquery_client.list_tables(dataset_id))  # สร้างรายการของตารางทั้งหมด
            if not tables:
                st.warning(f"Dataset '{dataset_id}' ไม่มีตารางใดๆ")
                return
            
            st.session_state.hr_data = {}
            context_data = []
            for table in tables:
                table_name = table.table_id
                query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}`"
                df = bigquery_client.query(query).to_dataframe()
                st.session_state.hr_data[table_name] = df
                context_data.append(f"Table: {table_name}\n{df.to_string(index=False)}")

            st.session_state.context = "\n\n".join(context_data)  # สร้าง context สำหรับ Chatbot
            st.success("โหลดข้อมูล HR จาก BigQuery สำเร็จ!")
        else:
            st.success("ข้อมูล HR ถูกโหลดแล้วจากการใช้งานครั้งก่อน")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูลจาก BigQuery: {str(e)}")
  


def display_all_data():
    st.title("📊 ข้อมูลทั้งหมดจาก BigQuery")
    if "hr_data" not in st.session_state:
        load_hr_data_from_bigquery()
    if st.session_state.hr_data:
        for table_name, df in st.session_state.hr_data.items():
            st.dataframe(df)  # แสดงข้อมูลใน DataFrame

# ฟังก์ชันบันทึก Feedback ลง BigQuery
def save_feedback(feedback, sprint_id, feedback_type="general"):
    try:
        client = bigquery.Client(project=project_id)  # ใช้ project_id
        table_id = f"{project_id}.wh_work.feedback_tb"  # ใช้ project_id
        rows_to_insert = [{
            "Employee_ID": st.session_state.employee_id,
            "Sprint_ID": sprint_id,
            "Feedback": feedback,
            "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Feedback_Type": feedback_type
        }]
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            st.error(f"เกิดข้อผิดพลาดในการบันทึก Feedback: {errors}")
        else:
            st.success("Feedback ได้รับการบันทึกลง BigQuery เรียบร้อยแล้ว")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")


# ฟังก์ชันหน้าเข้าสู่ระบบ
def login_page():
    st.title("เข้าสู่ระบบ")
    employee_id = st.text_input("Employee ID")
    username = st.text_input("ชื่อผู้ใช้")
    password = st.text_input("รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"):
        user_database = {
            "101": {"username": "admin", "password": hashlib.sha256("password123".encode()).hexdigest(), "role": "HR"},
            "102": {"username": "user1", "password": hashlib.sha256("user123".encode()).hexdigest(), "role": "พนักงาน"}
        }
        if employee_id in user_database:
            user = user_database[employee_id]
            if username == user["username"] and hashlib.sha256(password.encode()).hexdigest() == user["password"]:
                st.session_state.logged_in = True
                st.session_state.employee_id = employee_id
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.rerun()
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            st.error("ไม่พบ Employee ID นี้ในระบบ")
# ฟังก์ชันบันทึก Feedback ลง BigQuery (ปรับให้ใช้ BigQuery)
def save_feedback_rating(feedback_scores):
    try:
        # เตรียมข้อมูลที่จะบันทึก
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        rows_to_insert = [{
            'Employee_ID': st.session_state.employee_id,
            'Feedback_Type': "Sprint Feedback",
            'Colleague_Rating': feedback_scores['colleague'],
            'Process_Rating': feedback_scores['process'],
            'Task_Rating': feedback_scores['task'],
            'WorkLifeBalance_Rating': feedback_scores['work_life_balance'],
            'Environment_Rating': feedback_scores['work_environment'],
            'Timestamp': timestamp
        }]
        
        # บันทึกข้อมูลลงใน BigQuery
        table_id = f"{project_id}.wh_work.feedback_rating_tb"  # ชื่อ Table ที่จะบันทึก
        errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)
        
        if errors:
            st.error(f"เกิดข้อผิดพลาดในการบันทึก Feedback: {errors}")
        else:
            st.success("Feedback ได้รับการบันทึกลง BigQuery เรียบร้อยแล้ว")
    
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึก Feedback: {str(e)}")

def show_all_data_for_hr():
    st.title("📊 ข้อมูลทั้งหมดจาก BigQuery")
    if "hr_data" not in st.session_state or not st.session_state.hr_data:
        st.warning("ยังไม่ได้โหลดข้อมูลจาก BigQuery")
        load_hr_data_from_bigquery()  # ลองโหลดข้อมูลอีกครั้ง
    if st.session_state.hr_data:
        for table_name, df in st.session_state.hr_data.items():
            st.subheader(f"🔍 ตาราง: {table_name}")
            st.dataframe(df)  # แสดงข้อมูลใน DataFrame
            st.write(f"จำนวนแถวทั้งหมด: {len(df)}")
    else:
        st.warning("ไม่มีข้อมูลแสดง")

def feedback_tab():
    st.header("กรุณาให้คะแนนและให้ Feedback สำหรับ sprint ที่ผ่านมา")
    
    # Sprint ID dropdown
    sprint_id = st.selectbox(
        "เลือก Sprint ID",
        options=["001", "002", "003", "004", "005"],
        key="sprint_id"
    )
    
    # Define feedback questions
    feedback_questions = {
        "colleague": "ใน sprint ที่ผ่านมา คุณมีความสุขกับเพื่อนร่วมงานแค่ไหน? (1 น้อย - 5 มาก)",
        "process": "ใน sprint ที่ผ่านมา คุณมีความสุขกับกระบวนการทำงานแค่ไหน? (1 น้อย - 5 มาก)",
        "task": "ใน sprint ที่ผ่านมา คุณมีความสุขกับงานที่ได้รับมอบหมายแค่ไหน? (1 น้อย - 5 มาก)",
        "work_life_balance": "ใน sprint ที่ผ่านมา คุณมีความสุขกับ work-life balance แค่ไหน? (1 น้อย - 5 มาก)",
        "work_environment": "ใน sprint ที่ผ่านมา คุณมีความสุขกับบรรยากาศในการทำงานแค่ไหน? (1 น้อย - 5 มาก)"
    }
    
    # Collect ratings
    feedback_scores = {}
    for key, question in feedback_questions.items():
        st.write(question)
        feedback_scores[key] = st.radio(
            label=f"เลือกคะแนนสำหรับ {key}",
            options=[1, 2, 3, 4, 5],
            horizontal=True,
            key=f"rating_{key}"
        )
    
    # Free text feedback
    feedback_comment = st.text_area("ความคิดเห็นเพิ่มเติม (ถ้ามี)")
    
    # Submit button
    if st.button("ส่ง Feedback"):
        save_feedback_rating(feedback_scores)  # Save rating-based feedback
        if feedback_comment:
            save_feedback(feedback_comment, sprint_id, feedback_type="comment")  # Save free-text feedback


def chatbot_response(prompt):
    try:
        # ตรวจสอบว่ามี context ข้อมูล HR หรือไม่
        if "context" not in st.session_state or not st.session_state.context:
            return "ไม่มีข้อมูล HR ในระบบ โปรดโหลดข้อมูลก่อน"

        context = st.session_state.context  # ใช้ข้อมูล HR จากระบบ
        
        # ปรับปรุงการสร้าง prompt โดยให้รายละเอียดมากขึ้น
        full_prompt = f"""
        คุณเป็น ผู้เชี่ยวชาญ ที่เชี่ยวชาญการวิเคราะห์ข้อมูลพนักงาน 
        โปรดตอบคำถามต่อไปนี้โดยอ้างอิงจากข้อมูลที่มีในระบบ HR:

        ข้อมูลที่มี:
        {context}

        คำถาม: {prompt}

        กรุณาตอบให้ละเอียดและชัดเจน โดยแสดงข้อมูลเชิงสถิติ แนวโน้ม หรือเหตุผลที่สนับสนุนคำตอบ
        หากคำถามมีหลายแง่มุม หรือสามารถตอบได้หลายแบบ โปรดระบุทุกกรณีที่เกี่ยวข้อง
        """

        # เชื่อมต่อกับโมเดลการประมวลผลที่เหมาะสม
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()

        # ปรับปรุงการบันทึกประวัติแชทให้ละเอียดมากขึ้น
        save_to_chat_history(prompt, response_text)

        return response_text
    
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"


def save_to_chat_history(prompt, response):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # สร้างประวัติเริ่มต้น
    # ลบการตรวจสอบคำถามซ้ำออกไป
    st.session_state.chat_history.append({"prompt": prompt, "response": response})


def display_chat_history():
    if "chat_history" in st.session_state and st.session_state.chat_history:
        # แสดงคำถามและคำตอบในลำดับจากล่างขึ้นบน (คำถามใหม่อยู่ล่างสุด)
        for entry in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(entry['prompt'])
            with st.chat_message("assistant"):
                st.write(entry['response'])






def main():
    # ตรวจสอบสถานะการเข้าสู่ระบบ
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # ตรวจสอบว่าได้โหลดข้อมูล HR หรือยัง
    if "hr_data" not in st.session_state:
        load_hr_data_from_bigquery()  # โหลดข้อมูล HR จาก BigQuery

    # ตรวจสอบว่า context สำหรับ chatbot ถูกโหลดหรือยัง
    if "context" not in st.session_state or not st.session_state.context:
        load_hr_data_from_bigquery()  # โหลด context ถ้ายังไม่มี

    # ถ้ายังไม่ได้เข้าสู่ระบบ ให้แสดงหน้าเข้าสู่ระบบ
    if not st.session_state.logged_in:
        login_page()
    else:
        st.title("📊 HR Analytics Dashboard")
        with st.sidebar:
            st.header(f"Welcome, {st.session_state.username}")
            st.write(f"บทบาทของคุณ: {st.session_state.role}")
            if st.button("ออกจากระบบ"):
                st.session_state.clear()
                st.success("คุณได้ออกจากระบบแล้ว")
                st.rerun()
            # เมนูให้เลือกการเข้าถึงข้อมูล
            if st.session_state.role == "HR":
                page = st.selectbox("เลือกหน้าจอ", ["หน้าหลัก", "ข้อมูลทั้งหมด"])
                if page == "ข้อมูลทั้งหมด":
                    show_all_data_for_hr()  # เรียกใช้งานฟังก์ชันแสดงข้อมูลทั้งหมด

        if st.session_state.role == "พนักงาน":
            feedback_tab()  # ใช้ Feedback Tab ที่ปรับปรุง

        elif st.session_state.role == "HR":
            # ถามคำถามเกี่ยวกับข้อมูล HR
            if prompt := st.chat_input("ถามคำถามเกี่ยวกับข้อมูล HR..."):
                response = chatbot_response(prompt)

            # แสดงประวัติการสนทนา
            display_chat_history()

if __name__ == "__main__":
    main()
