import joblib
import os
import random
import requests
from datetime import date
from api.model.healthtip import HealthTip
from api.model.dailytip import DailyTip

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)

svm = joblib.load(os.path.join(base_dir, "svm_model.pkl"))
vectorizer = joblib.load(os.path.join(base_dir, "tfidf_vectorizer.pkl"))

def classify_question(question: str) -> str:
    vec = vectorizer.transform([question])
    prediction = svm.predict(vec)[0]
    return prediction

def fetch_daily_health_tip(force_refresh=True):
    today = date.today()

    if force_refresh:
        # Delete today's tips first
        DailyTip.objects.filter(date=today).delete()
        HealthTip.objects.filter(dailytip__date=today).delete()

    # If not forcing and already have 3 tips, skip
    if not force_refresh and DailyTip.objects.filter(date=today).count() >= 3:
        print("Daily tips already saved for today.")
        return

    tips_collected = []

    def save_tip(source, external_id, title, body):
        tip = HealthTip.objects.create(
            source=source,
            external_id=external_id,
            title=title,
            body=body
        )
        DailyTip.objects.create(tip=tip, date=today)
        tips_collected.append(tip)
        return tip

    while len(tips_collected) < 3:
        # 1️⃣ MyHealthfinder
        try:
            topics = requests.get(
                "https://odphp.health.gov/myhealthfinder/api/v4/itemlist.json?Type=topic",
                timeout=10
            ).json().get("Result", {}).get("Items", [])

            if topics:
                chosen = random.choice(topics)
                topic_id = chosen.get("TopicId") or chosen.get("Id")

                if topic_id:
                    detail = requests.get(
                        f"https://odphp.health.gov/myhealthfinder/api/v4/topicsearch.json?TopicId={topic_id}",
                        timeout=10
                    ).json().get("Result", {})

                    summary = detail.get("Summary", "")
                    if summary:
                        one_liner = summary.split(".")[0].strip() + "."
                        save_tip("myhealthfinder", str(topic_id), detail.get("Title", ""), one_liner)
                        continue
        except Exception as e:
            print(f"MyHealthfinder failed: {e}")

        # 2️⃣ CDC
        try:
            cdc = requests.get(
                "https://tools.cdc.gov/api/v2/resources/media?topicid=21&max=1",
                timeout=10
            ).json()

            results = cdc.get("results") or cdc.get("Results") or []
            if results:
                first = results[0]
                title = first.get("title") or "CDC Health Tip"
                description = first.get("description") or title
                one_liner = description.split(".")[0].strip() + "."
                save_tip("cdc", str(first.get("id")), title, one_liner)
                continue
        except Exception as e:
            print(f"CDC API failed: {e}")

        # 3️⃣ AdviceSlip fallback
        try:
            slip = requests.get("https://api.adviceslip.com/advice", timeout=5).json().get("slip", {})
            advice = slip.get("advice")
            if advice:
                save_tip("adviceslip", str(slip.get("slip_id")), "", advice)
                continue
        except Exception as e:
            print(f"AdviceSlip failed: {e}")

        if not tips_collected:
            break

    print(f"✅ Collected {len(tips_collected)} tips for {today}")
    return [tip.body for tip in tips_collected]