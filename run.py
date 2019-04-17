import nltk
import re
import requests
import json
import xlsxwriter
import emoji
from nltk.tag.stanford import StanfordTagger as POS_tag

#importing stanford part of speech tagger
_path_to_model='stanford-postagger/models/english-bidirectional-distsim.tagger'
_path_to_jar='stanford-postagger/stanford-postagger.jar'
st=POS_tag(_path_to_model,_path_to_jar)
#creating excel sheet to populate results

workbook=xlsxwriter.Workbook('dataset.xlsx')
worksheet=workbook.add_worksheet()
worksheet.write(0,0,'Original Message')
worksheet.write(0,1,'Has Emoticon?')
worksheet.write(0,2,'Contains URL?')
worksheet.write(0,3,"No. of characters")
worksheet.write(0,4,'No. of Uppercase Characters')
worksheet.write(0,5,'Upper Case Score')
worksheet.write(0,6,'Cleaned SMS')
worksheet.write(0,7,'No. of Characters in Cleaned SMS')
worksheet.write(0,8,'Cleaned Score')
worksheet.write(0,9,'Total Score')
worksheet.write(0,10,'Model Prediction')
worksheet.write(0,11,'Naive Bayes Prediction')
l=0
threshhold=0.4
with open('smsdata.txt','r') as f:
    for sms in f:
        l=l+1
        worksheet.write(l,0,sms.decode('utf-8'))
        has_emoji=False
        for c in sms:
            if c in emoji.UNICODE_EMOJI:
                has_emoji=True
                break
        worksheet.write(l,1,str(has_emoji))
        if has_emoji==True:
            worksheet.write(l,2,'N/A')
            worksheet.write(l,3,'N/A')
            worksheet.write(l,4,'N/A')
            worksheet.write(l,5,'N/A')
            worksheet.write(l, 6, 'N/A')
            worksheet.write(l, 7, 'N/A')
            worksheet.write(l, 8, 'N/A')
            worksheet.write(l, 9, 'N/A')
            worksheet.write(l,10,'HAM')
        else:
            spam_score=0
            has_url= bool(len(re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', sms)))
            print (re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]{2,3}\\s', sms)) #yahaan to kuchh print hui na hua
            if has_url==True:
                worksheet.write(l,2,'Yes')
                spam_score=spam_score+0.1
            else:
                worksheet.write(l,2,'No')
            length_sms=len(sms)-sms.count(' ')
            worksheet.write(l,3,length_sms)
            upper_chars=sum(1 for c in sms if c.isupper())
            worksheet.write(l,4,upper_chars)
            upper_case_score=(upper_chars/length_sms)*0.2
            worksheet.write(l,5,upper_case_score)
            spam_score=spam_score+upper_case_score
            arr = ' '.join(w for w in re.split(r'\W+', sms.lower()))
            ar = re.sub(r'\w*\d\w*', '', arr).strip()
            tag_sms = nltk.pos_tag(ar.split())
            edit_sms = [word for word, tag in tag_sms if tag != 'NNP' and tag != 'NNPS' and tag != 'NN' and tag != 'FW']
            cleaned = ' '.join(edit_sms)
            worksheet.write(l,6,cleaned.decode('utf-8'))
            cleaned_sms_len=len(cleaned)-cleaned.count(' ')
            cleaned_sms_score=(1-((length_sms-cleaned_sms_len)/float(length_sms)))*0.7
            worksheet.write(l,7,cleaned_sms_len)
            worksheet.write(l,8,cleaned_sms_score)
            spam_score=spam_score+cleaned_sms_score
            worksheet.write(l,9,spam_score)
            if spam_score>=threshhold:
                worksheet.write(l,10,'SPAM')
            else:
                worksheet.write(l,10,'HAM')
            payload = {"user": "sahil", "texts": [{"id": str(l), "textMessage": sms}]}
            r=requests.post('https://glacial-hamlet-87000.herokuapp.com/mobileapp/', json=payload)
            j = json.loads(r.text)
            worksheet.write(l,11,j['text']['cat'])
workbook.close()