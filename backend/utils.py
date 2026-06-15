"""
EduPath AI - Personal Reason Generator (utils.py)

Generates UNIQUE, personalized recommendation reasons for each student-major match.
Uses randomized sentence template pools to ensure varied, non-repetitive output.
"""

import random

# =============================================================================
# Helper Constants
# =============================================================================

SUBJECT_NAMES = {
    'math': 'Mathematics',
    'indonesian': 'Indonesian',
    'english': 'English',
    'biology': 'Biology',
    'physics': 'Physics',
    'chemistry': 'Chemistry',
    'economics': 'Economics',
    'sociology': 'Sociology'
}

RIASEC_FULL = {
    'R': 'Realistic',
    'I': 'Investigative',
    'A': 'Artistic',
    'S': 'Social',
    'E': 'Enterprising',
    'C': 'Conventional'
}

PRESTASI_LEVELS = {
    0: 'None',
    1: 'District',
    2: 'City/Province',
    3: 'Province',
    4: 'National',
    5: 'International'
}

# =============================================================================
# Sentence Template Pools
# =============================================================================

ACADEMIC_TEMPLATES = [
    "Your excellent {score} in {subject} aligns perfectly with {major}'s demand for strong {subject} skills.",
    "With a {score} in {subject}, you demonstrate the analytical ability that {major} students need.",
    "Your outstanding performance in {subject} ({score}) gives you a solid foundation for {major}.",
    "The {score} you scored in {subject} shows a natural aptitude that {major} values highly.",
    "Your {subject} grade of {score} places you well above the threshold needed to thrive in {major}.",
    "Scoring {score} in {subject} highlights a key strength that directly supports success in {major}.",
    "Your impressive {score} in {subject} reflects the kind of academic readiness {major} programs look for.",
    "A {score} in {subject} is a strong indicator of your potential to excel in {major} coursework.",
]

RIASEC_TEMPLATES = [
    "Your {type_full} personality type resonates with the typical profile of successful {major} graduates.",
    "As someone who scores high in {type_full}, you share key traits with professionals in {bidang}.",
    "The {riasec_code} pattern in your personality assessment maps closely to what {major} programs seek.",
    "Your dominant {type_full} trait suggests you'd feel right at home in the {major} learning environment.",
    "People with your {type_full} orientation tend to find genuine satisfaction and engagement in {bidang}.",
    "Your {riasec_code} personality profile is a strong match for the working style expected in {major}.",
    "The {type_full} dimension of your personality is a hallmark of students who flourish in {major}.",
    "With a pronounced {type_full} inclination, your natural working style fits well within {bidang}.",
]

ACHIEVEMENT_TEMPLATES = [
    "Your {level}-level achievement in {field} further demonstrates your dedication to this path.",
    "Having earned a {level} recognition in {field} adds meaningful weight to this recommendation.",
    "Your {level} accomplishment in {field} sets you apart and strengthens your candidacy for {major}.",
    "Achieving at the {level} level in {field} shows commitment that goes beyond the classroom.",
    "The {level} honor you received in {field} is a testament to your passion and capability.",
    "Your track record of {level}-level success in {field} reinforces your readiness for {major}.",
]

INTEREST_TEMPLATES = [
    "Your stated interest in {minat_field} reinforces this recommendation.",
    "The fact that you're drawn to {minat_field} aligns naturally with what {major} has to offer.",
    "Your curiosity about {minat_field} is a strong motivational factor for pursuing {major}.",
    "An active interest in {minat_field} tells us you'd engage deeply with {major}'s curriculum.",
    "Your enthusiasm for {minat_field} suggests you'll find the {major} journey both relevant and rewarding.",
    "Being passionate about {minat_field} is exactly the kind of intrinsic drive that helps students succeed in {major}.",
]

CLOSING_TEMPLATES = [
    "This combination of skills and interests positions you well for a fulfilling career in {bidang}.",
    "We believe {major} could be an excellent pathway to leverage your unique strengths.",
    "All things considered, {major} stands out as a promising match for your academic and personal profile.",
    "Your blend of abilities and inclinations makes {major} a compelling choice worth exploring.",
    "With your profile, pursuing {major} could unlock exciting opportunities in {bidang}.",
    "Given everything we've assessed, {major} is a recommendation we feel confident about for you.",
    "You have the right mix of talent and drive to make a real impact through {major}.",
    "We see strong potential for you to thrive and grow within the {major} program.",
]


# =============================================================================
# Main Generator Function
# =============================================================================

def generate_personal_alasan(jurusan_name, jurusan_bidang, jurusan_profile,
                              academic_scores, riasec_scores, riasec_top3,
                              prestasi, bidang_prestasi, minat, student_analysis):
    """
    Generate a UNIQUE, personal reason why this major suits the student.

    Args:
        jurusan_name: str - major name (e.g., 'Teknik Informatika')
        jurusan_bidang: str - major field (e.g., 'Sains dan Teknologi')
        jurusan_profile: dict - ideal profile of the major {'math': 5, 'R': 4, ...}
        academic_scores: dict - student's scores 0-100 {'math': 95, ...}
        riasec_scores: dict - student's RIASEC totals {'R': 15, 'I': 28, ...}
        riasec_top3: list - top 3 RIASEC types [('I', 28), ('C', 24), ('E', 22)]
        prestasi: int - achievement level 0-5
        bidang_prestasi: str - achievement field
        minat: list - interest areas
        student_analysis: dict - contains 'top_subjects', 'riasec_type'

    Returns:
        str - Personal reason paragraph (2-3 sentences)
    """
    components = []

    # -------------------------------------------------------------------------
    # Component 1 - Academic Strength
    # -------------------------------------------------------------------------
    best_subject = _find_best_matching_subject(jurusan_profile, academic_scores)
    if best_subject:
        subj_key, subj_score = best_subject
        template = random.choice(ACADEMIC_TEMPLATES)
        components.append(template.format(
            score=subj_score,
            subject=SUBJECT_NAMES.get(subj_key, subj_key),
            major=jurusan_name
        ))

    # -------------------------------------------------------------------------
    # Component 2 - RIASEC Personality Match
    # -------------------------------------------------------------------------
    if riasec_top3:
        top_type_code = riasec_top3[0][0]
        riasec_code = ''.join([t[0] for t in riasec_top3])
        template = random.choice(RIASEC_TEMPLATES)
        components.append(template.format(
            type_full=RIASEC_FULL.get(top_type_code, top_type_code),
            riasec_code=riasec_code,
            major=jurusan_name,
            bidang=jurusan_bidang
        ))

    # -------------------------------------------------------------------------
    # Component 3 - Achievement / Interest Bonus (optional)
    # -------------------------------------------------------------------------
    achievement_added = False
    if prestasi and prestasi > 0 and bidang_prestasi:
        level_name = PRESTASI_LEVELS.get(prestasi, str(prestasi))
        # Check if achievement field has some relevance to the major's field
        if _fields_related(bidang_prestasi, jurusan_bidang):
            template = random.choice(ACHIEVEMENT_TEMPLATES)
            components.append(template.format(
                level=level_name,
                field=bidang_prestasi,
                major=jurusan_name
            ))
            achievement_added = True

    if minat and not achievement_added:
        matching_interest = _find_matching_interest(minat, jurusan_bidang, jurusan_name)
        if matching_interest:
            template = random.choice(INTEREST_TEMPLATES)
            components.append(template.format(
                minat_field=matching_interest,
                major=jurusan_name
            ))

    # -------------------------------------------------------------------------
    # Component 4 - Closing Encouragement
    # -------------------------------------------------------------------------
    template = random.choice(CLOSING_TEMPLATES)
    components.append(template.format(
        major=jurusan_name,
        bidang=jurusan_bidang
    ))

    # Combine into a natural paragraph (2-3 sentences)
    # Keep at most 3 components to stay concise
    if len(components) > 3:
        # Always keep academic (first) and closing (last), pick one from middle
        middle = components[1:-1]
        chosen_middle = random.choice(middle)
        components = [components[0], chosen_middle, components[-1]]

    return ' '.join(components)


# =============================================================================
# Internal Helpers
# =============================================================================

def _find_best_matching_subject(jurusan_profile, academic_scores):
    """
    Find the student's strongest subject that also matters to the major.
    Returns (subject_key, score) or None.
    """
    academic_subjects = [k for k in jurusan_profile if k in SUBJECT_NAMES]

    if not academic_subjects:
        return None

    # Sort by major's requirement weight (descending), then student score (descending)
    candidates = []
    for subj in academic_subjects:
        major_weight = jurusan_profile.get(subj, 0)
        student_score = academic_scores.get(subj, 0)
        if student_score >= 70 and major_weight >= 3:
            candidates.append((subj, student_score, major_weight))

    if not candidates:
        # Fallback: just pick the student's best subject that appears in profile
        for subj in academic_subjects:
            student_score = academic_scores.get(subj, 0)
            if student_score >= 60:
                candidates.append((subj, student_score, jurusan_profile.get(subj, 0)))

    if not candidates:
        return None

    # Sort: highest (major_weight * student_score) first for best alignment
    candidates.sort(key=lambda x: x[2] * x[1], reverse=True)
    best = candidates[0]
    return (best[0], best[1])


def _fields_related(bidang_prestasi, jurusan_bidang):
    """Check if the achievement field is loosely related to the major's field."""
    if not bidang_prestasi or not jurusan_bidang:
        return False

    bp_lower = bidang_prestasi.lower()
    jb_lower = jurusan_bidang.lower()

    # Direct substring match
    if bp_lower in jb_lower or jb_lower in bp_lower:
        return True

    # Keyword-based loose matching
    related_keywords = {
        'science': ['science', 'math', 'physics', 'chemistry', 'biology', 'computer', 'informatics'],
        'technology': ['science', 'technology', 'computer', 'informatics', 'engineering'],
        'social': ['social', 'humanities', 'law', 'economics', 'business', 'sociology', 'psychology'],
        'economics': ['economics', 'business', 'management', 'accounting', 'finance'],
        'health': ['health', 'medicine', 'pharmacy', 'nursing', 'biology'],
        'arts': ['art', 'arts', 'design', 'creative', 'music', 'literature'],
        'education': ['education', 'teaching', 'teacher'],
    }

    for category, keywords in related_keywords.items():
        if any(kw in bp_lower for kw in keywords) and any(kw in jb_lower for kw in keywords):
            return True
        if category in bp_lower and category in jb_lower:
            return True

    return False


def _find_matching_interest(minat_list, jurusan_bidang, jurusan_name):
    """Find the first student interest that relates to the major."""
    if not minat_list:
        return None

    jb_lower = jurusan_bidang.lower()
    jn_lower = jurusan_name.lower()

    for interest in minat_list:
        interest_lower = interest.lower()
        # Check if interest keywords appear in major name or field
        interest_words = interest_lower.split()
        for word in interest_words:
            if len(word) > 3 and (word in jb_lower or word in jn_lower):
                return interest

    # If no direct match, return the first interest as a general reference
    if minat_list:
        return minat_list[0]

    return None
