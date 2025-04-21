
import streamlit as st
import os
import math
from io import StringIO

# ── Page Config & CSS ─────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="SMART CVD Risk Reduction")
st.markdown("""
<style>
.header { position: sticky; top: 0; background:#f7f7f7; padding:10px; display:flex; justify-content:flex-end; z-index:100;}
.card { background:#fff; padding:15px; margin:15px 0; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# ── Header with Logo ─────────────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.warning("⚠️ Upload logo.png")
st.markdown('</div>', unsafe_allow_html=True)

# ── Progress Selector ─────────────────────────────────────────────────────────
step = st.selectbox("Go to Step", ["1 Profile", "2 Labs", "3 Therapies", "4 Results"])

# ── Initialize defaults ───────────────────────────────────────────────────────
defaults = {
    'age':60, 'sex':'Male', 'weight':75.0, 'height':170.0,
    'smoker':False, 'diabetes':False, 'egfr':90,
    'tc':5.2, 'hdl':1.3, 'ldl0':3.0, 'crp':2.5,
    'hba1c':7.0, 'tg':1.2,
    'pre_stat':'None','pre_ez':False,'pre_bemp':False,
    'new_stat':'None','new_ez':False,'new_bemp':False,
    'sbp':140
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Risk Functions ────────────────────────────────────────────────────────────
def estimate_10y(age, sex, sbp, tc, hdl, smoker, diabetes, egfr, crp, vasc):
    sv = 1 if sex=='Male' else 0
    sm=1 if smoker else 0
    dm=1 if diabetes else 0
    lp = 0.064*age + 0.34*sv + 0.02*sbp + 0.25*tc -0.25*hdl +0.44*sm +0.51*dm -0.2*(egfr/10)+0.25*math.log(crp+1)+0.4*vasc
    raw = 1 - 0.900**math.exp(lp-5.8)
    return min(raw*100,95.0)

def convert_5yr(r10):
    p = min(r10,95.0)/100
    return min((1-(1-p)**0.5)*100,95.0)

def estimate_lt(age, r10):
    years = max(85-age,0)
    annual = 1 - (1-min(r10,95.0)/100)**(1/10)
    return min((1- (1-annual)**years)*100,95.0)

# ── UI Sections ────────────────────────────────────────────────────────────────
if step=='1 Profile':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader('Step 1: Profile')
    st.session_state.age = st.number_input('Age', 30, 90, st.session_state.age)
    st.session_state.sex = st.selectbox('Sex',['Male','Female'], index=0 if st.session_state.sex=='Male' else 1)
    st.session_state.weight = st.number_input('Weight (kg)',40.0,200.0,st.session_state.weight)
    st.session_state.height = st.number_input('Height (cm)',140.0,210.0,st.session_state.height)
    st.session_state.smoker = st.checkbox('Smoker', value=st.session_state.smoker)
    st.session_state.diabetes = st.checkbox('Diabetes', value=st.session_state.diabetes)
    st.session_state.egfr = st.slider('eGFR',15,120,st.session_state.egfr)
    st.markdown('</div>', unsafe_allow_html=True)

elif step=='2 Labs':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader('Step 2: Labs')
    st.session_state.tc = st.number_input('Total Chol',2.0,10.0,st.session_state.tc)
    st.session_state.hdl = st.number_input('HDL',0.5,3.0,st.session_state.hdl)
    st.session_state.ldl0 = st.number_input('LDL',0.5,6.0,st.session_state.ldl0)
    st.session_state.crp = st.number_input('hs-CRP',0.1,20.0,st.session_state.crp)
    st.session_state.hba1c = st.number_input('HbA1c',4.0,14.0,st.session_state.hba1c)
    st.session_state.tg = st.number_input('Trig',0.3,5.0,st.session_state.tg)
    st.markdown('</div>', unsafe_allow_html=True)

elif step=='3 Therapies':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader('Step 3: Therapies')
    options=['None','Atorvastatin','Rosuvastatin']
    st.session_state.pre_stat = st.selectbox('Pre Statin',options,index=0)
    st.session_state.pre_ez = st.checkbox('Pre Ezetimibe',value=st.session_state.pre_ez)
    st.session_state.pre_bemp = st.checkbox('Pre Bempedoic',value=st.session_state.pre_bemp)
    st.session_state.new_stat = st.selectbox('New Statin',options,index=0)
    st.session_state.new_ez = st.checkbox('Add Ezetimibe',value=st.session_state.new_ez)
    st.session_state.new_bemp = st.checkbox('Add Bempedoic',value=st.session_state.new_bemp)
    st.markdown('</div>', unsafe_allow_html=True)

elif step=='4 Results':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader('Step 4: Results')
    vasc = sum([st.session_state.pre_stat!='None', st.session_state.pre_ez, st.session_state.pre_bemp])
    r10 = estimate_10y(st.session_state.age,st.session_state.sex,st.session_state.egfr,
                       st.session_state.tc,st.session_state.hdl,st.session_state.smoker,
                       st.session_state.diabetes,st.session_state.egfr,st.session_state.crp,vasc)
    r5 = convert_5yr(r10)
    lt = estimate_lt(st.session_state.age, r10)
    st.write(f'5yr: {r5:.1f}%, 10yr: {r10:.1f}%, LT: {lt:.1f}%')
    csv = StringIO()
    csv.write('metric,value\n')
    csv.write(f'5yr,{r5:.1f}\n10yr,{r10:.1f}\nLT,{lt:.1f}\n')
    st.download_button('Download CSV', csv.getvalue(), 'results.csv', 'text/csv')
    st.bar_chart({'Risk':[r5,r10,lt]}).container()
    st.markdown('</div>', unsafe_allow_html=True)
