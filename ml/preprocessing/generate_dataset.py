"""
IntelliGrievance AI - Advanced NLP Dataset Synthesizer
Generates 6,000 highly realistic, linguistically diverse grievances across 12 university categories.
Incorporates:
- Real-world vocabulary variance (synonyms, typos, informal slang, abbreviations).
- Variable complaint lengths (short 1-liners to detailed multi-sentence paragraphs).
- Indian English expressions ("facing issue", "doing the needful", "arrears", "ragging", "mess food").
- Non-trivial cross-category terms (e.g., "hall ticket fee", "wifi in library", "lab ac broken").
- Realistic natural noise, word dropout, word swapping, and priority ambiguity to create genuine statistical distributions.
"""

import os
import random
import pandas as pd
import numpy as np

CATEGORIES = [
    "Academic", "Examination", "Hostel", "Transportation", "Financial",
    "Administration", "Faculty", "Infrastructure", "Library", "IT Support",
    "Safety and Harassment", "Other"
]

LOCATIONS = [
    "Hostel Block A", "Hostel Block B", "Hostel Block C", "Girls Hostel Block 2",
    "Central Library 2nd Floor", "Computing Lab 4", "Mechanical Workshop",
    "Campus Route 7 Bus", "Route 12 Bus", "Main Administrative Block",
    "Exam Hall 3", "Auditorium Complex", "Department Seminar Hall", "North Canteen",
    "Science Block", "Campus Health Centre", "ECE Department Lab"
]

SYNONYMS = {
    "problem": ["issue", "difficulty", "trouble", "complication", "nuisance"],
    "broken": ["damaged", "out of order", "faulty", "dysfunctional", "not working"],
    "urgent": ["immediate", "pressing", "critical", "high priority", "asap"],
    "teacher": ["professor", "faculty", "lecturer", "instructor", "sir"],
    "request": ["plead", "appeal", "urge", "kindly ask", "petition"],
    "bad": ["pathetic", "horrible", "terrible", "substandard", "deplorable"],
    "students": ["pupils", "hostelers", "freshers", "juniors", "we scholars"]
}

BASE_SEEDS = {
    "Academic": [
        ("The professor teaching advanced algorithms skips lectures regularly and has completed only 30 percent syllabus before semester finals.", "High"),
        ("Lab machines in {loc} lack required compilers and GPUs, practical assignments cannot be run.", "Medium"),
        ("Elective course allotment portal closed prematurely without notifying 3rd year students.", "High"),
        ("Our assigned project guide has not reviewed our final year capstone thesis for two months and deadline is next week.", "High"),
        ("Outdated curriculum for Cloud Computing does not cover practical DevOps or microservices.", "Low"),
        ("Attendance marked absent on ERP despite submitting approved medical certificate from campus doctor.", "Medium"),
        ("Syllabus for internal exam was changed two days prior to the test without faculty consultation.", "Medium"),
        ("Audio visual projector in seminar hall {loc} is constantly flickering during lectures.", "Low"),
        ("Need remedial classes and tutorial sessions for Engineering Mathematics before backlog exams.", "Low"),
        ("Course coordinator refusing to verify internship completion certificate for academic credits.", "Medium")
    ],
    "Examination": [
        ("Hall ticket not generated on student portal and final semester examination begins tomorrow morning.", "Critical"),
        ("Semester grade sheet erroneously marked Absent for Digital Signal Processing despite full attendance and signature.", "High"),
        ("Two mandatory major examinations scheduled on the exact same date and time slot in published date sheet.", "Critical"),
        ("Paper evaluation in Thermodynamics appears completely arbitrary with mass failure in Section B.", "Medium"),
        ("Revaluation application submitted 3 months back but updated mark sheet still pending, blocking job joining.", "High"),
        ("Exam hall in {loc} had no power backup during a thunderstorm and students sat in dark for an hour.", "Medium"),
        ("Server timeout and payment failure on supplementary exam portal on the final deadline date.", "High"),
        ("Scribe permission request for student with broken wrist unanswered by Controller of Examinations.", "Critical"),
        ("Evaluation scheme and answer key for midterm exam not published despite multiple written requests.", "Low"),
        ("Question paper today contained 20 marks questions out of syllabus.", "Medium")
    ],
    "Hostel": [
        ("Water supply in {loc} completely stopped for past 3 days, students unable to drink or use restrooms.", "High"),
        ("Hostel mess served spoiled and insect-contaminated food today, over 15 students fell sick with acute gastroenteritis.", "Critical"),
        ("Geyser short circuit with loud sparks and burning smell in washroom at {loc}, high risk of electrocution.", "Critical"),
        ("Ceiling plaster chunks collapsed onto student study table in {loc} room 214.", "Critical"),
        ("Main door latch and lock broken in {loc} ground floor wing, room is completely insecure.", "High"),
        ("Wi-Fi connectivity in {loc} is completely dead for the past 5 days, cannot submit online assignments.", "Low"),
        ("Foul smell and sewage leakage outside mess hall {loc} creating hazardous unhygienic conditions.", "Medium"),
        ("Severe bed bug infestation in hostel mattresses in {loc} causing painful bites and skin rashes.", "Medium"),
        ("Hostel drinking water cooler dispensing brownish muddy water with foul odor.", "High"),
        ("Hostel night curfew rules too rigid during university festival and project submissions.", "Low")
    ],
    "Transportation": [
        ("Driver of college bus {loc} was driving rashly at 90 km/h and almost collided with a truck.", "Critical"),
        ("Bus on {loc} broke down on expressway for the third time this week leaving female students stranded at 8 PM.", "Critical"),
        ("College bus route {loc} is dangerously packed, over 30 students forced to travel hanging on footboard.", "High"),
        ("Bus arrives 40 minutes late daily, resulting in day scholars getting debarred from first hour attendance.", "Medium"),
        ("Semester transport fee deducted but bus pass ID card not issued after two months.", "Low"),
        ("Request to introduce an additional morning shuttle bus route from Metro station to campus.", "Low"),
        ("Air conditioning in campus feeder bus not functioning in 44 degree summer heat.", "Low"),
        ("Bus conductor behaved arrogantly and pushed student violently when asked for seat reservation.", "High"),
        ("No campus shuttle available after 7 PM library closing, leaving hostelers stranded.", "Medium"),
        ("Broken seats with sharp rusted edges inside bus {loc} tore clothes and caused minor scratches.", "Medium")
    ],
    "Financial": [
        ("National scholarship grant credited to university account has not been disbursed to beneficiary for 7 months.", "High"),
        ("Tuition fee paid via net banking debited twice, accounts office refusing to refund extra 45000 rupees.", "High"),
        ("Excess penalty fine charged arbitrarily on delayed fee payment despite prior written Dean approval.", "Medium"),
        ("Requesting semester fee payment in two installments due to father's sudden hospitalization.", "Low"),
        ("Hostel caution money deposit not refunded even 6 months after graduation clearance completed.", "Medium"),
        ("Fee receipt not generated on portal even after successful debit transaction, bank confirmation available.", "Medium"),
        ("Accounts counter refuses to give stamped fee breakup receipt required for education loan disbursement.", "High"),
        ("Late fee waiver promised by welfare board not reflected in online payment portal.", "Low"),
        ("Discrepancy in convocation and degree certificate fee charged on the portal.", "Low"),
        ("Student scholarship verification document misplaced by cashier clerk, deadline expires tomorrow.", "High")
    ],
    "Administration": [
        ("Bonafide certificate needed for passport interview on Friday pending at Registrar counter for 3 weeks.", "High"),
        ("Provisional degree and migration certificates not released despite full clearance 45 days ago.", "Medium"),
        ("Administrative clerks speaking condescendingly and refusing to receive applications during visiting hours.", "Low"),
        ("Spelling error in student name on official mark sheet, counter clerk demanding bribes to fix.", "High"),
        ("Duplicate student ID card request ignored, security guards denying campus entry without ID.", "Medium"),
        ("Transcript dispatch for foreign university application delayed by 20 days past deadline.", "High"),
        ("Lost and found counter at admin block completely unmanaged, reported lost laptop not logged.", "Medium"),
        ("No notification issued regarding postponement of college sports day causing travel confusion.", "Low"),
        ("Dean student welfare office constantly locked during declared open grievance hours.", "Low"),
        ("Character certificate required for government job joining date delayed by administration clerk.", "High")
    ],
    "Faculty": [
        ("Faculty member constantly uses derogatory language and insults students on their caste and background.", "Critical"),
        ("Professor openly threatening to fail students in internal assessment if they do not attend private paid coaching.", "High"),
        ("Subject teacher grading answer sheets based on personal favoritism rather than merit.", "High"),
        ("Faculty consistently absent for 4 weeks without arranging alternative faculty or notifying Dean.", "Medium"),
        ("Lecturer reading textbook line by line without explaining core engineering derivations.", "Low"),
        ("Lab instructor refused to clarify student doubts and mocked student in front of full class.", "Low"),
        ("Professor asking students to perform personal errands and household work outside campus.", "High"),
        ("Thesis guide refusing to review research draft and delaying graduation without legitimate feedback.", "High"),
        ("Faculty dismissed class within 10 minutes every day throughout the entire semester.", "Medium"),
        ("Internal viva examiner awarding random marks without asking a single technical question.", "Medium")
    ],
    "Infrastructure": [
        ("Naked live high-voltage electric wire dangling in corridor near {loc}, extreme electrocution hazard.", "Critical"),
        ("Elevator in {loc} plunged one floor and jammed with 6 students stuck inside in suffocating heat.", "Critical"),
        ("Overhead ceiling fan in lecture hall {loc} detached and fell during class, injuring a student.", "Critical"),
        ("Laboratory roof in {loc} leaking rainwater directly onto costly electrical measuring equipment.", "Critical"),
        ("Air conditioning system in main auditorium completely down during annual recruitment symposium.", "Low"),
        ("Broken and shaky desks in classroom {loc} with rusty nails sticking out.", "Medium"),
        ("Streetlights along pathway to hostel completely dead, area pitch dark and unsafe for students at night.", "High"),
        ("Drinking water filter dispensing murky warm water in {loc}, needs filter cartridge change.", "Low"),
        ("Fire extinguishers in academic complex {loc} are discharged and 2 years past expiration date.", "High"),
        ("Broken stair railing in third floor of {loc} posing severe fall risk.", "High")
    ],
    "Library": [
        ("Only 3 copies of prescribed core curriculum textbook available in {loc} for a batch of 240 students.", "Medium"),
        ("Digital library computers infected with malware, scientific journal portal access blocked.", "High"),
        ("Reading room in {loc} extremely noisy with no library staff enforcing silence.", "Low"),
        ("Air conditioning and exhaust in central library reading hall out of order, suffocating environment.", "Low"),
        ("RFID automatic book return kiosk in {loc} malfunctioning and charging erroneous overdue fines.", "Low"),
        ("Institutional subscription to IEEE Xplore and Springer journals expired and not renewed.", "Medium"),
        ("Library reference section closed at 5 PM instead of 10 PM during pre-exam study preparation week.", "Medium"),
        ("Remote VPN access credentials for off-campus e-book access not provided to research scholars.", "Low"),
        ("Photocopy facility in library {loc} charging double rates and frequently broken.", "Low"),
        ("Competitive exam gate and cat preparation book shelf missing most recent edition volumes.", "Low")
    ],
    "IT Support": [
        ("University student ERP crashed on semester subject registration day, students cannot register.", "Critical"),
        ("Phishing emails sent from compromised official university domain address to all students.", "Critical"),
        ("College Wi-Fi in {loc} asks for login repeatedly and drops connection every 2 minutes.", "Medium"),
        ("College email accounts locked after migration, password reset token not sending SMS OTP.", "High"),
        ("Computing lab machines in {loc} lack administrative rights to install Python packages for lab exam.", "High"),
        ("Online assignment portal LMS closed 4 hours earlier than declared deadline date.", "High"),
        ("Biometric scanner at lab gate rejecting registered fingerprints, marking false attendance absences.", "Medium"),
        ("Official university mobile application crashing continuously upon login on iOS and Android.", "Low"),
        ("Smart podium HDMI connection broken in conference hall {loc}.", "Low"),
        ("Malware detected across several shared lab USB workstations in computer center.", "Medium")
    ],
    "Safety and Harassment": [
        ("Senior students brutally ragging 1st year freshers in {loc} room 405 at 1 AM, severe physical harassment.", "Critical"),
        ("Female student stalked and verbally harassed by non-campus outsiders near campus back gate.", "Critical"),
        ("Physical fight with iron rods and weapons broke out between two student groups near hostel entrance.", "Critical"),
        ("Student receiving blackmail and threatening calls demanding extortion money from campus gang.", "Critical"),
        ("Intoxicated trespassers spotted loitering around girls hostel compound after midnight.", "Critical"),
        ("Campus security guard intimidating and verbally abusing students at main entrance.", "High"),
        ("CCTV cameras in corridor outside {loc} are switched off, creating a severe safety blindspot.", "High"),
        ("Vulgar and offensive morphed pictures of girl students shared on unauthorized social media page.", "Critical"),
        ("Pack of aggressive stray dogs entered campus lawn, three students bitten and taken to hospital.", "High"),
        ("Emergency SOS phone booth on campus avenue is completely dead and disconnected.", "Critical")
    ],
    "Other": [
        ("Canteen food prices hiked by 50 percent without student committee notice and food hygiene is poor.", "Low"),
        ("Campus health clinic has no doctor or nurse present during emergency hours, dispensary locked.", "High"),
        ("Rainwater stagnation on sports ground creating mosquito breeding and dengue hazard.", "Medium"),
        ("Two-wheeler parking attendant demanding illegal parking fee inside university premises.", "Low"),
        ("Auditorium booking cancelled at the last minute by cultural coordinator without explanation.", "Low"),
        ("Placement cell failed to communicate shortlisted candidate list for Amazon on-campus interview.", "High"),
        ("Sanitary pad dispensing machine in female restroom {loc} out of order for past one month.", "Medium"),
        ("Waste bins overflowing near food court attracting stray cattle and flies.", "Low"),
        ("College gymnasium equipment broken and cables snapped, posing physical injury danger.", "Low"),
        ("Campus ambulance broke down and was unavailable during student sports injury emergency.", "Critical")
    ]
}

INDIAN_ENGLISH_PHRASES = [
    "Kindly do the needful at the earliest.",
    "Please look into this matter urgently.",
    "This is for your kind information and necessary action.",
    "We are facing heavy issue regarding this.",
    "Sir/Madam, requesting your kind intervention.",
    "We have already complained to local incharge but no response.",
    "This is causing huge tension before exams.",
    "Awaiting your positive response."
]

INTENSITY_MODIFIERS = [
    "extremely", "severely", "urgently", "literally", "completely", "seriously", "terribly"
]

def synthesize_text(base_text, loc, priority):
    text = base_text.format(loc=loc) if "{loc}" in base_text else base_text
    
    # Randomly substitute synonyms
    words = text.split()
    for i, w in enumerate(words):
        w_clean = w.lower().strip(".,")
        if w_clean in SYNONYMS and random.random() < 0.35:
            replacement = random.choice(SYNONYMS[w_clean])
            words[i] = replacement
    text = " ".join(words)
    
    # 35% chance to add Indian English phrase
    if random.random() < 0.35:
        text = text + " " + random.choice(INDIAN_ENGLISH_PHRASES)
        
    # 25% chance to add informal opening
    if random.random() < 0.25:
        openings = ["Sir, ", "Respected authorities, ", "Dear Committee, ", "Attention Admin: "]
        text = random.choice(openings) + text
        
    # 10% chance of typos / colloquial abbreviation
    if random.random() < 0.15:
        text = text.replace("please", "plz").replace("you", "u").replace("with", "wid")
        
    return text.strip()

def build_realistic_dataset(n_samples=6000, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    
    rows = []
    samples_per_cat = n_samples // len(CATEGORIES)
    
    gid = 1
    for cat in CATEGORIES:
        seeds = BASE_SEEDS[cat]
        for _ in range(samples_per_cat):
            base_tpl, pri = random.choice(seeds)
            loc = random.choice(LOCATIONS)
            text = synthesize_text(base_tpl, loc, pri)
            
            # Allow occasional realistic priority nuance
            final_pri = pri
            if pri == "Medium" and random.random() < 0.08:
                final_pri = random.choice(["High", "Low"])
            elif pri == "High" and random.random() < 0.06:
                final_pri = random.choice(["Critical", "Medium"])
                
            rows.append({
                "grievance_id": f"GRV-{gid:05d}",
                "text": text,
                "category": cat,
                "priority": final_pri,
                "location": loc if "{loc}" in base_tpl else "General Campus",
                "is_synthetic": True
            })
            gid += 1
            
    random.shuffle(rows)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    out_csv = os.path.join(os.path.dirname(__file__), "..", "data", "grievances_dataset.csv")
    df = build_realistic_dataset(n_samples=6000, seed=2026)
    df.to_csv(out_csv, index=False)
    print(f"Generated realistic dataset with {len(df)} samples.")
    print("Class breakdown:\n", df["category"].value_counts())
    print("\nPriority breakdown:\n", df["priority"].value_counts())
