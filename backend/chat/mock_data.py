"""CBP Training Knowledge Base - Mock training content for CBP personnel."""

CBP_TRAINING_CONTENT = [
    {
        'id': 1,
        'title': 'Primary Inspection Procedures - Port of Entry',
        'content': 'Primary inspection at a Port of Entry (POE) is the first point of contact between CBP officers and travelers. Officers must verify travel documents, determine admissibility, and assess potential risks. Key steps include: (1) Greeting the traveler professionally, (2) Requesting passport and any required visas, (3) Asking purpose of travel and duration of stay, (4) Querying relevant databases (TECS, ATS), (5) Examining documents for authenticity, (6) Making an admissibility determination. If concerns arise, refer to secondary inspection. Always maintain situational awareness and officer safety protocols.',
        'metadata': {
            'category': 'Inspection Procedures',
            'module': 'Primary Inspection',
            'difficulty': 'Foundational',
            'duration': '45 minutes',
        },
    },
    {
        'id': 2,
        'title': 'Secondary Inspection Referral Criteria',
        'content': 'Secondary inspection is conducted when primary inspection cannot resolve admissibility questions. Referral criteria include: document discrepancies or suspected fraud, database hits requiring verification, inconsistent statements, suspected criminal activity, agricultural or customs concerns, random selection for compliance review. During secondary, officers conduct more thorough interviews, baggage examination, and database queries. Document all findings on Form I-94 or appropriate records. Secondary inspection authority derives from 8 USC 1225 and 19 USC 1581.',
        'metadata': {
            'category': 'Inspection Procedures',
            'module': 'Secondary Inspection',
            'difficulty': 'Intermediate',
            'duration': '60 minutes',
        },
    },
    {
        'id': 3,
        'title': 'Immigration Document Verification',
        'content': 'CBP officers must verify numerous immigration documents including: U.S. Passports (check MRZ, photo, security features), Passport Cards (RFID chip verification), Visa stamps and foils (holographic features, proper endorsements), Green Cards (I-551, biometric verification), Employment Authorization Documents (I-766), Advance Parole documents. Key security features to examine: UV reactive elements, microprinting, optically variable devices, laser perforations. Use document verification equipment (UV lights, magnification) and reference guides. Report suspected fraudulent documents to the Document Fraud Unit.',
        'metadata': {
            'category': 'Document Verification',
            'module': 'Immigration Documents',
            'difficulty': 'Intermediate',
            'duration': '90 minutes',
        },
    },
    {
        'id': 4,
        'title': 'Customs Declaration and Duty Assessment',
        'content': 'All travelers entering the U.S. must complete CBP Declaration Form 6059B. Officers assess declarations for: prohibited items (certain foods, plants, wildlife products), restricted items requiring permits, duty-free exemptions ($800 for returning residents, $100 for non-residents), items requiring formal entry ($2,500+ value). Duty rates are determined by the Harmonized Tariff Schedule (HTS). Common dutiable items include alcohol (over exemption), tobacco, luxury goods, and commercial merchandise. Agricultural specialists handle food and plant inspections.',
        'metadata': {
            'category': 'Customs',
            'module': 'Declarations & Duties',
            'difficulty': 'Foundational',
            'duration': '45 minutes',
        },
    },
    {
        'id': 5,
        'title': 'Agricultural Inspection Requirements',
        'content': 'Agricultural inspection protects U.S. agriculture from foreign pests and diseases. Prohibited items include: most fresh fruits and vegetables, meats and meat products from most countries, plants and seeds without permits, soil. Regulated items requiring inspection: cut flowers, dried spices, wooden handicrafts. Officers should ask travelers about farm visits abroad (potential foot-and-mouth disease). Use the APHIS Traveler Inspection Manual for guidance. Detector dogs assist in identifying concealed agricultural products. Violations may result in civil penalties up to $50,000.',
        'metadata': {
            'category': 'Agriculture',
            'module': 'Agricultural Inspection',
            'difficulty': 'Intermediate',
            'duration': '60 minutes',
        },
    },
    {
        'id': 6,
        'title': 'Currency Reporting Requirements',
        'content': 'Travelers must report monetary instruments exceeding $10,000 to CBP using FinCEN Form 105. Monetary instruments include: currency (U.S. and foreign), travelers checks, money orders, negotiable instruments. Failure to report is a violation of 31 USC 5316 and may result in seizure and civil/criminal penalties. Officers should look for indicators of bulk cash smuggling: unusual packaging, conflicting statements about funds, nervous behavior. Coordinate with the Trade and Revenue Division for complex currency cases.',
        'metadata': {
            'category': 'Trade & Currency',
            'module': 'Currency Enforcement',
            'difficulty': 'Intermediate',
            'duration': '45 minutes',
        },
    },
    {
        'id': 7,
        'title': 'Visa Waiver Program (VWP) and ESTA',
        'content': 'The Visa Waiver Program allows citizens of 41 participating countries to travel to the U.S. for tourism or business for up to 90 days without a visa. Requirements: valid ESTA approval, machine-readable passport, no prior immigration violations, no visa refusals under INA 212. Officers verify ESTA status via CBP One or TECS. VWP travelers cannot extend stay or change status. Travelers with criminal history or prior overstays should be referred to secondary. The 90-day period includes any time spent in Canada, Mexico, or Caribbean islands.',
        'metadata': {
            'category': 'Immigration',
            'module': 'Visa Waiver Program',
            'difficulty': 'Foundational',
            'duration': '30 minutes',
        },
    },
    {
        'id': 8,
        'title': 'Trusted Traveler Programs Overview',
        'content': 'CBP administers several Trusted Traveler Programs to expedite processing of pre-approved, low-risk travelers: Global Entry (air travelers, includes TSA PreCheck), NEXUS (U.S.-Canada border), SENTRI (U.S.-Mexico border), FAST (commercial drivers). Benefits include dedicated lanes and kiosks. Officers should verify membership status, ensure biometric match, and confirm no new derogatory information. Membership can be revoked for violations including customs infractions, providing false information, or new criminal convictions. Direct enrollment questions to the Trusted Traveler Programs office.',
        'metadata': {
            'category': 'Trusted Traveler',
            'module': 'TTP Overview',
            'difficulty': 'Foundational',
            'duration': '45 minutes',
        },
    },
    {
        'id': 9,
        'title': 'Identifying Human Trafficking Indicators',
        'content': 'CBP officers play a critical role in identifying potential human trafficking victims. Key indicators include: traveler seems coached, scripted responses, third party controls documents, signs of physical abuse or malnourishment, inappropriate attire for travel, inconsistencies between stated purpose and circumstances, minor traveling with non-family member, fear or anxiety when separated from companion. If trafficking is suspected, separate the potential victim from the suspected trafficker, conduct interview with sensitivity, contact the CBP Human Trafficking hotline or ICE HSI. Victims may be eligible for T or U visa protections.',
        'metadata': {
            'category': 'Law Enforcement',
            'module': 'Human Trafficking',
            'difficulty': 'Advanced',
            'duration': '90 minutes',
        },
    },
    {
        'id': 10,
        'title': 'Use of Force Policy and De-escalation',
        'content': 'CBP Use of Force Policy authorizes force that is objectively reasonable based on the totality of circumstances. The force continuum includes: officer presence, verbal commands, empty-hand control, intermediate weapons, deadly force. De-escalation techniques should be employed when safe and feasible: create distance, use time and communication, request backup, provide clear instructions. All use of force incidents must be reported. Body-worn camera footage should be preserved. Officer safety is paramount - never sacrifice safety for de-escalation. Review the CBP Use of Force Handbook annually.',
        'metadata': {
            'category': 'Officer Safety',
            'module': 'Use of Force',
            'difficulty': 'Advanced',
            'duration': '120 minutes',
        },
    },
    {
        'id': 11,
        'title': 'TECS and Law Enforcement Database Queries',
        'content': 'TECS is the primary law enforcement database system used by CBP. Key databases and records include: NCIC (criminal records, warrants, stolen property), NLETS (motor vehicle records, driver licenses), IDENT/HART (biometric records), CLASS (visa records), ATS (targeting and risk assessment). Query all travelers through TECS during inspection. Positive hits require verification before any enforcement action. TECS access is audited - misuse results in disciplinary action. Sensitive information requires need-to-know basis. Report any suspected identity fraud or record anomalies to TECS Operations.',
        'metadata': {
            'category': 'Systems & Technology',
            'module': 'Law Enforcement Databases',
            'difficulty': 'Intermediate',
            'duration': '60 minutes',
        },
    },
    {
        'id': 12,
        'title': 'CBP Ethics and Professional Conduct',
        'content': 'All CBP personnel must adhere to the highest standards of ethics and professional conduct. Key principles: maintain integrity and honesty, treat all persons with dignity and respect, avoid conflicts of interest, protect sensitive information, report misconduct. Prohibited activities include: accepting gifts from travelers or importers, discrimination based on race or national origin, excessive force, falsifying records. Ethics violations are reported to the Office of Professional Responsibility (OPR). Whistleblower protections exist for good-faith reporting. Annual ethics training is mandatory for all CBP employees.',
        'metadata': {
            'category': 'Professional Standards',
            'module': 'Ethics & Conduct',
            'difficulty': 'Foundational',
            'duration': '60 minutes',
        },
    },
]
