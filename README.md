# IKS School Wellness & Action Research

A Streamlit application for a school-based action research project exploring how selected Indian Knowledge System (IKS) practices may support students' everyday wellbeing, self-awareness and coping skills.

**Institution:** PM SHRI Kendriya Vidyalaya Dongargarh

## Features

- Pre-intervention student reflection questionnaire.
- IKS intervention planner and session implementation log.
- Post-intervention questionnaire covering the same core wellbeing statements and practice helpfulness.
- Matched pre/post descriptive comparison using anonymous student codes.
- CSV export of assessment records, comparison and intervention logs.
- Local CSV storage; no external database or paid service required.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this repository.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

The app opens in your browser. Data files are created in the `data/` directory after the first submission.

## Suggested action-research cycle

1. **Pre-assessment:** identify reported challenges and current coping methods.
2. **Intervention:** conduct age-appropriate, inclusive sessions over approximately 4–6 weeks.
3. **Post-assessment:** use the same student code and repeat the core statements.
4. **Reflection:** review matched responses, practice logs and student suggestions.

The intervention library includes Yoga / gentle stretching, Pranayama / mindful breathing, Meditation / Dhyana, Svadhyaya, Karma Yoga, Dinacharya and Seva.

## Important safeguards

- This application is an educational reflection and action-research aid, **not a mental-health screening, diagnostic or treatment tool**.
- Participation must be voluntary and follow applicable school permissions, consent/assent and child-safeguarding procedures.
- Use a pseudonymous student code. Do not enter full names, phone numbers, addresses, diagnoses or unnecessary sensitive details.
- Students may skip questions or activities. Do not force postures, breath retention, personal disclosure or any practice that causes discomfort.
- If a student expresses serious distress or a safety concern, follow school safeguarding procedures and involve the designated qualified professional.
- Keep the repository public only for source code. **Do not commit student data, completed CSV files, or identifiable information.**
- The app stores data in local CSV files. On hosted services, local files may be temporary or shared with the host; use an institution-approved private deployment and storage process before collecting real student responses.

## Data files

- `data/assessments.csv` — pre/post questionnaire submissions.
- `data/practice_log.csv` — intervention session log.

Both files are excluded from Git by `.gitignore`.

## Analysis notes

The analysis uses the latest pre and latest post record for each student code. For stress and worry, a lower post score is treated as a favourable direction; for the other core statements, a higher score is treated as favourable. These are descriptive self-reports and should not be presented as clinical measures or proof that the intervention caused a change.
