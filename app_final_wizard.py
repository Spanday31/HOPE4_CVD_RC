import streamlit as st
from datetime import date

# Initialize session state safely
if 'age' not in st.session_state:
    st.session_state.update({
        'age': 65,
        'sex': "Male",
        'diabetes': False,
        'smoker': False,
        'egfr': 90,
        'ldl': 3.5,
        'sbp': 140,
        'cad': False,
        'stroke': False,
        'pad': False
    })

# SMART-2 Risk Calculation (pure Python implementation)
def calculate_smart2_risk():
    try:
        # Convert inputs to numbers safely
        age = float(st.session_state.age)
        egfr = float(st.session_state.egfr)
        ldl = float(st.session_state.ldl)
        sbp = float(st.session_state.sbp)
        vasc_count = sum([st.session_state.cad, st.session_state.stroke, st.session_state.pad])
        
        # Coefficients from SMART-2 paper
        coefficients = {
            'intercept': -8.1937,
            'age': 0.0635 * (age - 60),
            'female': -0.3372 if st.session_state.sex == "Female" else 0,
            'diabetes': 0.5034 if st.session_state.diabetes else 0,
            'smoker': 0.7862 if st.session_state.smoker else 0,
            'egfr<30': 0.9235 if egfr < 30 else 0,
            'egfr30-60': 0.5539 if 30 <= egfr < 60 else 0,
            'polyvascular': 0.5434 if vasc_count >= 2 else 0,
            'ldl': 0.2436 * (ldl - 2.5),
            'sbp': 0.0083 * (sbp - 120)
        }
        
        # Calculate risk
        lp = sum(coefficients.values())
        risk_percent = 100 * (1 - 2.71828**(-2.71828**lp * 10))  # Using e≈2.71828 to avoid math import
        return max(1.0, min(99.0, round(risk_percent, 1)))
    except:
        return None  # Will be handled in display

# App layout
def main():
    st.set_page_config(
        page_title="PRIME CVD Risk Calculator",
        layout="wide",
        page_icon="❤️"
    )
    
    # Header - No external image needed
    st.title("PRIME SMART-2 CVD Risk Calculator")
    st.markdown("""
    <div style="background:#f0f2f6;padding:10px;border-radius:5px;margin-bottom:20px">
    <strong style="font-size:1.2em">Cardiovascular Risk Assessment</strong><br>
    <em>Based on SMART-2 Risk Score</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Inputs
    with st.sidebar:
        st.header("Patient Profile")
        
        # Demographic inputs
        st.session_state.age = st.slider("Age (years)", 30, 90, st.session_state.age, key='age_input')
        st.session_state.sex = st.radio("Sex", ["Male", "Female"], index=0 if st.session_state.sex == "Male" else 1, key='sex_input')
        
        # Risk factors
        st.session_state.diabetes = st.checkbox("Diabetes", st.session_state.diabetes, key='diabetes_input')
        st.session_state.smoker = st.checkbox("Current smoker", st.session_state.smoker, key='smoker_input')
        
        # Biomarkers
        st.session_state.egfr = st.slider("eGFR (mL/min)", 15, 120, st.session_state.egfr, key='egfr_input')
        st.session_state.ldl = st.number_input("LDL-C (mmol/L)", 1.0, 10.0, st.session_state.ldl, step=0.1, key='ldl_input')
        st.session_state.sbp = st.number_input("SBP (mmHg)", 90, 220, st.session_state.sbp, key='sbp_input')
        
        # Vascular disease
        st.subheader("Vascular Disease")
        st.session_state.cad = st.checkbox("Coronary artery disease", st.session_state.cad, key='cad_input')
        st.session_state.stroke = st.checkbox("Prior stroke/TIA", st.session_state.stroke, key='stroke_input')
        st.session_state.pad = st.checkbox("Peripheral artery disease", st.session_state.pad, key='pad_input')
    
    # Main content
    tab1, tab2 = st.tabs(["Risk Assessment", "Clinical Guidance"])
    
    with tab1:
        # Calculate and display risk
        risk = calculate_smart2_risk()
        
        if risk is not None:
            st.subheader("10-Year Risk Estimate")
            
            # Visual risk display
            if risk >= 30:
                st.error(f"**{risk}%** - Very High Risk")
            elif risk >= 20:
                st.warning(f"**{risk}%** - High Risk")
            else:
                st.success(f"**{risk}%** - Moderate Risk")
            
            # Risk factor summary
            with st.expander("Risk Factors"):
                factors = [
                    f"Age: {st.session_state.age}",
                    f"Sex: {st.session_state.sex}",
                    f"LDL-C: {st.session_state.ldl} mmol/L",
                    f"SBP: {st.session_state.sbp} mmHg"
                ]
                if st.session_state.diabetes:
                    factors.append("Diabetes: Yes")
                if st.session_state.smoker:
                    factors.append("Smoker: Yes")
                if st.session_state.egfr < 60:
                    factors.append(f"eGFR: {st.session_state.egfr} (CKD)")
                
                vasc_count = sum([st.session_state.cad, st.session_state.stroke, st.session_state.pad])
                if vasc_count > 0:
                    factors.append(f"Vascular Territories: {vasc_count}")
                
                st.markdown(" • ".join(factors))
        else:
            st.warning("Complete all fields to calculate risk")
    
    with tab2:
        st.header("Clinical Recommendations")
        
        if 'risk' in locals() and risk is not None:
            if risk >= 30:
                st.error("""
                **Very High Risk Management:**
                - High-intensity statin (atorvastatin 40-80mg or rosuvastatin 20-40mg)
                - Consider PCSK9 inhibitor if LDL ≥1.8 mmol/L
                - Target SBP <130 mmHg if tolerated
                - Annual monitoring
                """)
            elif risk >= 20:
                st.warning("""
                **High Risk Management:**
                - Moderate-high intensity statin
                - Target SBP <130 mmHg
                - Lifestyle modifications
                - Biannual monitoring
                """)
            else:
                st.success("""
                **Moderate Risk Management:**
                - Moderate intensity statin
                - Target SBP <140 mmHg
                - Lifestyle counseling
                - Routine follow-up
                """)
        else:
            st.info("Complete risk assessment to see recommendations")
    
    # Footer
    st.divider()
    st.caption(f"PRIME Cardiology • {date.today().strftime('%Y-%m-%d')} • v2.0")

if __name__ == "__main__":
    main()
