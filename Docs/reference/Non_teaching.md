This document provides a structured breakdown of the **"25-26 Appraisal form for Non-Teaching (1).docx"** specifically organized by its internal sections. This format is designed to be easily parsed by a local development agent or used as a project specification document.

---

# Technical Specification: Non-Teaching Staff Appraisal System (2025-26)

## I. General Information Section
This section identifies the staff member and establishes the context for the assessment year.

*   **Field: Staff Name**[cite: 1]
*   **Field: Date of Joining**[cite: 1]
*   **Field: Current Designation**[cite: 1]
*   **Field: Department/Section**[cite: 1]
*   **Field: Experience at DYPIU**[cite: 1]
*   **Field: Total Work Experience**[cite: 1]
*   **Field: Current Qualifications**[cite: 1]
*   **Field: New Qualifications Acquired** (Acquired during the current year)[cite: 1]
*   **Field: Reporting Head**[cite: 1]
*   **Field: Other Information**[cite: 1]
*   **Field: Staff Signature/Date**[cite: 1]

---

## II. PART A: Self-Appraisal Details
**Maximum Points: 25**
This section is filled by the staff member first, then reviewed by authorities.

| Particular (Metric) | Max Score | Marks Claimed by Staff | Marks by Reporting Authority | Marks by Registrar |
| :--- | :--- | :--- | :--- | :--- |
| **Current Responsibilities** | 10 |[cite: 1] |[cite: 1] |[cite: 1] |
| **Other Useful Contributions** | 10 |[cite: 1] |[cite: 1] |[cite: 1] |
| **Achievements** | 5 |[cite: 1] |[cite: 1] |[cite: 1] |

---

## III. PART B: Assessment by Reporting Officer
**Maximum Points: 105** (across 4 sub-categories)
The assessment uses a 5-point scale: **5 (Excellent), 4 (Very Good), 3 (Good), 2 (Average), 1 (Below Average)**.[cite: 1]

### 1. Professional Competence (Max 25)
*   Knowledge of Rules, Regulations, and Procedures (5 pts)[cite: 1]
*   Ability to organize work and carry it out (5 pts)[cite: 1]
*   Ability and willingness to take up additional assignments (5 pts)[cite: 1]
*   Creativity and Innovation (5 pts)[cite: 1]
*   Ability to learn and perform new duties (5 pts)[cite: 1]

### 2. Quality of Work (Max 25)
*   Ability to Maintain Files & Office Records (5 pts)[cite: 1]
*   Accuracy & Speed of Work (5 pts)[cite: 1]
*   Neatness & Tidiness of Work (5 pts)[cite: 1]
*   Completion of work on time (5 pts)[cite: 1]
*   Diligence and Sense of Responsibility (5 pts)[cite: 1]

### 3. Personal Characteristics (Max 30)
*   Reliability (5 pts)[cite: 1]
*   Attitude & Respect (5 pts)[cite: 1]
*   Discipline (5 pts)[cite: 1]
*   Team Work Spirit (5 pts)[cite: 1]
*   Integrity and Behavior (5 pts)[cite: 1]
*   Interpersonal Relations (5 pts)[cite: 1]

### 4. Regularity (Max 25)
*   Attendance Consistency & Punctuality (5 pts)[cite: 1]
*   Leave Planning & Approval Discipline (5 pts)[cite: 1]
*   Communication & Intimation (5 pts)[cite: 1]
*   Adherence to Working Hours (5 pts)[cite: 1]
*   Responsibility During Absence (5 pts)[cite: 1]

---

## IV. Summary Section & Final Approvals
**Total Maximum Score: 130** (25 from Part A + 105 from Part B).[cite: 1]

### Summary Table
1.  **Self Appraisal Details** (Max 25)[cite: 1]
2.  **Professional Competence** (Max 25)[cite: 1]
3.  **Quality of Work** (Max 25)[cite: 1]
4.  **Personal Characteristics** (Max 30)[cite: 1]
5.  **Regularity** (Max 25)[cite: 1]

### Final Decisioning
*   **Reporting Officer:** Recommendation, Grade, and Signature.[cite: 1]
*   **Registrar:** Recommendation, Grade, and Signature.[cite: 1]
*   **Vice-Chancellor:** Final Approved Grade and Signature.[cite: 1]

---

## Technical Notes for Dev Agent:
*   **Validation:** Part A fields must not exceed their specific max scores (10, 10, or 5).[cite: 1]
*   **Calculated Fields:** `Total_Score` should be a computed value derived from summing Part A and all categories in Part B.[cite: 1]
*   **State Management:** The form has a workflow (Staff -> Reporting Officer -> Registrar -> VC). Use a `status` field to track this progression.[cite: 1]