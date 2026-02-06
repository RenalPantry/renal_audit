def apply_custom_styles():
    """Inject custom CSS styles into the Streamlit app"""
    import streamlit as st
    st.markdown(
        """
        <style>
            /* Make sidebar narrower */
            [data-testid="stSidebar"] {
                min-width: 150px !important;
                max-width: 150px !important;
            }

            /* Adjust sidebar content padding */
            [data-testid="stSidebar"] > div:first-child {
                padding: 1rem 0.3rem;
            }

            /* Make buttons more compact */
            [data-testid="stSidebar"] .stButton button {
                padding: 0.3rem 0.4rem;
                font-size: 0.85rem;
            }

            /* Smaller title */
            [data-testid="stSidebar"] h1 {
                font-size: 1.2rem;
            }

            /* Force 3 columns on mobile - aggressive approach */
            @media (max-width: 640px) {
                [data-testid="column"] {
                    width: 33% !important;
                    flex: 0 0 33% !important;
                    min-width: 33% !important;
                    max-width: 33% !important;
                }

                /* Force horizontal layout */
                div[data-testid="stHorizontalBlock"] {
                    flex-direction: row !important;
                    gap: 0.25rem !important;
                }

                /* Make metrics more compact on mobile */
                [data-testid="stMetric"] {
                    font-size: 0.7rem;
                    padding: 0.25rem !important;
                }

                [data-testid="stMetricLabel"] {
                    font-size: 0.6rem !important;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }

                [data-testid="stMetricValue"] {
                    font-size: 0.9rem !important;
                }

                [data-testid="stMetricDelta"] {
                    font-size: 0.65rem !important;
                }

                [data-testid="stMetricDelta"] svg {
                    width: 8px !important;
                    height: 8px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True
    )
    

def nutrient_comparison_style(values, delta_color, delta_percent, nutrient, unit):
    """
    Generate the HTML style for nutrient comparison.
    """
    def format_value(value):
        if value is None:
            return "-"
        return f"{value:.1f}"

    def format_delta(value):
        if value is None:
            return "-"
        return f"{value:+.1f}%"

    return f"""
    <div style="display: grid; grid-template-columns: 1fr 100px 1fr; gap: 0.1rem; align-items: center; justify-content: center; margin-bottom: 0.5rem; padding: 0.25rem; min-height: 50px;">
        <div style="text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-size: 1.2rem; font-weight: bold; line-height: 1.2;">{format_value(values['label'])}</div>
            <div style="font-size: 0.75rem; color: {delta_color}; font-weight: bold; line-height: 1.2; margin-top: 2px;">{format_delta(delta_percent)}</div>
        </div>
        <div style="text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; width: 100px;">
            <div style="font-weight: bold; font-size: 0.9rem; line-height: 1.2;">{nutrient}</div>
            <div style="font-size: 0.7rem; color: #666; line-height: 1.2; margin-top: 2px;">({unit})</div>
        </div>
        <div style="text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-size: 1.2rem; font-weight: bold; line-height: 1.2;">{format_value(values['usda'])}</div>
        </div>
    </div>
    """