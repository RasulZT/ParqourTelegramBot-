import pandas as pd
from services.models import Parking  # или как у тебя

df = pd.read_excel("parkings.xlsx")  # или read_csv()

for _, row in df.iterrows():
    Parking.objects.create(
        name=row["name"],
        host=row["host"],
        ip=row["ip"],
        group_name=row.get("group_name"),
        group_chat_id=row.get("group_chat_id"),
        language_code=row.get("language_code", "ru")
    )
