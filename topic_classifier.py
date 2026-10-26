# ============================================
# دسته‌بند موضوع نظرات مشتریان - نسخه نهایی
# موضوعات: ارسال، قیمت، کیفیت، طراحی، پشتیبانی
# ============================================

import re
from typing import Dict, List

# ---------- نرمال‌سازی فارسی ----------
def normalize_persian(text: str) -> str:
    text = text.strip()
    replacements = {
        'ي': 'ی', 'ك': 'ک', 'ة': 'ه', 'ؤ': 'و',
        'إ': 'ا', 'أ': 'ا', 'ۀ': 'ه',
        '٠': '۰', '١': '۱', '٢': '۲', '٣': '۳', '٤': '۴',
        '٥': '۵', '٦': '۶', '٧': '۷', '٨': '۸', '٩': '۹',
    }
    for ar, fa in replacements.items():
        text = text.replace(ar, fa)

    # کاهش تکرار بیش از حد حروف (خیلیییی → خیلی)
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ---------- کلمات توقف ----------
STOPWORDS = {
    'و', 'در', 'به', 'از', 'که', 'این', 'آن', 'با', 'برای', 'را',
    'هم', 'من', 'تو', 'او', 'ما', 'شما', 'خیلی', 'بسیار', 'است',
    'بود', 'شد', 'یک', 'دو', 'سه', 'همه', 'هر', 'اگر', 'ولی', 'اما', 'یا'
}

# ---------- کلیدواژه‌ها (قابل گسترش) ----------
KEYWORDS = {
    "ارسال": [
        "ارسال", "پست", "پیک", "تحویل", "رسیدن", "دیر", "زود",
        "بسته", "بسته‌بندی", "آوردن", "رسید", "تاخیر", "سریع", "کند"
    ],
    "قیمت": [
        "قیمت", "گرون", "گران", "ارزون", "ارزان", "هزینه", "پول",
        "ارزش", "مناسب", "مقرون", "صرفه"
    ],
    "کیفیت": [
        "کیفیت", "جنس", "مقاوم", "خراب", "شکست", "دوام", "ضعیف",
        "عالی", "ساخت", "مواد", "مستحکم", "شکننده"
    ],
    "طراحی": [
        "طراحی", "ظاهر", "رنگ", "زیبا", "قشنگ", "شکل", "جذاب",
        "شیک", "فرم", "استایل", "زیبایی"
    ],
    "پشتیبانی": [
        "پشتیبانی", "پاسخ", "تماس", "پاسخگو", "خدمات", "جواب",
        "مشکل", "پاسخگویی", "خدمات‌پس‌از‌فروش"
    ],
}

NEGATION_WORDS = {"نه", "نمی", "نمی‌", "نیست", "نبود", "بدون", "فاقد", "ندارد", "اصلا"}


def preprocess(text: str) -> List[str]:
    text = normalize_persian(text)
    tokens = re.findall(r'[\u0600-\u06FF]+', text)
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return tokens


def predict_topics(text: str, threshold: float = 0.35) -> Dict:
    """
    خروجی نمونه:
    {
        "topics": ["ارسال", "کیفیت"],
        "primary": "ارسال",
        "scores": {"ارسال": 0.82, "کیفیت": 0.45, ...},
        "raw_counts": {...}
    }
    """
    tokens = preprocess(text)
    if not tokens:
        return {
            "topics": ["نامشخص"],
            "primary": "نامشخص",
            "scores": {},
            "raw_counts": {}
        }

    scores = {topic: 0.0 for topic in KEYWORDS}
    negation_flag = False

    for token in tokens:
        if token in NEGATION_WORDS:
            negation_flag = True
            continue

        for topic, words in KEYWORDS.items():
            for w in words:
                if w in token or token in w:
                    add = 1.0
                    if negation_flag:
                        add = -0.6
                    scores[topic] += add
                    break
        negation_flag = False

    max_score = max(scores.values()) if scores else 0
    if max_score <= 0:
        return {
            "topics": ["نامشخص"],
            "primary": "نامشخص",
            "scores": scores,
            "raw_counts": scores
        }

    normalized = {k: round(v / max_score, 3) for k, v in scores.items()}
    selected = [t for t, s in normalized.items() if s >= threshold]

    if not selected:
        selected = [max(normalized, key=normalized.get)]

    primary = max(normalized, key=normalized.get)

    return {
        "topics": selected,
        "primary": primary,
        "scores": normalized,
        "raw_counts": scores
    }


# ========== تست ==========
if __name__ == "__main__":
    tests = [
        "خیلی دیر به دستم رسید و بسته‌بندی خراب بود",
        "جنسش نسبت به قیمتش خوبه ولی ظاهرش خیلی قشنگه",
        "پشتیبانی جوابم رو نداد و مشکل حل نشد",
        "قیمتش خیلی گرونه و کیفیت پایینی داره",
        "ارسال سریع بود و طراحی محصول عالیه",
        "اصلاً راضی نیستم از کیفیت و پشتیبانی",
        "رنگ و ظاهرش جذاب بود ولی دیر رسید",
        "هیچ مشکلی نداشت همه چیز عالی بود",
    ]

    print("=" * 65)
    print("نتایج نسخه نهایی")
    print("=" * 65)

    for t in tests:
        result = predict_topics(t)
        print(f"\nنظر: {t}")
        print(f"→ موضوعات: {result['topics']}")
        print(f"→ موضوع اصلی: {result['primary']}")
        print(f"→ امتیازها: {result['scores']}")
        print("-" * 55)


