import json


supported_languages_map = {
    "eng": "English",
    "asm": "Assamese",
    "mni": "Manipuri",
    "nep": "Nepali",
    "san": "Sanskrit",
    "urd": "Urdu",
    "hin": "Hindi",
    "mai": "Maithili",
    "tam": "Tamil",
    "mal": "Malayalam",
    "ben": "Bengali",
    "kok": "Konkani",
    "guj": "Gujarati",
    "kan": "Kannada",
    "snd": "Sindhi",
    "ori": "Odia",
    "sat": "Santali",
    "pan": "Punjabi",
    "mar": "Marathi",
    "tel": "Telugu",
    "kas": "Kashmiri",
    "brx": "Bodo",
}


def get_de_master_col(de_id):
    result = {
        "de_name": "IP Address",
        "de_description": "A unique numerical label assigned to a device connected to the internet for identification and location tracking.",
        "de_original_name": "IP Address",
        "de_data_type": "string",
        "de_sensitivity": "low",
        "is_core_identifier": False,
        "de_retention_period": 30,
        "de_status": "draft",
        "translations": {
            "asm": "আইপি ঠিকনা",
            "ben": "আইপি ঠিকানা",
            "brx": "आइपि इयाड्रेस",
            "doi": "आई पी पता",
            "guj": "આઈપી સરનામું",
            "hin": "आईपी ​​पता",
            "kan": "ಐಪಿ ವಿಳಾಸ",
            "kas": "آئی پی پتہ",
            "kok": "आयपी ऍड्रेस",
            "mai": "आईपी पता",
            "mal": "IP വിലാസം",
            "mar": "आयपी ऍड्रेस",
            "mni": "আইপি এদ্রেছ",
            "nep": "आईपी ​​ठेगाना",
            "ori": "ଆଇପି ଠିକଣା",
            "pan": "ਆਈਪੀ ਐਡਰੈੱਸ",
            "san": "आइ पि address",
            "sat": "ᱟᱭᱤᱯᱤ ᱟᱭᱳᱜ",
            "snd": "آئی پی ايڊريس",
            "tam": "ஐபி முகவரி",
            "tel": "ఐపి చిరునామా",
            "urd": "آئی پی ایڈریس",
        },
        "collection_points": [],
        "purposes": [],
        "df_id": "string11",
        "created_by": "688b2a32ea184e982e2c27aa",
        "created_at": {"$date": "2025-08-11T09:47:35.035Z"},
        "updated_at": None,
        "updated_by": None,
    }
    return result


def get_purpose_col(purpose_id):
    result = {
        "_id": {"$oid": "6899ba62bb6576641b05377e"},
        "purpose_title": "To provide ongoing training in communication skills for customer service agents to enhance their interactions.",
        "purpose_description": "",
        "purpose_priority": "low",
        "review_frequency": "quarterly",
        "consent_time_period": 30,
        "reconsent": False,
        "data_elements": [],
        "translations": {
            "eng": "To provide ongoing training in communication skills for customer service agents to enhance their interactions.",
            "asm": "গ্রাহক সেৱা agent-সমূহৰ বাবে যোগাযোগ দক্ষতাৰ ওপৰত চলি থকা প্ৰশিক্ষণ প্ৰদান কৰা, তেওঁলোকৰ আলোচনা উন্নত কৰিবলৈ।",
            "ben": "গ্রাহক পরিষেবা এজেন্টদের সাথে তাদের মিথস্ক্রিয়া উন্নত করার জন্য যোগাযোগ দক্ষতার উপর চলমান প্রশিক্ষণ প্রদানের জন্য।",
            "brx": "गिजाब खालामग्राफोरनि थाखाय, खौरां फोरोंनायनि सोलोंथायखौ सोलोंनायजों लोगोसे, बेफोरनि खामानिखौ बांद्राय मोजां खालामनो थाखाय।",
            "doi": "ग्राहक सेवा एजैंटें दी संवाद कुशलतायें पर निरंतर प्रशिक्षण देणें तां जे ओआं दी गैल करदे हैं।",
            "guj": "ગ્રાહક સેવા એજન્ટોની ક્રિયાપ્રતિક્રિયાને વધારવા માટે સંચાર કૌશલ્યો પર સતત તાલીમ આપવી.",
            "hin": "ग्राहक सेवा एजेंटों के लिए उनकी बातचीत को बेहतर बनाने के लिए संचार कौशल में चल रहे प्रशिक्षण को प्रदान करना।",
            "kan": "ಗ್ರಾಹಕ ಸೇವಾ ಪ್ರತಿನಿಧಿಗಳ ಸಂವಹನ ಕೌಶಲಗಳನ್ನು ಹೆಚ್ಚಿಸಲು ಅವರಿಗೆ ನಿರಂತರ ತರಬೇತಿ ನೀಡಬೇಕು.",
            "kas": "گاہَکَن ہُنٛد سَروَس ایجنٹَن ہُنٛد باسان بہتر بناونہٕ خٲطرٕ، کَم کَشِیُلن پؠٹھ مُسلسل تَرَبِیَتھ دِیوُن۔",
            "kok": "ग्राहक सेवा एजंटांक तांच्या संवादांक सुदारपा खातीर संचार कौशल्यांचेर चालू प्रशिक्षण दिवप.",
            "mai": "ग्राहक सेवा एजेंट लोकनि केँ अपन बातचीत क' बेसी नीक बनाउल जाए एकरा लेल संचार कौशल पर चलि रहल प्रशिक्षण देबाक लेल।",
            "mal": "ഉപഭോക്തൃ സേവന ഏജന്റുമാരുമായുള്ള അവരുടെ ഇടപെഴകുകൾ മെച്ചപ്പെടുത്തുന്നതിന് ആശയവിനിമയ വൈദഗ്ദ്ധ്യത്തിൽ തുടർച്ചയായ പരിശീലനം നൽകുന്നതിന്.",
            "mni": "গ্রাহক সেবা এজেন্টশিংগী ইন্টারেকশনশিং হেনগৎহনবা য়াহন্নবা কম্যুনিকেশন স্কিলশিংদা চত্থরিবা ত্রৈনিং পীব।",
            "mar": "ग्राहक सेवा एजंट्ससाठी, त्यांच्या संवादांना अधिक सुधारण्यासाठी संवाद कौशल्यांचे सतत प्रशिक्षण देणे.",
            "nep": "ग्राहक सेवा एजेन्टहरूको अन्तरक्रियालाई बढाउन संचार कौशलमा निरन्तर तालिम प्रदान गर्नको लागि।",
            "ori": "গ্রାହକ ସେବା ଏଜେଣ୍ଟମାନଙ୍କର ପାରସ୍ପରିକ କ୍ରିୟାକୁ ବୃଦ୍ଧି କରିବା ପାଇଁ ଯୋଗାଯୋଗ ଦକ୍ଷତା ଉପରେ ଚାଲୁଥିବା ତାଲିମ ପ୍ରଦାନ କରିବା।",
            "pan": "ਗਾਹਕ ਸੇਵਾ ਏਜੰਟਾਂ ਲਈ ਉਹਨਾਂ ਦੀਆਂ ਗੱਲਬਾਤਾਂ ਨੂੰ ਵਧਾਉਣ ਲਈ ਸੰਚਾਰ ਹੁਨਰਾਂ 'ਤੇ ਚੱਲ ਰਹੀ ਸਿਖਲਾਈ ਪ੍ਰਦਾਨ ਕਰਨ ਲਈ।",
            "san": "ग्राहकसेवाकारिणां संवादानां वर्धनाय सम्भाषणकौशलेषु सततप्रशिक्षणं प्रदातुं।",
            "tam": "வாடிக்கையாளர் சேவை முகவர்களின் தொடர்புகளை மேம்படுத்த, தகவல் தொடர்பு திறன்களில் தொடர்ச்சியான பயிற்சி அளித்தல்.",
            "tel": "కస్టమర్ సేవా ఏజెంట్లకు వారి పరస్పర చర్యలను మెరుగుపరచడానికి కమ్యూనికేషన్ నైపుణ్యాలపై కొనసాగుతున్న శిక్షణను అందించడానికి.",
            "sat": "ᱜᱨᱟᱦᱚᱠ ᱥᱮᱵᱟ ᱮᱡᱮᱱᱴ ᱠᱚᱣᱟᱜ ᱠᱟᱛᱷᱟ ᱵᱟᱲᱦᱟᱣ ᱞᱟᱹᱜᱤᱫ ᱠᱟᱛᱷᱟ ᱨᱮᱱᱟᱜ ᱦᱩᱱᱟᱹᱨ ᱪᱮᱛᱟᱱ ᱨᱮ ᱞᱟᱜᱟᱛᱟᱨ ᱥᱮᱪᱮᱫ ᱮᱢᱚᱜ ᱞᱟᱹᱜᱤᱫ᱾",
            "snd": "گراهڪن جي خدمت ڪندڙ ايجنٽن لاءِ انھن جي رابطن کي وڌائڻ لاءِ رابطي جي صلاحيتن تي ھلندڙ تربيت ڏيڻ.",
            "urd": "کسٹمر سروس ایجنٹوں کے ساتھ بات چیت کو بہتر بنانے کے لیے مواصلاتی مہارتوں میں جاری تربیت فراہم کرنا۔",
        },
        "collection_points": [],
        "purpose_status": "draft",
        "df_id": "string11",
        "created_by": "688b2a32ea184e982e2c27aa",
        "created_at": {"$date": "2025-08-11T09:39:46.590Z"},
        "updated_at": None,
        "updated_by": None,
    }
    return result


def load_and_consolidate_data(static_json_file, de_id: str, purpose_id: str):
    """
    Loads static data from a JSON file and consolidates it with the mock data.
    """
    with open(static_json_file, "r", encoding="utf-8") as f:
        static_data = json.load(f)

    static_data_dict = {item["language"]: item for item in static_data}

    de_data = get_de_master_col(de_id)
    purpose_data = get_purpose_col(purpose_id)

    if not de_data or not purpose_data:
        return {}

    consolidated_data = {}

    for lang_code, lang_data in static_data_dict.items():
        lang_name = supported_languages_map.get(lang_code, lang_code)

        combined_data = lang_data.copy()
        combined_data["language"] = lang_name

        data_element_title = de_data["translations"].get(lang_code, de_data["de_name"])
        consent_description = purpose_data["translations"].get(lang_code, purpose_data["purpose_title"])

        combined_data["data_elements"] = [
            {
                "de_id": de_id,
                "title": data_element_title,
                "data_retention_period": de_data["de_retention_period"],
                "consents": [
                    {
                        "purpose_id": purpose_id,
                        "description": consent_description,
                        "consent_expiry_period": purpose_data["consent_time_period"],
                    },
                ],
            }
        ]

        consolidated_data[lang_code] = combined_data

    return consolidated_data


def generate_html(template_file, data_dict):
    """
    Generates the final HTML by replacing a placeholder with a JSON string.
    """

    with open(template_file, "r", encoding="utf-8") as f:
        html_template = f.read()

    json_string = json.dumps(data_dict, indent=4, ensure_ascii=False)
    df_name = "TRUST NAME"

    final_html = html_template.replace("// {{ NOTCIE_DATA }}", json_string)
    final_html = final_html.replace("{{ df_name }}", df_name)

    return final_html


if __name__ == "__main__":

    static_data_file = "notice_static.json"
    dynamic_data_module = "dynamic_data"
    html_template_file = "html_simple.html"
    output_html_file = "final_notice.html"

    consolidated_data = load_and_consolidate_data(
        static_data_file,
        de_id="6899bc37952ea40942638e14",
        purpose_id="6899ba62bb6576641b05377e",
    )

    rendered_html = generate_html(html_template_file, consolidated_data)

    with open(output_html_file, "w", encoding="utf-8") as f:
        f.write(rendered_html)
