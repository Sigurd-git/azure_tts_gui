from math import e
import azure.cognitiveservices.speech as speechsdk
import requests
import pandas as pd





def get_voices(SPEECH_KEY,SPEECH_REGION = 'eastus'):
    headers = {
        "Ocp-Apim-Subscription-Key": SPEECH_KEY
    }
    url = f"https://{SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list"

    names, regions,styles = [], [], []
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json()
        for voice in voices:
            region = voice['Locale']
            name = voice['ShortName'].replace(region+'-', '')
        # second_locale = voice['SecondaryLocaleList']

            if 'StyleList' in voice.keys():
                for style in voice['StyleList']:
                    names.append(name)
                    regions.append(region)
                    styles.append(style)

            else:
                names.append(name)
                regions.append(region)
                styles.append(None)

        
    else:
        print(f"Failed to get voices: {response.status_code}")
    df = pd.DataFrame({'name':names, 'region':regions, 'style':styles})
    return df



