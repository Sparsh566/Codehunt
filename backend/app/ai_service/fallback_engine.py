"""Offline deterministic fallback explanations and authoritative maritime references.

Guarantees 100% operational uptime if Groq or Tavily APIs are unreachable,
rate-limited, or executed without network connectivity.
"""

from typing import Dict, Any, List

FALLBACK_EXPLANATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "FISH-ARAB-001": {
        "opt_fish_shelter": {
            "en": "🌊 **Ocean Physics & Safety:** You respected the INCOIS Orange High Wave Alert (3.8m waves). Small artisanal and mechanized fishing craft (<15m) operating in seas higher than 2.5m experience extreme rolling and wave shoaling. Remaining in harbor preserved vessel integrity, crew lives, and fishing gear.\n\n🧭 **INCOIS Advisory Lesson:** INCOIS High Wave Alerts are calibrated from wave rider buoys and the WAVEWATCH III model. When wave heights exceed 3.5m, never compromise safety for PFZ catch gains.",
            "hi": "🌊 **समुद्री भौतिकी एवं सुरक्षा:** आपने INCOIS ऑरेंज हाई वेव अलर्ट (3.8 मीटर तरंग ऊंचाई) का सम्मान किया। 2.5 मीटर से ऊंची लहरों में छोटी मछली पकड़ने वाली नौकाएं पलटने के भारी खतरे में होती हैं। बंदरगाह में रहने से चालक दल और नौका सुरक्षित रही।\n\n🧭 **INCOIS सलाह सीख:** जब INCOIS 3.5 मीटर से अधिक की लहरों की चेतावनी जारी करे, तो कभी भी मछली पकड़ने के लालच में समुद्र में न जाएं।"
        },
        "opt_fish_venture": {
            "en": "🌊 **Hazard Analysis:** Venturing into 3.8m waves with a 14.2s swell period caused dangerous wave slamming and potential swamping. High swell waves carry immense kinetic energy that overpowers small vessel steering.\n\n🧭 **INCOIS Advisory Lesson:** INCOIS Orange Alerts signal dangerous sea states. Always check the SAMUDRA app before untying moorings.",
            "hi": "🌊 **खतरे का विश्लेषण:** 3.8 मीटर ऊंची लहरों में जाने से नौका के पलटने और टूटने का गंभीर खतरा पैदा हो गया।\n\n🧭 **INCOIS सलाह सीख:** ऑरेंज अलर्ट का अर्थ है समुद्र में न जाना। प्रस्थान से पहले हमेशा INCOIS समुद्री सलाह देखें।"
        },
        "opt_fish_shallow": {
            "en": "🌊 **Shoaling Wave Danger:** High swell waves (14.2s period) feel the ocean bottom in shallow coastal waters, causing them to rapidly steepen and break violently, destroying nets and beaching hulls.\n\n🧭 **INCOIS Advisory Lesson:** Shallow coastal waters are often MORE dangerous than deep sea during high swell events due to bathymetric wave transformation.",
            "hi": "🌊 **उथले पानी का खतरा:** 14 सेकंड की लंबी लहरें उथले तट के पास अचानक बहुत ऊंची और हिंसक हो जाती हैं, जिससे जाल फट जाते हैं और नाव टकरा जाती है।\n\n🧭 **INCOIS सलाह सीख:** उच्च तरंग चेतावनी के दौरान उथले तटीय पानी में कभी जाल न डालें।"
        }
    },
    "CAPT-BOB-003": {
        "opt_divert_south": {
            "en": "🌊 **Maritime Meteorology:** You altered course to the navigable semicircle away from the cyclone's dangerous forward-right quadrant. This minimized wind-wave superposition, keeping cargo secure and preventing parametric roll resonance.\n\n🧭 **INCOIS / IMD Advisory Lesson:** Deep-sea merchant vessels must maintain continuous radio watch on INCOIS Cyclone Bulletins and execute storm avoidance protocols well before gale-force winds strike.",
            "hi": "🌊 **समुद्री मौसम विज्ञान:** आपने चक्रवात के खतरनाक हिस्से से बचते हुए दक्षिण-पूर्व का सुरक्षित मार्ग चुना। इससे 5.4 मीटर ऊंची लहरों से कार्गो और जहाज को कोई नुकसान नहीं हुआ।\n\n🧭 **INCOIS / IMD सलाह सीख:** चक्रवात चेतावनी रेड अलर्ट होने पर तुरंत जहाज का मार्ग बदलें।"
        },
        "opt_push_ahead": {
            "en": "🌊 **Catastrophic Structural Loading:** Maintaining course into 52-knot winds caused heavy green water impact on the forecastle, cargo shifting, and risk of structural hull rupture.\n\n🧭 **INCOIS / IMD Advisory Lesson:** Never attempt to race across the eye or dangerous quadrant of a severe cyclonic storm.",
            "hi": "🌊 **विनाशकारी भूल:** 52 समुद्री मील की आंधी में आगे बढ़ने से जहाज पर भारी लहरें गिरीं और कंटेनर समुद्र में गिर गए।\n\n🧭 **INCOIS सलाह सीख:** कभी भी चक्रवात के केंद्र की ओर सीधा जहाज न ले जाएं।"
        }
    }
}

DEFAULT_FALLBACK: Dict[str, str] = {
    "en": "🌊 **Maritime Decision Review:** Your decision was evaluated deterministically according to INCOIS maritime safety thresholds and standard seamanship rules. Environmental parameters (wave height, wind velocity, swell period, and active hazard alerts) determine whether an action is safe or hazardous.\n\n🧭 **Official Advice:** Always monitor INCOIS Ocean State Forecasts (OSF) and coastal advisories at incois.gov.in.",
    "hi": "🌊 **समुद्री निर्णय समीक्षा:** आपके निर्णय का मूल्यांकन INCOIS समुद्री सुरक्षा मानकों और मौसम नियमों के आधार पर किया गया है। लहरों की ऊंचाई, हवा की गति और आपदा चेतावनियां यह तय करती हैं कि कार्य सुरक्षित है या खतरनाक।\n\n🧭 **आधिकारिक सलाह:** हमेशा incois.gov.in पर INCOIS समुद्री पूर्वानुमान और चेतावनियों का पालन करें।"
}

CURATED_AUTHORITATIVE_RESOURCES: Dict[str, List[Dict[str, str]]] = {
    "high_wave": [
        {
            "title": "INCOIS Ocean State Forecast & High Wave Warning System",
            "url": "https://incois.gov.in/portal/osf/osf.jsp",
            "snippet": "INCOIS provides round-the-clock Ocean State Forecast services including High Wave Alerts and Swell Surge forecasts along the entire Indian coastline.",
            "source": "incois.gov.in"
        },
        {
            "title": "Ministry of Earth Sciences — Marine Early Warning Services",
            "url": "https://moes.gov.in",
            "snippet": "MoES oversees national meteorological and oceanographic forecasting institutions protecting coastal communities and marine operations.",
            "source": "moes.gov.in"
        }
    ],
    "pfz": [
        {
            "title": "Potential Fishing Zone (PFZ) Advisory Services — INCOIS",
            "url": "https://incois.gov.in/MarineFisheries/pfz.jsp",
            "snippet": "PFZ advisories are generated by INCOIS using satellite measurements of Sea Surface Temperature (SST) and chlorophyll concentration to guide fishermen to rich pelagic fishing grounds.",
            "source": "incois.gov.in"
        },
        {
            "title": "UN Ocean Decade — Sustainable Ocean Economy & Fisheries",
            "url": "https://oceandecade.org/challenges/",
            "snippet": "UN Ocean Decade Challenge 3 and Challenge 4 emphasize sustainable marine food production and ecosystem stewardship.",
            "source": "oceandecade.org"
        }
    ],
    "cyclone": [
        {
            "title": "India Meteorological Department (IMD) — Cyclone Warnings",
            "url": "https://imd.gov.in",
            "snippet": "Official operational cyclone monitoring, storm surge warnings, and track forecast bulletins for the North Indian Ocean basin.",
            "source": "imd.gov.in"
        },
        {
            "title": "INCOIS Joint Storm Surge Warning Dissemination",
            "url": "https://incois.gov.in",
            "snippet": "Joint IMD-INCOIS storm surge prediction models compute inundation depths along vulnerable coastal stretches.",
            "source": "incois.gov.in"
        }
    ],
    "general": [
        {
            "title": "SAMUDRA Mobile App — Smart Access to Marine Users for Data Resources",
            "url": "https://incois.gov.in",
            "snippet": "All-in-one mobile app from INCOIS delivering real-time ocean advisories, PFZ charts, and high wave warnings directly to seafarers.",
            "source": "incois.gov.in"
        },
        {
            "title": "UNESCO-IOC / UN Ocean Decade Collaborative Centre at INCOIS",
            "url": "https://oceandecade.org",
            "snippet": "INCOIS acts as the regional collaborative centre for the Indian Ocean, spearheading Ocean Literacy and coastal resilience.",
            "source": "oceandecade.org"
        }
    ]
}

def get_fallback_explanation(scenario_code: str, chosen_option_id: str, language: str = "en") -> str:
    lang = language.lower() if language.lower() in ["en", "hi"] else "en"
    scenario_dict = FALLBACK_EXPLANATIONS.get(scenario_code, {})
    option_dict = scenario_dict.get(chosen_option_id, {})
    return option_dict.get(lang, DEFAULT_FALLBACK.get(lang, DEFAULT_FALLBACK["en"]))

def get_fallback_learn_more(topic: str = "general") -> List[Dict[str, str]]:
    t = topic.lower()
    for key in CURATED_AUTHORITATIVE_RESOURCES:
        if key in t:
            return CURATED_AUTHORITATIVE_RESOURCES[key]
    return CURATED_AUTHORITATIVE_RESOURCES["general"]
