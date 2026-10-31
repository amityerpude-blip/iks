"""IKS School Wellness & Action Research Tool
A school-based reflection and evaluation tool. It is not a diagnostic or treatment tool.
Run: streamlit run app.py
"""
from __future__ import annotations

import io
import json
import uuid
from datetime import date, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
ASSESSMENTS_FILE = DATA_DIR / "assessments.csv"
PRACTICE_FILE = DATA_DIR / "practice_log.csv"
SUPPORT_FILE = DATA_DIR / "individual_support_plans.csv"

st.set_page_config(
    page_title="IKS School Wellness Project",
    page_icon="🪷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Project content -----------------------------
LIKERT = {
    "Never": 1,
    "Rarely": 2,
    "Sometimes": 3,
    "Often": 4,
    "Almost always": 5,
}
FREQUENCY = list(LIKERT.keys())
CORE_ITEMS = {
    "stress": "I feel stressed by studies, schoolwork or expectations.",
    "calm": "I am able to remain calm when I face a difficult situation.",
    "concentration": "I can concentrate on my studies or the task in front of me.",
    "worry": "I worry so much that it affects my daily activities.",
    "sleep": "I follow a regular sleep and daily routine.",
    "confidence": "I feel confident about handling everyday challenges.",
    "sharing": "I can talk to a trusted person when something is troubling me.",
    "positivity": "I can notice positive things in my day.",
}
# Higher scores are not uniformly better. Reverse-score stress and worry for
# the overall positive-wellbeing index; display individual items transparently.
REVERSE_ITEMS = {"stress", "worry"}
PRACTICES = [
    "Yoga / gentle stretching (as appropriate)",
    "Pranayama / mindful breathing",
    "Meditation / Dhyana",
    "Svadhyaya / reflective reading or journaling",
    "Karma Yoga / mindful, sincere action",
    "Dinacharya / balanced daily routine",
    "Seva / helpfulness and service",
]
ISSUES = [
    "Academic pressure or examination stress",
    "Difficulty concentrating",
    "Worry or overthinking",
    "Sleep or daily-routine difficulties",
    "Low confidence",
    "Difficulty expressing feelings",
    "Peer or friendship concerns",
    "Family or personal responsibilities",
    "Managing anger or frustration",
    "Other / prefer not to say",
]

# Concern-led suggestions are educational options, not clinical prescriptions.
SUPPORT_GUIDE = {
    "Academic pressure or examination stress": {
        "focus": "Reduce study-related tension and make the next step manageable.",
        "practices": ["Pranayama / mindful breathing", "Svadhyaya / reflective reading or journaling", "Karma Yoga / mindful, sincere action"],
        "plan": "Begin with 2–3 minutes of comfortable natural breathing. Write one worry and one practical next step. Work on one small study task at a time.",
        "goal": "I can identify one manageable next step when study pressure rises.",
    },
    "Difficulty concentrating": {
        "focus": "Build a gentle routine for returning attention to one task.",
        "practices": ["Meditation / Dhyana", "Pranayama / mindful breathing", "Karma Yoga / mindful, sincere action"],
        "plan": "Try 2–3 minutes of quiet attention or natural breathing, followed by a short single-task study period and a brief break. Increase duration only if comfortable.",
        "goal": "I can return my attention to the task after a distraction.",
    },
    "Worry or overthinking": {
        "focus": "Notice recurring thoughts and practise a calm, supportive response.",
        "practices": ["Meditation / Dhyana", "Svadhyaya / reflective reading or journaling", "Pranayama / mindful breathing"],
        "plan": "Use a short guided quiet-attention activity. In a private journal, note what is within your control and one person you can talk to. Keep breathing natural; stop if uncomfortable.",
        "goal": "I can name one helpful response and one trusted person I can approach.",
    },
    "Sleep or daily-routine difficulties": {
        "focus": "Create a realistic and consistent daily rhythm.",
        "practices": ["Dinacharya / balanced daily routine", "Svadhyaya / reflective reading or journaling", "Meditation / Dhyana"],
        "plan": "Choose one realistic regular time for winding down. Make a simple evening routine with quiet reflection and reduced stimulating activity. Review it without self-blame.",
        "goal": "I can follow one small, realistic part of a balanced daily routine.",
    },
    "Low confidence": {
        "focus": "Recognise strengths and build confidence through small achievable actions.",
        "practices": ["Svadhyaya / reflective reading or journaling", "Karma Yoga / mindful, sincere action", "Seva / helpfulness and service"],
        "plan": "Record one effort or strength each day. Choose a small achievable task, complete it with care, and reflect on what helped. Service is optional and should never be forced.",
        "goal": "I can identify a strength and one small action I completed.",
    },
    "Difficulty expressing feelings": {
        "focus": "Find a safe, comfortable way to express a feeling and seek support.",
        "practices": ["Svadhyaya / reflective reading or journaling", "Meditation / Dhyana", "Seva / helpfulness and service"],
        "plan": "Use a private word, drawing or journal prompt to identify a feeling. Practise sharing only what feels comfortable with a trusted adult. Do not require public disclosure.",
        "goal": "I can identify at least one safe way to communicate when I need support.",
    },
    "Peer or friendship concerns": {
        "focus": "Support respectful interaction and help-seeking.",
        "practices": ["Svadhyaya / reflective reading or journaling", "Seva / helpfulness and service", "Meditation / Dhyana"],
        "plan": "Reflect privately on what happened, what is within your control and what support is needed. Optional cooperative service may help build positive connection. Speak to a trusted adult if the concern continues or involves bullying.",
        "goal": "I can identify a respectful next step or a trusted adult to approach.",
    },
    "Family or personal responsibilities": {
        "focus": "Make responsibilities manageable while protecting time for rest and support.",
        "practices": ["Dinacharya / balanced daily routine", "Karma Yoga / mindful, sincere action", "Svadhyaya / reflective reading or journaling"],
        "plan": "List tasks that are manageable, choose one priority and plan a realistic study/rest routine. Discuss workload with a trusted adult if responsibilities feel overwhelming.",
        "goal": "I can plan one manageable task while making time for rest or help.",
    },
    "Managing anger or frustration": {
        "focus": "Create a pause before responding and reflect on what may help.",
        "practices": ["Pranayama / mindful breathing", "Meditation / Dhyana", "Svadhyaya / reflective reading or journaling"],
        "plan": "When appropriate, pause and take a few comfortable natural breaths. Step away to a safe, calm space if possible, then reflect on the trigger and a respectful next response. Never use forced breathing or breath retention.",
        "goal": "I can practise one safe pause before responding when frustrated.",
    },
    "Other / prefer not to say": {
        "focus": "Choose a supportive activity based on the student's comfort and preference.",
        "practices": ["Meditation / Dhyana", "Svadhyaya / reflective reading or journaling", "Dinacharya / balanced daily routine"],
        "plan": "Discuss the concern privately with a trusted teacher or counsellor, if the student wishes. Select one low-pressure activity together and review whether it feels useful.",
        "goal": "I can identify one form of support that feels comfortable and appropriate.",
    },
}

def read_csv(path: Path) -> pd.DataFrame:
    if path.exists() and path.stat().st_size:
        try:
            return pd.read_csv(path, dtype={"student_code": str})
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
            return pd.DataFrame()
    return pd.DataFrame()


def append_record(path: Path, record: dict) -> None:
    frame = read_csv(path)
    frame = pd.concat([frame, pd.DataFrame([record])], ignore_index=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def save_assessment(record: dict) -> None:
    append_record(ASSESSMENTS_FILE, record)


def next_step_button(label: str, target_page: str, key: str) -> None:
    """Render a button that navigates to the next workflow page."""
    st.button(
        label,
        key=key,
        type="primary",
        use_container_width=True,
        on_click=lambda: st.session_state.update({"page_nav": target_page}),
    )


def header():
    st.title("🪷 IKS School Wellness & Action Research")
    st.caption("Indian Knowledge System practices for student wellbeing • School-based action research")
    st.info(
        "This tool supports reflection and educational action research. It does not diagnose "
        "mental-health conditions or replace support from qualified professionals."
    )


def student_fields(prefix: str):
    c1, c2, c3 = st.columns(3)
    with c1:
        code = st.text_input("Student code (do not enter full name)", key=f"{prefix}_code",
                             placeholder="e.g. XI-A-001")
    with c2:
        class_section = st.text_input("Class / section", key=f"{prefix}_class",
                                      placeholder="e.g. XI-A")
    with c3:
        age_band = st.selectbox("Age group (optional)", ["Prefer not to say", "13–14", "15–16", "17–18", "Above 18"],
                                key=f"{prefix}_age")
    return code.strip(), class_section.strip(), age_band


def render_pre_assessment():
    st.header("1. Pre-intervention assessment")
    st.write(
        "Purpose: understand students’ current experiences and the kinds of support they may find useful. "
        "There are no right or wrong answers."
    )
    st.caption("Use a student code rather than a name. Participation should be voluntary and handled according to school policy.")
    with st.form("pre_assessment_form"):
        code, class_section, age_band = student_fields("pre")
        st.subheader("A. Areas where support may be useful")
        selected_issues = st.multiselect(
            "Which of these, if any, have been challenging for you recently? (Select all that apply.)",
            ISSUES,
        )
        other_issue = st.text_input("If you selected ‘Other’, you may describe it briefly (optional).")
        st.subheader("B. How often do these statements describe you?")
        st.caption("1 = Never • 2 = Rarely • 3 = Sometimes • 4 = Often • 5 = Almost always")
        answers = {}
        for key, question in CORE_ITEMS.items():
            answers[key] = st.select_slider(
                question, options=FREQUENCY, value="Sometimes", key=f"pre_{key}"
            )
        coping = st.multiselect(
            "What do you currently do when you feel stressed or worried? (Optional)",
            ["Talk to a trusted person", "Take a break", "Play / exercise", "Listen to music",
             "Pray / meditate", "Breathing exercises", "Write / draw", "Other", "I am not sure"],
        )
        support = st.radio(
            "Would you like to learn simple practices for managing everyday stress?",
            ["Yes", "Maybe", "Not at present"], horizontal=True,
        )
        consent = st.checkbox(
            "I understand that this is a voluntary educational reflection activity and my responses "
            "will be used for the stated school project."
        )
        submitted = st.form_submit_button("Save pre-assessment", type="primary", use_container_width=True)
    if submitted:
        if not code or not class_section:
            st.error("Please enter a student code and class / section.")
        elif not consent:
            st.error("Please confirm the participation statement before saving.")
        else:
            record = {
                "record_id": str(uuid.uuid4()),
                "student_code": code,
                "class_section": class_section,
                "age_band": age_band,
                "assessment_type": "pre",
                "submitted_at": datetime.now().isoformat(timespec="seconds"),
                "selected_issues": "; ".join(selected_issues),
                "other_issue": other_issue.strip(),
                "coping_methods": "; ".join(coping),
                "interest_in_practices": support,
            }
            record.update({k: LIKERT[v] for k, v in answers.items()})
            save_assessment(record)
            st.success("Pre-assessment submitted successfully.")
            st.caption("Your responses are saved. Keep the same student code for the individual support plan and post-assessment.")
            next_step_button("Next: Create Individual IKS Support Plan", "Individual IKS support plan", "pre_to_plan")



def render_individual_plan():
    st.header("2. Individualised IKS support plan")
    st.write(
        "Create a student-led plan from the concern the student identifies. The suggestions below are "
        "starting points for discussion—not diagnoses or automatic prescriptions. A teacher/counsellor "
        "should review suitability with the student."
    )
    st.info("Use a pseudonymous student code. Do not enter names, diagnoses, trauma details or other sensitive disclosures.")
    with st.form("individual_plan_form"):
        code, class_section, age_band = student_fields("plan")
        concern = st.selectbox("Which concern would you like support with first?", ISSUES)
        frequency = st.selectbox(
            "How often has this concern been present recently?",
            ["Occasionally", "Some days", "Most days", "Prefer not to say"],
        )
        impact = st.selectbox(
            "How much does it affect your school day or daily routine?",
            ["A little", "Somewhat", "A lot", "Prefer not to say"],
        )
        preference = st.radio(
            "What kind of activity would you feel most comfortable trying?",
            ["Quiet reflection", "Gentle movement", "Breathing awareness", "Daily routine / planning", "Helping activity", "Not sure yet"],
            horizontal=False,
        )
        available_time = st.select_slider("Time you would prefer for one activity", options=["2–3 minutes", "5 minutes", "10 minutes", "Not sure"], value="5 minutes")
        student_choice = st.multiselect(
            "Would you like to include any of these practices? (Optional)",
            PRACTICES,
        )
        safety = st.checkbox(
            "I understand I can skip any activity, stop if uncomfortable, and speak privately with a trusted adult."
        )
        submitted = st.form_submit_button("Create my suggested support plan", type="primary", use_container_width=True)
    if submitted:
        if not code or not class_section:
            st.error("Please enter a student code and class / section.")
            return
        if not safety:
            st.error("Please confirm the choice-and-safety statement.")
            return
        guide = SUPPORT_GUIDE[concern]
        preferred = student_choice if student_choice else guide["practices"]
        plan = {
            "plan_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "student_code": code,
            "class_section": class_section,
            "age_band": age_band,
            "focus_concern": concern,
            "frequency": frequency,
            "impact": impact,
            "preferred_activity": preference,
            "available_time": available_time,
            "recommended_practices": "; ".join(guide["practices"]),
            "student_selected_practices": "; ".join(preferred),
            "suggested_plan": guide["plan"],
            "student_goal": guide["goal"],
            "review_status": "Pending teacher/counsellor review",
        }
        append_record(SUPPORT_FILE, plan)
        st.success("A suggested plan has been created. Please review it with a trusted teacher/counsellor before starting.")
        st.subheader("Your suggested support plan")
        st.markdown(f"**Focus:** {guide['focus']}")
        st.markdown(f"**Suggested practices:** {', '.join(guide['practices'])}")
        st.write(guide["plan"])
        st.markdown(f"**A small goal to review:** {guide['goal']}")
        st.markdown(f"**Student's preferred options:** {', '.join(preferred)}")
        st.caption(f"Suggested activity time: {available_time}. Start gently and adjust together.")
        st.warning(
            "This plan is not medical or psychological treatment. If the student feels unsafe, "
            "is in serious distress, or needs urgent help, stop this activity and follow school "
            "safeguarding procedures immediately with the designated qualified professional."
        )
        st.caption("The plan is saved for project monitoring. Do not use this shared/public app for identifiable or confidential student records.")
        next_step_button("Next: Record IKS Intervention Session", "IKS intervention & session log", "plan_to_session")

    st.divider()
    st.subheader("Saved plans and linked intervention progress")
    saved_plans = read_csv(SUPPORT_FILE)
    saved_logs = read_csv(PRACTICE_FILE)
    if saved_plans.empty:
        st.info("No individual support plans have been saved yet.")
    else:
        plan_labels = {
            f"{row.get('student_code', '')} | {row.get('focus_concern', '')} | {row.get('created_at', '')}": str(row.get("plan_id", ""))
            for _, row in saved_plans.iterrows()
        }
        selected_label = st.selectbox("Select a saved plan to review", list(plan_labels.keys()), key="review_plan_select")
        selected_id = plan_labels[selected_label]
        selected_rows = saved_plans[saved_plans["plan_id"].astype(str) == selected_id]
        if not selected_rows.empty:
            selected_plan = selected_rows.iloc[-1]
            st.markdown(f"**Student code:** {selected_plan.get('student_code', '')}  \n**Concern:** {selected_plan.get('focus_concern', '')}")
            st.markdown(f"**Suggested goal:** {selected_plan.get('student_goal', '')}")
            if not saved_logs.empty and "plan_id" in saved_logs.columns:
                linked = saved_logs[saved_logs["plan_id"].fillna("").astype(str) == selected_id]
            else:
                linked = pd.DataFrame()
            a, b = st.columns(2)
            a.metric("Linked sessions completed", len(linked))
            b.metric("Total practice minutes", int(pd.to_numeric(linked.get("duration_minutes", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()))
            if linked.empty:
                st.info("No session has been linked to this plan yet. Use the session-log link below to record the first activity.")
            else:
                display_columns = [column for column in ["date", "practice", "duration_minutes", "student_feedback", "reflection"] if column in linked.columns]
                st.dataframe(linked[display_columns].tail(20), use_container_width=True, hide_index=True)
            review_status = st.selectbox(
                "Plan review status",
                ["Pending teacher/counsellor review", "In progress", "Continue", "Adapt the plan", "Pause / stop", "Review completed"],
                index=["Pending teacher/counsellor review", "In progress", "Continue", "Adapt the plan", "Pause / stop", "Review completed"].index(str(selected_plan.get("review_status", "Pending teacher/counsellor review"))) if str(selected_plan.get("review_status", "Pending teacher/counsellor review")) in ["Pending teacher/counsellor review", "In progress", "Continue", "Adapt the plan", "Pause / stop", "Review completed"] else 0,
                key=f"review_status_{selected_id}",
            )
            if st.button("Update plan review status", key=f"save_review_{selected_id}"):
                saved_plans.loc[saved_plans["plan_id"].astype(str) == selected_id, "review_status"] = review_status
                saved_plans.to_csv(SUPPORT_FILE, index=False, encoding="utf-8-sig")
                st.success("Plan review status updated.")
    st.button(
        "Open IKS intervention & session log",
        type="primary",
        use_container_width=True,
        on_click=lambda: st.session_state.update({"page_nav": "IKS intervention & session log"}),
    )

    st.divider()
    st.subheader("How the plan should be reviewed")
    st.markdown(
        "1. Ask the student whether the suggested activity feels acceptable.\n"
        "2. Agree on one small practice and a realistic frequency.\n"
        "3. Check in after 1–2 weeks: helpful, not helpful, uncomfortable, or needs changing.\n"
        "4. Keep, adapt or stop the activity based on the student's feedback.\n"
        "5. Refer concerns beyond the scope of school wellbeing activities through the school's support system."
    )

def render_intervention():
    st.header("2. IKS intervention planner & practice log")
    st.write(
        "Use these practices as age-appropriate, inclusive wellbeing activities. Explain the activity, "
        "allow students to opt out, and never force breath retention, strenuous postures or personal disclosure."
    )
    descriptions = {
        PRACTICES[0]: "Gentle, comfortable movement with attention to posture and bodily awareness. Adapt for ability and safety.",
        PRACTICES[1]: "Simple natural breathing awareness. Avoid forceful breathing or breath-holding; stop if uncomfortable.",
        PRACTICES[2]: "A short, guided quiet-attention practice. Students may keep their eyes open or simply sit quietly.",
        PRACTICES[3]: "Reflective reading, journaling or self-observation focused on learning and constructive thoughts.",
        PRACTICES[4]: "Doing an everyday task with care, attention and a sense of responsibility.",
        PRACTICES[5]: "A balanced and realistic daily routine that includes sleep, study, recreation and rest.",
        PRACTICES[6]: "A voluntary act of kindness or contribution to the class or community, without pressure.",
    }
    for practice, description in descriptions.items():
        with st.expander(practice):
            st.write(description)
    st.subheader("Record a completed session")
    support_plans = read_csv(SUPPORT_FILE)
    plan_options = {"General session (not linked to an individual plan)": ""}
    plan_lookup = {}
    if not support_plans.empty and "plan_id" in support_plans.columns:
        for _, plan_row in support_plans.iterrows():
            plan_id_value = str(plan_row.get("plan_id", ""))
            plan_label = f"{plan_row.get('student_code', '')} | {plan_row.get('focus_concern', '')} | {plan_row.get('created_at', '')}"
            plan_options[plan_label] = plan_id_value
            plan_lookup[plan_id_value] = plan_row
    with st.form("practice_log_form"):
        selected_plan_label = st.selectbox("Link this session to an individual support plan (optional)", list(plan_options.keys()))
        selected_plan_id = plan_options[selected_plan_label]
        linked_plan = plan_lookup.get(selected_plan_id)
        if linked_plan is not None:
            st.caption(f"Linked student: {linked_plan.get('student_code', '')} • Concern: {linked_plan.get('focus_concern', '')}")
        c1, c2 = st.columns(2)
        with c1:
            session_date = st.date_input("Date", value=date.today())
            suggested_for_plan = []
            if linked_plan is not None:
                suggested_for_plan = [p.strip() for p in str(linked_plan.get("student_selected_practices", "")).split(";") if p.strip()]
            practice_choices = list(dict.fromkeys(suggested_for_plan + PRACTICES))
            practice = st.selectbox("Practice", practice_choices, index=0)
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=60, value=5)
        with c2:
            class_section = st.text_input("Class / section", placeholder="e.g. XI-A", key="log_class")
            facilitator = st.text_input("Facilitator (optional)")
            participation = st.selectbox("Participation", ["Whole class", "Small group", "Individual / self-practice"])
        student_feedback = st.selectbox("Student's response to the activity", ["Not discussed", "Helpful", "A little helpful", "Not helpful", "Uncomfortable", "Would like to try something different"])
        notes = st.text_area("Brief session reflection (avoid naming students or recording sensitive disclosures)", max_chars=500)
        log_submit = st.form_submit_button("Save session log", type="primary")
    if log_submit:
        if linked_plan is None and not class_section.strip():
            st.error("Please enter the class / section for a general session.")
        else:
            linked_student_code = str(linked_plan.get("student_code", "")) if linked_plan is not None else ""
            linked_class = str(linked_plan.get("class_section", "")) if linked_plan is not None else class_section.strip()
            append_record(PRACTICE_FILE, {
                "session_id": str(uuid.uuid4()),
                "plan_id": selected_plan_id,
                "student_code": linked_student_code,
                "focus_concern": str(linked_plan.get("focus_concern", "")) if linked_plan is not None else "",
                "date": session_date.isoformat(), "class_section": linked_class,
                "practice": practice, "duration_minutes": duration,
                "participation": participation, "facilitator": facilitator.strip(),
                "student_feedback": student_feedback,
                "reflection": notes.strip(),
            })
            st.success("Session log submitted successfully and linked to the selected support plan.")
            next_step_button("Next: Review Individual Support Plan", "Individual IKS support plan", "session_to_plan")
    logs = read_csv(PRACTICE_FILE)
    if not logs.empty:
        st.subheader("Recent sessions")
        st.dataframe(logs.tail(10), use_container_width=True, hide_index=True)
        if "plan_id" in logs.columns:
            linked_logs = logs[logs["plan_id"].fillna("").astype(str).str.strip() != ""]
            st.caption(f"{len(linked_logs)} session(s) are linked to individual support plans.")
    st.button(
        "Open Individual IKS support plan",
        use_container_width=True,
        on_click=lambda: st.session_state.update({"page_nav": "Individual IKS support plan"}),
    )


def render_post_assessment():
    st.header("3. Post-intervention assessment")
    st.write(
        "Complete after the planned intervention period (suggested: 4–6 weeks). "
        "Use the same student code entered in the pre-assessment."
    )
    with st.form("post_assessment_form"):
        code, class_section, age_band = student_fields("post")
        st.subheader("A. Current experience")
        st.caption("Use the same scale as the pre-assessment: 1 = Never to 5 = Almost always.")
        answers = {}
        for key, question in CORE_ITEMS.items():
            answers[key] = st.select_slider(
                question, options=FREQUENCY, value="Sometimes", key=f"post_{key}"
            )
        st.subheader("B. IKS practices")
        used = st.multiselect("Which practices did you try during the intervention?", PRACTICES)
        helpfulness = {}
        for index, practice in enumerate(PRACTICES):
            helpfulness[practice] = st.select_slider(
                f"How helpful was {practice.lower()} for you?",
                options=["Not tried", "Not helpful", "A little", "Moderately", "Very helpful"],
                value="Not tried", key=f"post_help_{index}"
            )
        most_useful = st.selectbox("Which practice was most useful to you?", ["Not sure"] + PRACTICES)
        change = st.selectbox(
            "Which area, if any, do you feel has improved the most?",
            ["Not sure / no noticeable change"] + ISSUES
        )
        reflection = st.text_area("What did you learn about looking after your wellbeing? (Optional)", max_chars=500)
        suggestion = st.text_area("What could be improved in these sessions? (Optional)", max_chars=500)
        usefulness = st.slider("Overall, how useful were the IKS activities?", 1, 5, 3,
                               help="1 = Not useful, 5 = Very useful")
        consent = st.checkbox("I understand that this is a voluntary educational reflection activity.")
        submitted = st.form_submit_button("Save post-assessment", type="primary", use_container_width=True)
    if submitted:
        if not code or not class_section:
            st.error("Please enter the student code and class / section.")
        elif not consent:
            st.error("Please confirm the participation statement before saving.")
        else:
            record = {
                "record_id": str(uuid.uuid4()), "student_code": code,
                "class_section": class_section, "age_band": age_band,
                "assessment_type": "post", "submitted_at": datetime.now().isoformat(timespec="seconds"),
                "practices_tried": "; ".join(used),
                "most_useful_practice": most_useful, "area_improved": change,
                "reflection": reflection.strip(), "suggestion": suggestion.strip(),
                "overall_usefulness": usefulness,
            }
            record.update({k: LIKERT[v] for k, v in answers.items()})
            for index, practice in enumerate(PRACTICES):
                record[f"helpfulness_{index}"] = helpfulness[practice]
            save_assessment(record)
            st.success("Post-assessment submitted successfully. Thank you for sharing your reflection.")
            next_step_button("Next: View Analysis & Export", "Analysis & export", "post_to_analysis")


def score_frame(frame: pd.DataFrame, assessment_type: str) -> pd.DataFrame:
    subset = frame[frame["assessment_type"] == assessment_type].copy()
    if subset.empty:
        return subset
    for key in CORE_ITEMS:
        if key in subset:
            subset[key] = pd.to_numeric(subset[key], errors="coerce")
    # Latest submission per student and assessment type is used in paired analysis.
    subset["submitted_at"] = pd.to_datetime(subset["submitted_at"], errors="coerce")
    return subset.sort_values("submitted_at").drop_duplicates("student_code", keep="last")


def render_analysis():
    st.header("4. Analysis & export")
    frame = read_csv(ASSESSMENTS_FILE)
    if frame.empty or "assessment_type" not in frame.columns:
        st.info("No assessment records yet. Complete pre- and post-assessments to see analysis.")
        return
    pre = score_frame(frame, "pre")
    post = score_frame(frame, "post")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pre-assessments", len(pre))
    c2.metric("Post-assessments", len(post))
    paired_codes = sorted(set(pre.get("student_code", [])) & set(post.get("student_code", [])))
    c3.metric("Matched students", len(paired_codes))
    st.caption("Analysis uses the latest pre and latest post submission for each student code. Use anonymous codes consistently.")
    if paired_codes:
        pre_pair = pre[pre["student_code"].isin(paired_codes)].set_index("student_code")
        post_pair = post[post["student_code"].isin(paired_codes)].set_index("student_code")
        rows = []
        for key, question in CORE_ITEMS.items():
            before = pd.to_numeric(pre_pair[key], errors="coerce").mean() if key in pre_pair else float("nan")
            after = pd.to_numeric(post_pair[key], errors="coerce").mean() if key in post_pair else float("nan")
            # A positive change is favourable for every displayed domain.
            if key in REVERSE_ITEMS:
                change_value = before - after
            else:
                change_value = after - before
            rows.append({"Domain": question, "Pre mean": before, "Post mean": after,
                         "Favourable-direction change": change_value})
        comparison = pd.DataFrame(rows)
        st.subheader("Matched pre/post comparison")
        st.dataframe(comparison.round(2), use_container_width=True, hide_index=True)
        st.caption(
            "For stress and worry, a decrease is favourable; for calmness, concentration, routine, "
            "confidence, sharing and positivity, an increase is favourable. These are descriptive "
            "self-reports, not clinical measures or proof of causation."
        )
        plot_data = comparison.set_index("Domain")[["Pre mean", "Post mean"]]
        fig, ax = plt.subplots(figsize=(10, 5))
        plot_data.plot(kind="bar", ax=ax)
        ax.set_ylim(0, 5)
        ax.set_ylabel("Mean response (1–5)")
        ax.set_title("Pre- and post-intervention self-reported responses")
        ax.tick_params(axis="x", labelrotation=35)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        csv = comparison.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download comparison (CSV)", csv, "iks_pre_post_comparison.csv", "text/csv")
    else:
        st.warning("No matching student codes found in both pre- and post-assessments yet.")
    with st.expander("View assessment records"):
        st.dataframe(frame, use_container_width=True, hide_index=True)
    st.download_button(
        "Download all assessment records (CSV)",
        frame.to_csv(index=False).encode("utf-8-sig"),
        "iks_assessments.csv", "text/csv",
    )
    logs = read_csv(PRACTICE_FILE)
    if not logs.empty:
        st.subheader("Intervention implementation summary")
        st.dataframe(logs, use_container_width=True, hide_index=True)
        st.download_button("Download practice log (CSV)",
                           logs.to_csv(index=False).encode("utf-8-sig"),
                           "iks_practice_log.csv", "text/csv")


def render_dashboard():
    st.header("Project overview")
    st.markdown(
        """
        This project explores how selected **Indian Knowledge System (IKS)** practices may support
        students’ everyday wellbeing, self-awareness and coping skills in a school setting.

        **Suggested action-research cycle**

        1. **Pre-assessment:** identify students’ reported challenges and existing coping methods.
        2. **Individualised support:** use the student’s selected concern, comfort and preferences to co-create a small IKS-based plan.
        3. **Intervention (4–6 weeks):** offer short, inclusive activities selected for the student rather than giving everyone the same practice.
        4. **Post-assessment:** repeat the core questions and ask which practices students found useful.
        5. **Reflection:** compare matched responses, review implementation notes and plan improvements.
        """
    )
    st.subheader("Start or continue the action-research cycle")
    start_cols = st.columns(3)
    with start_cols[0]:
        next_step_button("Take Pre-assessment", "Pre-assessment", "dashboard_pre")
    with start_cols[1]:
        next_step_button("Create Support Plan", "Individual IKS support plan", "dashboard_plan")
    with start_cols[2]:
        next_step_button("Open Session Log", "IKS intervention & session log", "dashboard_session")
    st.caption("Complete the post-assessment after the planned intervention period (suggested: 4–6 weeks).")
    next_step_button("Take Post-assessment", "Post-assessment", "dashboard_post")
    frame = read_csv(ASSESSMENTS_FILE)
    logs = read_csv(PRACTICE_FILE)
    pre_count = int((frame.get("assessment_type", pd.Series(dtype=str)) == "pre").sum()) if not frame.empty else 0
    post_count = int((frame.get("assessment_type", pd.Series(dtype=str)) == "post").sum()) if not frame.empty else 0
    a, b, c = st.columns(3)
    a.metric("Pre-assessments recorded", pre_count)
    b.metric("Post-assessments recorded", post_count)
    c.metric("IKS sessions logged", len(logs))
    st.subheader("Project principles")
    p1, p2, p3 = st.columns(3)
    p1.markdown("**Voluntary participation**\n\nStudents may skip a question or activity.")
    p2.markdown("**Respect & privacy**\n\nUse student codes; avoid collecting unnecessary personal details.")
    p3.markdown("**Non-clinical use**\n\nDo not interpret scores as diagnosis or treatment outcomes.")
    st.warning(
        "If a student expresses serious distress or a safety concern, follow the school’s child-protection "
        "and safeguarding procedures and refer to the designated qualified professional. Do not rely on this app."
    )


def main():
    header()
    page = st.sidebar.radio(
        "Navigate",
        ["Project overview", "Pre-assessment", "Individual IKS support plan",
         "IKS intervention & session log", "Post-assessment", "Analysis & export"],
        key="page_nav",
    )
    st.sidebar.divider()
    st.sidebar.caption("PM SHRI Kendriya Vidyalaya Dongargarh")
    st.sidebar.caption("IKS School Wellness Action Research")
    if page == "Project overview":
        render_dashboard()
    elif page == "Pre-assessment":
        render_pre_assessment()
    elif page == "Individual IKS support plan":
        render_individual_plan()
    elif page == "IKS intervention & session log":
        render_intervention()
    elif page == "Post-assessment":
        render_post_assessment()
    else:
        render_analysis()


if __name__ == "__main__":
    main()
