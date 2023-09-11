import os
import azure.cognitiveservices.speech as speechsdk
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from get_voices import get_voices

SPEECH_KEY = 'YOUR_KEY'
SPEECH_REGION = 'YOUR_REGION'


class App:
    def __init__(self,SPEECH_KEY):
        self.root = tk.Tk()

        self.voice_df = get_voices(SPEECH_KEY)

        tk.Label(self.root, text="Region:").grid(row=0, column=0)
        self.region = tk.StringVar()
        self.region_OptionMenu = ttk.OptionMenu(self.root, self.region,None, *self.voice_df['region'].unique(),command=self.update_voice_name)
        self.region_OptionMenu.grid(row=0, column=1)

        tk.Label(self.root, text="Voice Name:").grid(row=1, column=0)
        self.voice_name = tk.StringVar()

        #voice_name_OptionMenu should be not selectable until region is selected
        self.voice_name_OptionMenu = ttk.OptionMenu(self.root, self.voice_name)
        self.voice_name_OptionMenu.configure(state='disabled')
        self.voice_name_OptionMenu.grid(row=1, column=1)



        tk.Label(self.root, text="Style Name:").grid(row=2, column=0)
        self.style_name = tk.StringVar()
        self.style_name_OptionMenu = ttk.OptionMenu(self.root, self.style_name)
        self.style_name_OptionMenu.configure(state='disabled')
        self.style_name_OptionMenu.grid(row=2, column=1)


        tk.Label(self.root, text="Rate:").grid(row=3, column=0)
        self.rate_entry = tk.Entry(self.root)
        self.rate_entry.insert(0, "+10.00%")
        self.rate_entry.grid(row=3, column=1)

        tk.Label(self.root, text="File:").grid(row=4, column=0)
        self.file_entry = tk.Entry(self.root)
        self.file_entry.grid(row=4, column=1)

        browse_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        browse_button.grid(row=5, column=2)

        save_button = tk.Button(self.root, text="Save", command=self.save_info)
        save_button.grid(row=5, column=1)

    def update_voice_name(self, event):
        voice_df = self.voice_df[self.voice_df['region']==self.region.get()]
        self.voice_name_OptionMenu.destroy()
        self.voice_name_OptionMenu = ttk.OptionMenu(self.root, self.voice_name,
                                                    voice_df['name'].iloc[0], *voice_df['name'].unique(), command=self.update_style_name)
        self.voice_name_OptionMenu.grid(row=1, column=1)
    
    def update_style_name(self, event):
        voice_df = self.voice_df[(self.voice_df['region']==self.region.get()) & (self.voice_df['name']==self.voice_name.get())]
        self.style_name_OptionMenu.destroy()
        self.style_name_OptionMenu = ttk.OptionMenu(self.root, self.style_name,
                                                    voice_df['style'].iloc[0], *voice_df['style'].unique())
        self.style_name_OptionMenu.grid(row=2, column=1)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(tk.END, filename)

    def save_info(self):
        self.input_dir, self.input_name = os.path.split(self.file_entry.get())
        
        #input_name should be a txt file
        if not self.input_name.endswith(".txt"):
            messagebox.showerror("Error", "Input file should be a txt file!")
            return

        self.region = self.region.get()
        
        self.voice_name = self.voice_name.get()

        self.rate = self.rate_entry.get()
        try:
            float(self.rate.rstrip('%'))
        except ValueError:
            messagebox.showerror("Error", "Rate should be a percentage!")
            return

        self.style_name = self.style_name.get()

        
        self.root.quit()

    def run(self):
        self.root.mainloop()

app = App(SPEECH_KEY)
app.run()

# Access the variables
print(f'input_dir: {app.input_dir}')
print(f'input_name: {app.input_name}')
print(f'region: {app.region}')
print(f'voice_name: {app.voice_name}')
print(f'rate: {app.rate}')
print(f'style_name: {app.style_name}')

input_dir = app.input_dir
input_name = os.path.splitext(app.input_name)[0]
region = app.region
voice_name = app.voice_name
rate = app.rate
style_name = app.style_name



now_time = time.time()
formate_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(now_time))

input_file = f'{input_name}.txt'
text = open(os.path.join(input_dir, input_file), 'r').read()

out_dir = input_dir
out_file =  os.path.join(out_dir,f'{region}_{voice_name}_{style_name}_{input_name}_{formate_time}.wav')


speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

audio_config = speechsdk.audio.AudioOutputConfig(filename = out_file)
ssml_string = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
    <voice name="{}">
        <prosody rate="{}">
        <mstts:express-as style="{}" styledegree="2">
        {}
        </mstts:express-as>
        </prosody>
    </voice>
</speak>
""".format(region+'-'+voice_name, rate, style_name, text)

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_string).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized to speaker for text [{}]".format(text))
    messagebox.showinfo("Success", "Speech synthesized to speaker for text [{}]".format(text))
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
    messagebox.showerror("Error", "Speech synthesis canceled: {}".format(cancellation_details.reason))
else:
    messagebox.showerror("Error", "Error")
