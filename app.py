import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
import arabic_reshaper
from bidi.algorithm import get_display
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
import re
from streamlit_lottie import st_lottie
import requests
from plotly.graph_objs import *
from wordcloud import WordCloud
from urlextract import URLExtract
from collections import Counter
import emojis
#------------------------configuration of page ----------------------------------
st.set_page_config(page_title='WhatsApp Analyzer',layout="wide",page_icon="📊")

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_message = load_lottieurl(
    "https://assets10.lottiefiles.com/packages/lf20_uDilo5.json"
)
with st.sidebar:
    st_lottie(lottie_message, height=140, width=None, key="message")
# =============================================================================================
# ======================================functions==============================================
def data_read(data):
    df = pd.read_fwf(data)
    df.drop('Unnamed: 3',axis=1,inplace=True)
    df.columns=["Date","Time","Msg"]
    new = df["Msg"].str.split(":",expand=True)
    df["Name"]= new[0] 
    df["Messages"]= new[1]
    df.drop(columns =["Msg"], inplace = True)
    df.Date=df.Date.apply(lambda x: x.strip("[") if isinstance(x, str) else x)
    df.Time=df.Time.apply(lambda x: x.strip("]") if isinstance(x, str) else x)
    return df
#---------------------------------
def relation_plot():
    User_Percent=round((data1['Name'].value_counts()/data1.shape[0])*100,2).reset_index().rename(columns={'index' : 'name', 'Name' : 'precent'})
    fig = px.pie(User_Percent, values='precent', names='name', title='Percentage of Messages per Senders',
             color_discrete_sequence=px.colors.sequential.Darkmint)
    fig.update_layout(paper_bgcolor = "#1a2330")
    return fig
#---------------------------------
def extractor_url():
    extractor = URLExtract()
    for i in data1.Messages:
        urls= extractor.find_urls(i)
        return len(urls)
#---------------------------------
def wordcloud():
    text = data1['Messages'].str.cat(sep=" ")
    text = arabic_reshaper.reshape(text)
    wc = WordCloud(width=2000, height=400, min_font_size=20, background_color='black')
    df_wc = wc.generate(text)
    fig, ax = plt.subplots( figsize=(20,10), facecolor='k' )
    ax.imshow(df_wc)
    plt.axis("off")
    return fig




#---------------------------------
def plot_emoji():
    emoji_msg = []
    for message in data1['Messages']:
        emoji_msg.extend(emojis.get(message))
    emojis_df = pd.DataFrame(Counter(emoji_msg).most_common(len(emoji_msg)), columns=['Emoji', 'Count']).head()

    fig_emojie = px.pie(emojis_df, values=emojis_df['Count'], names=emojis_df['Emoji'], title='Most used emojis',
             color_discrete_sequence=px.colors.sequential.Aggrnyl)
    fig_emojie.update_layout(paper_bgcolor = "#1a2330")
    return fig_emojie
    
# -------------------------------------------------
def clear_multi():
    st.session_state.multiselect = []
    return

# ---------------------------------------------------
def day_wise_count():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_df = pd.DataFrame(data1["Messages"])
    day_df['day_of_date'] = data1['Date'].dt.weekday
    day_df['day_of_date'] = day_df["day_of_date"].apply(lambda d: days[d])
    day_df["messagecount"] = 1

    day = day_df.groupby("day_of_date")["messagecount"].sum()
    day=pd.DataFrame(day)


    fig = px.line_polar(day, r=day['messagecount'], theta=day.index,line_close=True)
    fig.update_traces(fill='toself',line_color = "#03d6e5")

    fig.update_layout(
        template=None,
        polar = dict(
            radialaxis = dict(showticklabels=False, ticks=''),
            angularaxis = dict(showticklabels=True, ticks='')
        )
    )
    fig.update_layout(paper_bgcolor = "#1a2330",title='Day Wise')               
    fig.update_layout(
        font_color="white",
        title_font_color="white")

    return fig
# ---------------------------------------------------
def getDataPoint(line):
    """
      function to extract date, time, author and message from line.
    Parameters
    ----------
    line : TYPE
        DESCRIPTION.
    Returns : date, time, author,message
    -------
    """
    splitLine = line.split(' - ')

    dateTime = splitLine[0]

    if ',' not in dateTime:
        dateTime = dateTime.replace(' ', ', ', 1)

    date, time = dateTime.split(', ')

    message = ' '.join(splitLine[1:])

    splitMessage = message.split(': ')
    author = splitMessage[0]
    message = ' '.join(splitMessage[1:])
   
    return date, time, author, message
# ======================================End Functions==============================================


# =======================================Sidebar===================================================
st.sidebar.markdown("<h1 style='text-align: center; color: white;'>Powered By Data Scientist Abdelhamid Adel</h1>", unsafe_allow_html=True)
st.sidebar.caption("<h5 style='text-align: center;'><a href='https://github.com/AbdelhamidADel'>My GitHub</a></h5>", unsafe_allow_html=True)
st.sidebar.caption("This app is use to analyze your WhatsApp Chat using the exported text file 📁.")
st.sidebar.caption("**Don't worry your data is not stored!**")
st.sidebar.caption("**feel free to use 😊**")
st.sidebar.markdown('**How to export chat text file?**')
st.sidebar.text('Follow the steps 👇:')
st.sidebar.text('1) Open the individual or group chat.')
st.sidebar.text('2) Tap options > More > Export chat.')
st.sidebar.text('3) Choose export without media.')
# -------------------------------------------------
st.sidebar.markdown('**Upload your chat text file:**')
filename = st.sidebar.file_uploader("", type=["txt"])
lang = st.sidebar.radio(
    "What is the language of messages?",
    ('Latin', 'Other'))

# =========================================================
st.markdown("<h1 style='text-align: center; color: white;'>Chat Analysis Dashboard </h1>", unsafe_allow_html=True)
if filename is None :
    print("")        
else:
    try:
        if lang == 'Other':
            x = filename.read().decode("utf-8")
            content = x.splitlines()
            chat = [line.strip() for line in content]    # remove trailing white spaces from line
            clean_chat = [line for line in chat if not "joined using this" in line]  # remove join message warnings
            clean_chat1 = [line for line in clean_chat if not "created group" in line]  # remove message warnings about who created the group
            clean_chat2 = [line for line in clean_chat1 if not "changed this group" in line] # remove message warnings about who changed the group's icon
            clean_chat3 = [line for line in clean_chat2 if not "changed the subject" in line] # remove message warnings about who chnaged the subject
            clean_chat4 = [line for line in clean_chat3 if not "added" in line]     # remove messsge warnings about who added who
            clean_chat5 = [line for line in clean_chat4 if not "removed" in line]    # remove message warnings about who removed who
            clean_chat6 = [line for line in clean_chat5 if not "left" in line]        # remove message warnings about who left the group
            clean_chat_final = [line for line in clean_chat6 if len(line) > 1]
                
            data = []
            messageBuffer = []
            date, time, author = None, None, None
                
                
            for line in clean_chat_final:
                if re.findall("\A\d+[/]", line):         
                    if len(messageBuffer) > 0:    
                        data.append([date, time, author, ' '.join(messageBuffer)])
                    messageBuffer.clear()  # clear mesage data so it can be used for the next message
                    date, time, author, message = getDataPoint(line)
                    messageBuffer.append(message)        
                else:
                    messageBuffer.append(line)

            data1 =pd.DataFrame(data, columns=['Date', 'Time', 'Name', 'Messages'])# Initialising a pandas Dataframe.
            data1 = data1.dropna()
            data1["Date"] = pd.to_datetime(data1["Date"])
            data1["Date"] = pd.to_datetime(data1["Date"],format='%Y-%m-%d')
            data1['year'] = data1['Date'].dt.year
            data1['month'] = data1['Date'].dt.month
            data1['day'] = data1['Date'].dt.day
            data1['hour'] = data1['Time'].apply(lambda x: str(x).strip(':')[0:2])
            data1['hour']= data1['hour'].apply(lambda x: x.strip(":"))
            
            if len(data1)!=0:
                options = st.multiselect('Visualization Options',
                ['Data', 'Relation Pie',  'Wordcloud','Emojis','Timeline',"Am Messages","Pm Messages",'Day Wise'],disabled=False,
                default=['Data', 'Relation Pie', 'Wordcloud','Emojis','Timeline',"Am Messages","Pm Messages",'Day Wise'])
                st.sidebar.success("Upload successfully 👌")
            else:
                st.sidebar.warning("Check Upload File First to Start ⚠️")
                options = st.multiselect('Visualization Options',
                [],disabled=True)


        elif lang == 'Latin':
            data1=data_read(filename)
            data1.Date = pd.to_datetime(data1.Date)

            if len(data1)!=0:
                options = st.multiselect('Visualization Options',
                ['Data', 'Relation Pie',  'Wordcloud','Emojis','Timeline',"Am Messages","Pm Messages",'Day Wise'],disabled=False,
                default=['Data', 'Relation Pie', 'Wordcloud','Emojis','Timeline',"Am Messages","Pm Messages",'Day Wise'])
                st.sidebar.success("Upload successfully 👌")
            else:
                
                options = st.multiselect('Visualization Options',
                [],disabled=True)


    except:
        st.sidebar.warning("Check Upload File First to Start ⚠️")
        options = st.multiselect('Visualization Options',
        [],disabled=True)

# ======================================End Sidebar==============================================

# ======================================Start HomePage==============================================
try:
    if len(data1)!=0:
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            wch_colour_box = (54,169,138)
            wch_colour_font = (255,255,255)
            fontsize = 30
            valign = "center"
            iconname = "fa-regular fa-messages"
            sline = "Total Messages"
            lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
            i = len(data1)

            htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                        {wch_colour_box[1]}, 
                                                        {wch_colour_box[2]}, 1); 
                                    color: rgb({wch_colour_font[0]}, 
                                            {wch_colour_font[1]}, 
                                            {wch_colour_font[2]}, 1); 
                                    font-size: {fontsize}px; 
                                    border-radius: 7px; 
                                    padding-left: 12px; 
                                    padding-top: 18px;
                                    box-shadow: 0px 5px 10px 0px rgba(165,241,233,0.5);
                                    padding-bottom: 18px; 
                                    line-height:25px;'>
                                    <i class='f4b6 {iconname}'></i> {i} 
                                    </style><BR><span style='font-size: 14px; 
                                    margin-top: 0;'>{sline}</style></span></p>"""

            st.markdown(lnk + htmlstr, unsafe_allow_html=True)

        with col2:
            data1['counter'] = data1.Messages.apply(lambda x: len(str(x).split(' ')))
            wch_colour_box2 = (54,169,138)
            wch_colour_font2 = (255,255,255)
            fontsize2 = 30
            valign2 = "center"
            iconname2 = "fa-regular fa-messages"
            sline2 = "Total Words"
            lnk2 = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
            i2 = sum(data1['counter'])

            htmlstr2 = f"""<p style='background-color: rgb({wch_colour_box2[0]}, 
                                                        {wch_colour_box2[1]}, 
                                                        {wch_colour_box2[2]}, 1); 
                                    color: rgb({wch_colour_font2[0]}, 
                                            {wch_colour_font2[1]}, 
                                            {wch_colour_font2[2]}, 1); 
                                    font-size: {fontsize2}px; 
                                    border-radius: 7px; 
                                    padding-left: 12px; 
                                    padding-top: 18px;
                                    box-shadow: 0px 5px 10px 0px rgba(165,241,233,0.5); 
                                    padding-bottom: 18px; 
                                    line-height:25px;'>
                                    <i class='f4b6 {iconname2}'></i> {i2}
                                    </style><BR><span style='font-size: 14px; 
                                    margin-top: 0;'>{sline2}</style></span></p>"""

            st.markdown(lnk2 + htmlstr2, unsafe_allow_html=True)
        with col3:
            emoji_msg = []
            for message in data1['Messages']:
                emoji_msg.extend(emojis.get(message))
            wch_colour_box3 = (54,169,138)
            wch_colour_font3 = (255,255,255)
            fontsize3 = 30
            valign3 = "center"
            iconname3= "fa-regular fa-messages"
            sline3 = "Total Emojis"
            lnk3 = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
            i3 = len(emoji_msg)

            htmlstr3 = f"""<p style='background-color: rgb({wch_colour_box3[0]}, 
                                                        {wch_colour_box3[1]}, 
                                                        {wch_colour_box3[2]}, 1); 
                                    color: rgb({wch_colour_font3[0]}, 
                                            {wch_colour_font3[1]}, 
                                            {wch_colour_font3[2]}, 1); 
                                    font-size: {fontsize3}px; 
                                    border-radius: 7px; 
                                    padding-left: 12px;
                                    box-shadow: 0px 5px 10px 0px rgba(165,241,233,0.5);
                                    padding-top: 18px; 
                                    padding-bottom: 18px; 
                                    line-height:25px;'>
                                    <i class='f4b6 {iconname3}'></i> {i3}
                                    </style><BR><span style='font-size: 14px; 
                                    margin-top: 0;'>{sline3}</style></span></p>"""

            st.markdown(lnk3 + htmlstr3, unsafe_allow_html=True)    

        with col4:
            wch_colour_box4 = (54,169,138)
            wch_colour_font4 = (255,255,255)
            fontsize4 = 30
            valign4 = "center"
            iconname4= "fa-regular fa-messages"
            sline4 = "Links Shared"
            lnk4 = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
            i4 = extractor_url()

            htmlstr4 = f"""<p style='background-color: rgb({wch_colour_box4[0]}, 
                                                        {wch_colour_box4[1]}, 
                                                        {wch_colour_box4[2]}, 1); 
                                    color: rgb({wch_colour_font4[0]}, 
                                            {wch_colour_font4[1]}, 
                                            {wch_colour_font4[2]}, 1); 
                                    font-size: {fontsize4}px; 
                                    border-radius: 7px; 
                                    padding-left: 12px; 
                                    padding-top: 18px;
                                    box-shadow: 0px 5px 10px 0px rgba(165,241,233,0.5);
                                    padding-bottom: 18px; 
                                    line-height:25px;'>
                                    <i class='f4b6 {iconname4}'></i> {i4}
                                    </style><BR><span style='font-size: 14px; 
                                    margin-top: 0;'>{sline4}</style></span></p>"""

            st.markdown(lnk4 + htmlstr4, unsafe_allow_html=True)    

        with col5:
            wch_colour_box5 = (54,169,138)
            wch_colour_font5 = (255,255,255)
            fontsize5 = 30
            valign5 = "center"
            iconname5= "fa-regular fa-messages"
            sline5 = "Media Shared"
            lnk5 = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
            media = data1['Messages'].value_counts().values[0]
            i5 = media

            htmlstr5 = f"""<p style='background-color: rgb({wch_colour_box5[0]}, 
                                                        {wch_colour_box5[1]}, 
                                                        {wch_colour_box5[2]}, 1); 
                                    color: rgb({wch_colour_font5[0]}, 
                                            {wch_colour_font5[1]}, 
                                            {wch_colour_font5[2]}, 1); 
                                    font-size: {fontsize5}px; 
                                    border-radius: 7px; 
                                    padding-left: 12px; 
                                    padding-top: 18px;
                                    box-shadow: 0px 5px 10px 0px rgba(165,241,233,0.5);
                                    padding-bottom: 18px; 
                                    line-height:25px;'>
                                    <i class='f4b6 {iconname5}'></i> {i5}
                                    </style><BR><span style='font-size: 14px; 
                                    margin-top: 0;'>{sline5}</style></span></p>"""

            st.markdown(lnk5 + htmlstr5, unsafe_allow_html=True)  

        st.write("##")
        if 'Wordcloud' in options:
            try:
                st.pyplot(wordcloud())
            except:
                print()


        head_left,head_right=st.columns(2)
        if 'Data' in options:
            try:
                with head_left:
                    st.dataframe(data1, width=1000)
            except:
                st.error("Sorry, I can't display Data ..")

        #--------------------------------------------------------------------------

        if 'Relation Pie' in options:
            try:
                with head_right:
                    st.plotly_chart(relation_plot(), use_container_width=True)
            except:
                st.error("Sorry, I can't display Relation Pie ..")

        #--------------------------------------------------------------------------
        median_left,median_right=st.columns(2)


        #--------------------------------------------------------------------------
        if 'Day Wise' in options:
            try:
                with median_right:
                    # st.markdown("<h6 style='text-align: center; color: white;'>Most Repeated Words </h6>", unsafe_allow_html=True)
                    st.plotly_chart(day_wise_count(),use_container_width=True)
            except:
                st.error("Sorry, I can't display Day Wise ..")


        #--------------------------------------------------------------------------
        if 'Emojis' in options:
            try:
                with median_left:
                    st.plotly_chart(plot_emoji(), use_container_width=True)
            except:
                st.error("Sorry, I can't display Emojis ..")


        #--------------------------------------------------------------------------

        data1['year'] = data1['Date'].dt.year
        data1['month'] = data1['Date'].dt.month
        data1['day'] = data1['Date'].dt.day
        data1['hour'] = data1['Time'].apply(lambda x: str(x).strip(':')[0:2])
        timeline = data1.groupby(['year', 'month', 'day']).count()['Messages'].reset_index()
        time=[]
        for i in range(timeline.shape[0]):
            time.append(str(timeline['month'][i]) + '-' + str(timeline['year'][i]))
        timeline['time'] = time
        timeseris_list=timeline.time.unique()
        series={}
        for i in timeseris_list:
            new=timeline.loc[timeline['time'] == i]
            series[i]=new.Messages.sum()
        data_series=pd.DataFrame({'Time': series.keys(),
                'Messages': series.values()})
        line_series=go.Figure()

        line_series.add_trace(go.Scatter(x=data_series['Time'], y=data_series['Messages'],
                        name='lines+markers', 
                        line_color='rgb(111,212,152)',fill='tozeroy'))
        line_series.update_xaxes(showgrid=False)
        line_series.update_yaxes(showgrid=False)
        line_series.update_layout(paper_bgcolor = "#1a2330",title='Messages Rate')
        if 'Timeline' in options:
            try:
                st.plotly_chart(line_series, use_container_width=True,)
            except:
                st.error("Sorry, I can't display Timeline ..")


    # #--------------------------------------------------------------------------
        most_hours = data1.groupby('hour').count()['Messages'].reset_index()
        most_hours['hour']= most_hours['hour'].apply(lambda x: x.strip(":"))
        most_hours.hour=most_hours.hour.astype("int")
        most_hours.replace(to_replace=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],value=['0 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM'],inplace=True)
        most_hours.replace(to_replace=[12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],value=['12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM'],inplace=True)
        am = most_hours.iloc[0:12]
        pm = most_hours.iloc[12:24]
        bar_chart_am = px.bar(am,
                        x='hour',
                        y='Messages',
                        text='Messages',
                        color_discrete_sequence = ['#FFE15D']*len(am),
                        template= 'simple_white')
        bar_chart_am.update_layout(paper_bgcolor = "#1a2330",title='AM Messages')

        bar_chart_pm = px.bar(pm,
                        x='hour',
                        y='Messages',
                        text='Messages',
                        color_discrete_sequence = ['#046582']*len(pm),
                        template= 'simple_white')
        bar_chart_pm.update_layout(paper_bgcolor = "#1a2330",title='PM Messages')               
        col_am, col_pm= st.columns(2)
        if 'Am Messages' in options :
            try:
                with col_am:                   
                    st.plotly_chart(bar_chart_am, use_container_width=True)
            except:
                st.error("Sorry, I can't display Am Messages ..")
        if 'Pm Messages' in options :
            try:        
                with col_pm:        
                    st.plotly_chart(bar_chart_pm, use_container_width=True)
            except:
                st.error("Sorry, I can't display Pm Messages ..")


        # -----------------------------

        # ---- HIDE STREAMLIT STYLE ----
        hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_st_style, unsafe_allow_html=True)
except:
    print("")
