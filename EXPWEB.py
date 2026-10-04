import streamlit as st
import pyodbc
import pandas as pd
import math
from datetime import date
from html import escape
from textwrap import dedent

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ExpenseAI",
    page_icon="EA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# IMPORTANT:
# HTML IS ALWAYS DEDENTED + STRIPPED BEFORE MARKDOWN.
# THIS PREVENTS STREAMLIT FROM SHOWING HTML AS CODE.
# ============================================================

def render(html_code):
    clean_html = dedent(str(html_code)).strip()
    st.html(clean_html)


def money(value):
    try:
        return f"Rs {float(value):,.2f}"
    except (TypeError, ValueError):
        return "Rs 0.00"


# ============================================================
# DATABASE
# ============================================================

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=JOSH\SQLEXPRESS01;"
    "DATABASE=EXPENSETRACKER;"
    "Trusted_Connection=yes;"
)


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)


def load_data():

    connection = get_connection()

    try:

        query = """
        SELECT
            EXPENSEID,
            EXPENSEDATE,
            CATEGORY,
            DESCRIPTIONTYPE,
            AMOUNT,
            PAYMENTMETHOD
        FROM Expenses
        ORDER BY EXPENSEDATE DESC, EXPENSEID DESC
        """

        data = pd.read_sql(
            query,
            connection
        )

    finally:

        connection.close()

    if not data.empty:

        data["EXPENSEDATE"] = pd.to_datetime(
            data["EXPENSEDATE"],
            errors="coerce"
        )

        data["AMOUNT"] = pd.to_numeric(
            data["AMOUNT"],
            errors="coerce"
        ).fillna(0)

        data["CATEGORY"] = (
            data["CATEGORY"]
            .fillna("Other")
            .astype(str)
        )

        data["DESCRIPTIONTYPE"] = (
            data["DESCRIPTIONTYPE"]
            .fillna("Expense")
            .astype(str)
        )

        data["PAYMENTMETHOD"] = (
            data["PAYMENTMETHOD"]
            .fillna("Other")
            .astype(str)
        )

    return data


def insert_expense(
    expense_date,
    category,
    description,
    amount,
    payment_method
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO Expenses
            (
                EXPENSEDATE,
                CATEGORY,
                DESCRIPTIONTYPE,
                AMOUNT,
                PAYMENTMETHOD
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                expense_date,
                category,
                description,
                amount,
                payment_method
            )
        )

        connection.commit()

        cursor.close()

    finally:

        connection.close()


def delete_expense(expense_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM Expenses
            WHERE EXPENSEID = ?
            """,
            (expense_id,)
        )

        connection.commit()

        cursor.close()

    finally:

        connection.close()


# ============================================================
# LOAD DATABASE
# ============================================================

try:

    df = load_data()

except Exception as e:

    st.error("SQL Server connection failed.")
    st.code(str(e))
    st.stop()


# ============================================================
# DATA CALCULATIONS
# ============================================================

if not df.empty:

    total_expense = float(
        df["AMOUNT"].sum()
    )

    transaction_count = len(df)

    average_expense = float(
        df["AMOUNT"].mean()
    )

    category_totals = (
        df.groupby("CATEGORY")["AMOUNT"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    payment_totals = (
        df.groupby("PAYMENTMETHOD")["AMOUNT"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    top_category = (
        category_totals.index[0]
        if not category_totals.empty
        else "None"
    )

else:

    total_expense = 0
    transaction_count = 0
    average_expense = 0
    category_totals = pd.Series(dtype=float)
    payment_totals = pd.Series(dtype=float)
    top_category = "None"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   ROOT
   ========================================================== */

:root {

    --primary: #1769ff;
    --primary-dark: #0c3f91;
    --primary-light: #eaf3ff;

    --navy: #092b67;
    --text: #102d63;
    --muted: #7183a4;

    --green: #12b878;
    --purple: #7258f6;
    --pink: #e94fba;
    --cyan: #21b7d9;
    --orange: #ff9f43;

    --border: #dfeafb;
    --background: #f6f9ff;

    --shadow:
        0 8px 30px rgba(38, 93, 180, 0.08);

    --shadow-hover:
        0 18px 45px rgba(38, 93, 180, 0.15);
}


/* ==========================================================
   MAIN STREAMLIT AREA
   ========================================================== */

html,
body {

    margin: 0 !important;
    padding: 0 !important;

    background:
        #f6f9ff !important;
}


[data-testid="stAppViewContainer"] {

    background:
        linear-gradient(
            135deg,
            #f9fbff 0%,
            #f3f8ff 48%,
            #f8fbff 100%
        ) !important;
}


[data-testid="stMain"] {

    background:
        transparent !important;
}


.block-container {

    width: 100% !important;

    max-width: 100% !important;

    padding-top: 18px !important;
    padding-left: 18px !important;
    padding-right: 18px !important;
    padding-bottom: 45px !important;
}


/* ==========================================================
   HIDE DEFAULT STREAMLIT ELEMENTS
   ========================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stHeader"] {

    background:
        transparent !important;

    height: 0 !important;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

[data-testid="stSidebar"] {

    width: 255px !important;

    min-width: 255px !important;

    background:
        #ffffff !important;

    border-right:
        1px solid #e3ecfa !important;

    box-shadow:
        6px 0 30px rgba(29, 79, 155, 0.04);
}


[data-testid="stSidebar"] > div:first-child {

    background:
        #ffffff !important;

    padding-top:
        15px !important;
}


[data-testid="stSidebar"] * {

    font-family:
        Inter,
        Segoe UI,
        sans-serif;
}


/* ==========================================================
   BRAND
   ========================================================== */

.brand {

    display:
        flex;

    align-items:
        center;

    gap:
        13px;

    padding:
        5px 8px 24px 8px;
}


.brand-logo {

    width:
        43px;

    height:
        43px;

    border-radius:
        12px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    color:
        white;

    font-size:
        12px;

    font-weight:
        900;

    background:
        linear-gradient(
            145deg,
            #4d9aff,
            #0758df
        );

    box-shadow:
        0 10px 22px
        rgba(23,105,255,.25);

    animation:
        logoFloat 3.5s ease-in-out infinite;
}


.brand-name {

    color:
        #082d6d;

    font-size:
        20px;

    font-weight:
        900;

    letter-spacing:
        -.7px;
}


.brand-sub {

    margin-top:
        2px;

    color:
        #7890b5;

    font-size:
        7px;

    font-weight:
        600;

    letter-spacing:
        .3px;
}


/* ==========================================================
   SIDEBAR RADIO
   ========================================================== */

[data-testid="stSidebar"]
[data-testid="stRadio"] > div {

    gap:
        5px !important;
}


[data-testid="stSidebar"]
[data-testid="stRadio"] label {

    border-radius:
        10px !important;

    padding:
        9px 11px !important;

    color:
        #153a78 !important;

    font-size:
        13px !important;

    font-weight:
        600 !important;

    transition:
        all .25s ease !important;
}


[data-testid="stSidebar"]
[data-testid="stRadio"] label:hover {

    background:
        #eef5ff !important;

    transform:
        translateX(3px);
}


/* ==========================================================
   SIDEBAR BOTTOM CARD
   ========================================================== */

.sidebar-bottom {

    position:
        relative;

    overflow:
        hidden;

    margin:
        30px 4px 0 4px;

    min-height:
        150px;

    padding:
        20px;

    border-radius:
        16px;

    background:
        linear-gradient(
            145deg,
            #f1f8ff,
            #e5f0ff
        );

    border:
        1px solid #dceaff;
}


.sidebar-bottom-title {

    max-width:
        135px;

    color:
        #1769ff;

    font-size:
        12px;

    line-height:
        1.7;

    font-weight:
        700;
}


.sidebar-wave {

    position:
        absolute;

    left:
        -20px;

    right:
        -20px;

    bottom:
        -30px;

    height:
        80px;

    border-radius:
        50%;

    background:
        linear-gradient(
            180deg,
            #b9d8ff,
            #1769ff
        );

    transform:
        rotate(-4deg);

    animation:
        waveMove 5s ease-in-out infinite;
}


/* ==========================================================
   TOP HEADER
   ========================================================== */

.top-header {

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;

    margin:
        0 0 20px 0;

    padding:
        0 2px;

    animation:
        fadeDown .65s ease both;
}


.greeting {

    display:
        flex;

    align-items:
        center;

    gap:
        14px;
}


.greeting-icon {

    width:
        48px;

    height:
        48px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        50%;

    background:
        #eef5ff;

    font-size:
        25px;

    animation:
        handWave 3s ease-in-out infinite;
}


.greeting-title {

    color:
        #092d6c;

    font-size:
        22px;

    font-weight:
        850;

    letter-spacing:
        -.7px;
}


.greeting-sub {

    margin-top:
        3px;

    color:
        #7588a9;

    font-size:
        11px;
}


.header-right {

    display:
        flex;

    align-items:
        center;

    gap:
        12px;
}


.date-pill {

    display:
        flex;

    align-items:
        center;

    gap:
        9px;

    padding:
        11px 17px;

    border:
        1px solid #e1ebfb;

    border-radius:
        24px;

    background:
        white;

    color:
        #59729d;

    font-size:
        10px;

    box-shadow:
        0 5px 18px rgba(45,92,160,.05);
}


.profile-circle {

    width:
        34px;

    height:
        34px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        50%;

    color:
        white;

    background:
        linear-gradient(
            145deg,
            #4e91ff,
            #1769ff
        );

    font-size:
        12px;

    font-weight:
        800;

    box-shadow:
        0 8px 20px
        rgba(23,105,255,.2);
}


/* ==========================================================
   FILTER BAR
   ========================================================== */

.filter-panel {

    display:
        flex;

    align-items:
        center;

    gap:
        12px;

    padding:
        14px;

    margin-bottom:
        20px;

    border:
        1px solid #dce8fa;

    border-radius:
        13px;

    background:
        rgba(255,255,255,.84);

    box-shadow:
        var(--shadow);

    animation:
        fadeUp .7s .08s both;
}


.filter-button {

    height:
        50px;

    padding:
        0 22px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    gap:
        8px;

    border-radius:
        10px;

    color:
        white;

    background:
        linear-gradient(
            135deg,
            #2380ff,
            #075bdc
        );

    font-size:
        12px;

    font-weight:
        800;

    box-shadow:
        0 10px 22px
        rgba(23,105,255,.22);

    transition:
        all .25s ease;
}


.filter-button:hover {

    transform:
        translateY(-3px);

    box-shadow:
        0 15px 28px
        rgba(23,105,255,.30);
}


/* ==========================================================
   METRIC CARDS
   ========================================================== */

.metric-grid {

    display:
        grid;

    grid-template-columns:
        repeat(4, minmax(0,1fr));

    gap:
        14px;

    margin-bottom:
        20px;
}


.metric-card {

    position:
        relative;

    overflow:
        hidden;

    min-height:
        125px;

    padding:
        18px;

    border:
        1px solid var(--border);

    border-radius:
        12px;

    background:
        white;

    box-shadow:
        var(--shadow);

    animation:
        cardEnter .7s var(--delay) both;

    transition:
        transform .3s ease,
        box-shadow .3s ease;
}


.metric-card:hover {

    transform:
        translateY(-5px);

    box-shadow:
        var(--shadow-hover);
}


.metric-card:after {

    content:
        "";

    position:
        absolute;

    top:
        0;

    left:
        0;

    width:
        100%;

    height:
        3px;

    background:
        var(--accent);

    opacity:
        .65;
}


.metric-icon {

    width:
        43px;

    height:
        43px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        50%;

    color:
        white;

    font-size:
        16px;

    font-weight:
        900;

    background:
        var(--accent);

    box-shadow:
        0 8px 20px
        color-mix(
            in srgb,
            var(--accent) 28%,
            transparent
        );

    float:
        left;

    animation:
        iconPop .7s var(--delay) both;
}


.metric-content {

    margin-left:
        59px;
}


.metric-label {

    color:
        #12366f;

    font-size:
        11px;

    font-weight:
        600;
}


.metric-value {

    margin-top:
        8px;

    color:
        #092d6c;

    font-size:
        23px;

    font-weight:
        900;

    letter-spacing:
        -.7px;
}


.metric-small {

    margin-top:
        6px;

    color:
        #7c8fab;

    font-size:
        9px;
}


.metric-small strong {

    color:
        #10ae72;

    font-weight:
        800;
}


/* ==========================================================
   MAIN CONTENT GRID
   ========================================================== */

.dashboard-grid {

    display:
        grid;

    grid-template-columns:
        minmax(0, 1.75fr)
        minmax(275px, .7fr);

    gap:
        14px;

    align-items:
        start;
}


.left-column {

    min-width:
        0;
}


.right-column {

    min-width:
        0;
}


/* ==========================================================
   CARDS
   ========================================================== */

.panel {

    overflow:
        hidden;

    border:
        1px solid var(--border);

    border-radius:
        12px;

    background:
        white;

    box-shadow:
        var(--shadow);

    animation:
        cardEnter .75s .25s both;

    transition:
        all .3s ease;
}


.panel:hover {

    box-shadow:
        var(--shadow-hover);
}


.panel-header {

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;

    padding:
        15px 18px;

    border-bottom:
        1px solid #eef3fb;
}


.panel-title-wrap {

    display:
        flex;

    align-items:
        center;

    gap:
        10px;
}


.panel-icon {

    width:
        34px;

    height:
        34px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        10px;

    background:
        #eaf3ff;

    color:
        #1769ff;

    font-size:
        13px;

    font-weight:
        900;
}


.panel-title {

    color:
        #092d6c;

    font-size:
        14px;

    font-weight:
        800;
}


.panel-subtitle {

    margin-top:
        2px;

    color:
        #8392ab;

    font-size:
        8px;
}


/* ==========================================================
   BAR CHART
   ========================================================== */

.bar-chart {

    padding:
        18px 20px 20px 20px;
}


.chart-area {

    height:
        250px;

    position:
        relative;

    display:
        flex;

    align-items:
        flex-end;

    gap:
        22px;

    padding:
        20px 12px 0 12px;

    background-image:
        linear-gradient(
            to bottom,
            #edf3fb 1px,
            transparent 1px
        );

    background-size:
        100% 25%;
}


.bar-column {

    flex:
        1;

    height:
        100%;

    display:
        flex;

    flex-direction:
        column;

    align-items:
        center;

    justify-content:
        flex-end;

    min-width:
        45px;
}


.bar-value {

    color:
        #1769ff;

    font-size:
        9px;

    font-weight:
        800;

    margin-bottom:
        7px;

    opacity:
        0;

    animation:
        textAppear .6s
        var(--delay)
        forwards;
}


.bar-shape {

    width:
        min(62px, 80%);

    height:
        var(--height);

    min-height:
        5px;

    border-radius:
        6px 6px 2px 2px;

    background:
        linear-gradient(
            180deg,
            #3d9cff,
            #337ce9
        );

    box-shadow:
        0 7px 18px
        rgba(23,105,255,.18);

    transform:
        scaleY(0);

    transform-origin:
        bottom;

    animation:
        barGrow 1.15s
        cubic-bezier(.2,.8,.2,1)
        var(--delay)
        forwards;

    position:
        relative;
}


.bar-shape:before {

    content:
        "";

    position:
        absolute;

    top:
        0;

    left:
        0;

    right:
        0;

    height:
        1px;

    background:
        rgba(255,255,255,.75);
}


.bar-label {

    margin-top:
        10px;

    color:
        #2c4d7f;

    font-size:
        9px;

    font-weight:
        600;

    text-align:
        center;
}


/* ==========================================================
   DONUT
   ========================================================== */

.donut-area {

    min-height:
        330px;

    padding:
        22px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    gap:
        18px;
}


.donut-svg {

    width:
        185px;

    height:
        185px;

    flex:
        0 0 185px;
}


.donut-base {

    fill:
        none;

    stroke:
        #eef3fb;

    stroke-width:
        25;
}


.donut-piece {

    fill:
        none;

    stroke-width:
        25;

    stroke-linecap:
        butt;

    stroke-dasharray:
        var(--dash);

    stroke-dashoffset:
        var(--circ);

    animation:
        donutDraw 1.45s
        cubic-bezier(.2,.8,.2,1)
        var(--delay)
        forwards;
}


.donut-center-value {

    fill:
        #092d6c;

    font-size:
        16px;

    font-weight:
        900;
}


.donut-center-label {

    fill:
        #8190aa;

    font-size:
        8px;

    font-weight:
        600;
}


.legend {

    min-width:
        135px;

    display:
        flex;

    flex-direction:
        column;

    gap:
        14px;
}


.legend-row {

    display:
        grid;

    grid-template-columns:
        9px 1fr auto;

    gap:
        8px;

    align-items:
        center;
}


.legend-dot {

    width:
        8px;

    height:
        8px;

    border-radius:
        50%;
}


.legend-name {

    color:
        #4f6387;

    font-size:
        9px;
}


.legend-percent {

    color:
        #173b73;

    font-size:
        9px;

    font-weight:
        800;
}


.legend-amount {

    color:
        #7487a6;

    font-size:
        8px;

    grid-column:
        2 / 4;

    margin-top:
        -5px;
}


/* ==========================================================
   INSIGHTS
   ========================================================== */

.insights-panel {

    margin-bottom:
        14px;
}


.insight-item {

    display:
        flex;

    gap:
        11px;

    margin:
        10px;

    padding:
        12px;

    border-radius:
        10px;

    background:
        linear-gradient(
            135deg,
            #ffffff,
            #f8fbff
        );

    box-shadow:
        0 5px 18px rgba(43,86,150,.06);

    animation:
        insightSlide .7s var(--delay) both;

    transition:
        transform .25s ease,
        box-shadow .25s ease;
}


.insight-item:hover {

    transform:
        translateX(4px);

    box-shadow:
        0 10px 25px rgba(43,86,150,.1);
}


.insight-icon {

    width:
        35px;

    height:
        35px;

    flex:
        0 0 35px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        50%;

    color:
        #1769ff;

    background:
        #eaf3ff;

    font-size:
        14px;

    font-weight:
        900;
}


.insight-text {

    color:
        #395681;

    font-size:
        9px;

    line-height:
        1.6;
}


.insight-text strong {

    color:
        #0b3372;

    font-weight:
        800;
}


/* ==========================================================
   ROBOT / AI DECORATION
   ========================================================== */

.ai-decoration {

    position:
        relative;

    height:
        78px;

    overflow:
        hidden;

    margin-top:
        4px;

    border-radius:
        10px;

    background:
        linear-gradient(
            135deg,
            #eef6ff,
            #e5f1ff
        );
}


.ai-robot {

    position:
        absolute;

    right:
        18px;

    bottom:
        8px;

    width:
        50px;

    height:
        42px;

    border-radius:
        14px;

    background:
        linear-gradient(
            145deg,
            #8ab9ff,
            #1769ff
        );

    box-shadow:
        0 10px 22px
        rgba(23,105,255,.2);

    animation:
        robotFloat 3s ease-in-out infinite;
}


.ai-robot:before {

    content:
        "";

    position:
        absolute;

    width:
        5px;

    height:
        5px;

    border-radius:
        50%;

    background:
        white;

    left:
        13px;

    top:
        15px;

    box-shadow:
        19px 0 0 white;
}


.ai-robot:after {

    content:
        "";

    position:
        absolute;

    width:
        16px;

    height:
        3px;

    border-radius:
        5px;

    background:
        rgba(255,255,255,.8);

    left:
        17px;

    bottom:
        8px;
}


.ai-message {

    position:
        absolute;

    left:
        14px;

    top:
        25px;

    color:
        #1769ff;

    font-size:
        9px;

    font-weight:
        800;

    animation:
        messageFloat 3s ease-in-out infinite;
}


/* ==========================================================
   RECENT TRANSACTIONS
   ========================================================== */

.transactions-panel {

    margin-top:
        14px;
}


.transaction-table {

    width:
        100%;

    border-collapse:
        collapse;
}


.transaction-table th {

    padding:
        11px 13px;

    text-align:
        left;

    color:
        #7186aa;

    background:
        #f8fbff;

    font-size:
        8px;

    font-weight:
        800;
}


.transaction-table td {

    padding:
        11px 13px;

    border-top:
        1px solid #edf2fa;

    color:
        #2d4b79;

    font-size:
        9px;
}


.transaction-table tr {

    transition:
        background .2s ease;
}


.transaction-table tbody tr:hover {

    background:
        #f7fbff;
}


.category-pill {

    display:
        inline-flex;

    padding:
        4px 8px;

    border-radius:
        999px;

    background:
        #edf5ff;

    color:
        #1769ff;

    font-size:
        8px;

    font-weight:
        800;
}


.transaction-amount {

    color:
        #15376e;

    font-weight:
        800;
}


/* ==========================================================
   QUICK SUMMARY
   ========================================================== */

.summary-panel {

    margin-top:
        14px;
}


.summary-body {

    padding:
        16px;
}


.summary-line {

    display:
        flex;

    align-items:
        center;

    gap:
        10px;

    color:
        #3e5b84;

    font-size:
        10px;

    line-height:
        1.6;
}


.summary-icon {

    width:
        36px;

    height:
        36px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    flex:
        0 0 36px;

    border-radius:
        50%;

    background:
        #eef6ff;

    color:
        #1769ff;

    font-weight:
        900;
}


.progress {

    margin-top:
        14px;

    height:
        7px;

    overflow:
        hidden;

    border-radius:
        999px;

    background:
        #e8f0fb;
}


.progress-value {

    height:
        100%;

    width:
        var(--progress);

    border-radius:
        999px;

    background:
        linear-gradient(
            90deg,
            #1769ff,
            #54b8ff
        );

    transform:
        scaleX(0);

    transform-origin:
        left;

    animation:
        progressGrow 1.2s .4s forwards;
}


/* ==========================================================
   FORM
   ========================================================== */

.form-card {

    padding:
        22px;

    border:
        1px solid var(--border);

    border-radius:
        14px;

    background:
        white;

    box-shadow:
        var(--shadow);

    animation:
        cardEnter .7s both;
}


/* ==========================================================
   ANIMATIONS
   ========================================================== */

@keyframes fadeDown {

    from {
        opacity: 0;
        transform: translateY(-15px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(18px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


@keyframes cardEnter {

    from {
        opacity: 0;
        transform:
            translateY(20px)
            scale(.985);
    }

    to {
        opacity: 1;
        transform:
            translateY(0)
            scale(1);
    }
}


@keyframes iconPop {

    0% {
        opacity: 0;
        transform: scale(.55) rotate(-10deg);
    }

    70% {
        transform: scale(1.08) rotate(2deg);
    }

    100% {
        opacity: 1;
        transform: scale(1) rotate(0);
    }
}


@keyframes logoFloat {

    0%, 100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-5px);
    }
}


@keyframes handWave {

    0%, 100% {
        transform: rotate(0);
    }

    10% {
        transform: rotate(14deg);
    }

    20% {
        transform: rotate(-9deg);
    }

    30% {
        transform: rotate(12deg);
    }

    40% {
        transform: rotate(0);
    }
}


@keyframes waveMove {

    0%, 100% {
        transform:
            translateX(0)
            rotate(-4deg);
    }

    50% {
        transform:
            translateX(18px)
            rotate(-2deg);
    }
}


@keyframes barGrow {

    from {
        transform: scaleY(0);
    }

    to {
        transform: scaleY(1);
    }
}


@keyframes textAppear {

    from {
        opacity: 0;
        transform: translateY(5px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


@keyframes donutDraw {

    from {
        stroke-dashoffset:
            var(--circ);
    }

    to {
        stroke-dashoffset:
            var(--offset);
    }
}


@keyframes insightSlide {

    from {
        opacity: 0;
        transform:
            translateX(20px);
    }

    to {
        opacity: 1;
        transform:
            translateX(0);
    }
}


@keyframes robotFloat {

    0%, 100% {
        transform:
            translateY(0);
    }

    50% {
        transform:
            translateY(-7px);
    }
}


@keyframes messageFloat {

    0%, 100% {
        transform:
            translateY(0);
    }

    50% {
        transform:
            translateY(-3px);
    }
}


@keyframes progressGrow {

    from {
        transform: scaleX(0);
    }

    to {
        transform: scaleX(1);
    }
}


/* ==========================================================
   STREAMLIT WIDGET POLISH
   ========================================================== */

.stButton > button {

    border-radius:
        10px !important;

    min-height:
        42px !important;
}


.stTextInput input,
.stNumberInput input {

    border-radius:
        10px !important;
}


div[data-baseweb="select"] > div {

    border-radius:
        10px !important;
}


[data-testid="stDataFrame"] {

    border-radius:
        12px;

    overflow:
        hidden;
}


/* ==========================================================
   LAPTOP RESPONSIVE
   ========================================================== */

@media screen and (max-width: 1450px) {

    [data-testid="stSidebar"] {

        width:
            235px !important;

        min-width:
            235px !important;
    }

    .metric-grid {

        gap:
            10px;
    }

    .metric-card {

        padding:
            15px;
    }

    .metric-value {

        font-size:
            20px;
    }

    .dashboard-grid {

        grid-template-columns:
            minmax(0, 1.7fr)
            minmax(255px, .72fr);
    }

    .donut-svg {

        width:
            160px;

        height:
            160px;

        flex-basis:
            160px;
    }

    .legend {

        min-width:
            120px;
    }
}


/* ==========================================================
   SMALL LAPTOP
   ========================================================== */

@media screen and (max-width: 1200px) {

    .dashboard-grid {

        grid-template-columns:
            1fr;
    }

    .right-column {

        display:
            grid;

        grid-template-columns:
            1fr 1fr;

        gap:
            14px;
    }

    .transactions-panel {

        margin-top:
            0;
    }

    .metric-grid {

        grid-template-columns:
            repeat(2,1fr);
    }

    .filter-panel {

        flex-wrap:
            wrap;
    }
}


/* ==========================================================
   TABLET / SMALL WINDOW
   ========================================================== */

@media screen and (max-width: 850px) {

    [data-testid="stSidebar"] {

        width:
            210px !important;

        min-width:
            210px !important;
    }

    .right-column {

        grid-template-columns:
            1fr;
    }

    .metric-grid {

        grid-template-columns:
            repeat(2,1fr);
    }

    .header-right {

        display:
            none;
    }

    .greeting-title {

        font-size:
            18px;
    }

    .greeting-sub {

        font-size:
            9px;
    }

    .chart-area {

        gap:
            10px;
    }
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media screen and (max-width: 600px) {

    [data-testid="stSidebar"] {

        width:
            190px !important;

        min-width:
            190px !important;
    }

    .block-container {

        padding:
            10px !important;
    }

    .metric-grid {

        grid-template-columns:
            1fr;
    }

    .dashboard-grid {

        grid-template-columns:
            1fr;
    }

    .right-column {

        display:
            block;
    }

    .chart-area {

        height:
            210px;

        gap:
            5px;
    }

    .bar-shape {

        width:
            35px;
    }

    .donut-area {

        flex-direction:
            column;
    }

    .filter-panel {

        display:
            block;
    }

    .filter-button {

        width:
            100%;

        margin-bottom:
            8px;
    }

    .top-header {

        margin-bottom:
            12px;
    }

    .greeting-icon {

        width:
            40px;

        height:
            40px;

        font-size:
            20px;
    }

    .greeting-title {

        font-size:
            16px;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

render(
    """
    <div class="brand">

        <div class="brand-logo">
            EA
        </div>

        <div>

            <div class="brand-name">
                ExpenseAI
            </div>

            <div class="brand-sub">
                SMARTER SPENDING. BETTER TOMORROW.
            </div>

        </div>

    </div>
    """
)


page = st.sidebar.radio(
    "WORKSPACE",
    [
        "Dashboard",
        "Add Expense",
        "Transactions",
        "Analytics",
        "Insights"
    ],
    label_visibility="visible"
)


render(
    """
    <div class="sidebar-bottom">

        <div class="sidebar-bottom-title">
            Smart choices today,
            bigger dreams tomorrow.
        </div>

        <div style="
            position:absolute;
            right:20px;
            bottom:50px;
            color:#20a9ff;
            font-size:28px;
            font-weight:900;
        ">
            ↗
        </div>

        <div class="sidebar-wave"></div>

    </div>
    """
)


if st.sidebar.button(
    "Replay Animations",
    use_container_width=True
):

    st.rerun()


# ============================================================
# TOP HEADER
# ============================================================

today = date.today()

formatted_today = today.strftime(
    "%a, %d %b %Y"
)


render(
    f"""
    <div class="top-header">

        <div class="greeting">

            <div class="greeting-icon">
                👋
            </div>

            <div>

                <div class="greeting-title">
                    Good Morning, Josh!
                </div>

                <div class="greeting-sub">
                    Here's what's happening with your expenses today.
                </div>

            </div>

        </div>


        <div class="header-right">

            <div class="date-pill">

                <span style="
                    color:#1769ff;
                    font-size:14px;
                ">
                    ▣
                </span>

                {formatted_today}

            </div>

            <div class="profile-circle">
                J
            </div>

            <div style="
                color:#1769ff;
                font-size:12px;
            ">
                ⌄
            </div>

        </div>

    </div>
    """
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    # --------------------------------------------------------
    # FILTER PANEL
    # --------------------------------------------------------

    filter_left, filter_date, filter_cat, filter_pay, filter_search, filter_clear = st.columns(
        [1.15, 1.35, 1.05, 1.05, 1.15, .55],
        gap="small"
    )


    with filter_left:

        if st.button(
            "＋  Add New Expense",
            use_container_width=True
        ):

            st.session_state["go_add"] = True


    with filter_date:

        date_range = st.date_input(
            "Date Range",
            value=(
                today.replace(day=1),
                today
            ),
            label_visibility="visible"
        )


    with filter_cat:

        category_filter = st.selectbox(
            "Category",
            ["All Categories"]
            + sorted(
                df["CATEGORY"]
                .unique()
                .tolist()
            )
            if not df.empty
            else ["All Categories"]
        )


    with filter_pay:

        payment_filter = st.selectbox(
            "Payment Method",
            ["All Methods"]
            + sorted(
                df["PAYMENTMETHOD"]
                .unique()
                .tolist()
            )
            if not df.empty
            else ["All Methods"]
        )


    with filter_search:

        search_filter = st.text_input(
            "Search description...",
            label_visibility="visible"
        )


    with filter_clear:

        if st.button(
            "Clear",
            use_container_width=True
        ):

            st.rerun()


    # --------------------------------------------------------
    # FILTER DATA
    # --------------------------------------------------------

    filtered_df = df.copy()


    if not filtered_df.empty:

        if isinstance(
            date_range,
            tuple
        ) and len(date_range) == 2:

            start_date = pd.Timestamp(
                date_range[0]
            )

            end_date = (
                pd.Timestamp(
                    date_range[1]
                )
                + pd.Timedelta(days=1)
            )

            filtered_df = filtered_df[
                (
                    filtered_df["EXPENSEDATE"]
                    >= start_date
                )
                &
                (
                    filtered_df["EXPENSEDATE"]
                    < end_date
                )
            ]


        if category_filter != "All Categories":

            filtered_df = filtered_df[
                filtered_df["CATEGORY"]
                == category_filter
            ]


        if payment_filter != "All Methods":

            filtered_df = filtered_df[
                filtered_df["PAYMENTMETHOD"]
                == payment_filter
            ]


        if search_filter.strip():

            filtered_df = filtered_df[
                filtered_df[
                    "DESCRIPTIONTYPE"
                ]
                .str.contains(
                    search_filter,
                    case=False,
                    na=False
                )
            ]


    # --------------------------------------------------------
    # FILTERED METRICS
    # --------------------------------------------------------

    if filtered_df.empty:

        dash_total = 0
        dash_count = 0
        dash_average = 0
        dash_category = "None"

        dash_categories = pd.Series(
            dtype=float
        )

        dash_payments = pd.Series(
            dtype=float
        )

    else:

        dash_total = float(
            filtered_df["AMOUNT"].sum()
        )

        dash_count = len(
            filtered_df
        )

        dash_average = float(
            filtered_df["AMOUNT"].mean()
        )

        dash_categories = (
            filtered_df
            .groupby("CATEGORY")["AMOUNT"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        dash_payments = (
            filtered_df
            .groupby("PAYMENTMETHOD")["AMOUNT"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        dash_category = (
            dash_categories.index[0]
            if not dash_categories.empty
            else "None"
        )


    # --------------------------------------------------------
    # METRIC CARDS
    # --------------------------------------------------------

    top_amount = (
        float(
            dash_categories.iloc[0]
        )
        if not dash_categories.empty
        else 0
    )


    top_share = (
        top_amount / dash_total * 100
        if dash_total > 0
        else 0
    )


    render(
        f"""
        <div class="metric-grid">

            <div
                class="metric-card"
                style="
                    --accent:#19c47d;
                    --delay:.05s;
                "
            >

                <div class="metric-icon">
                    Rs
                </div>

                <div class="metric-content">

                    <div class="metric-label">
                        Total Expense
                    </div>

                    <div class="metric-value">
                        {money(dash_total)}
                    </div>

                    <div class="metric-small">
                        <strong>↑ Live</strong>
                        &nbsp; current filtered period
                    </div>

                </div>

            </div>


            <div
                class="metric-card"
                style="
                    --accent:#7359f5;
                    --delay:.12s;
                "
            >

                <div class="metric-icon">
                    =
                </div>

                <div class="metric-content">

                    <div class="metric-label">
                        Transactions
                    </div>

                    <div class="metric-value">
                        {dash_count}
                    </div>

                    <div class="metric-small">
                        <strong>↑ Active</strong>
                        &nbsp; recorded transactions
                    </div>

                </div>

            </div>


            <div
                class="metric-card"
                style="
                    --accent:#278cff;
                    --delay:.19s;
                "
            >

                <div class="metric-icon">
                    #
                </div>

                <div class="metric-content">

                    <div class="metric-label">
                        Average Expense
                    </div>

                    <div class="metric-value">
                        {money(dash_average)}
                    </div>

                    <div class="metric-small">
                        <strong>↑ 8%</strong>
                        &nbsp; spending metric
                    </div>

                </div>

            </div>


            <div
                class="metric-card"
                style="
                    --accent:#e64fb5;
                    --delay:.26s;
                "
            >

                <div class="metric-icon">
                    *
                </div>

                <div class="metric-content">

                    <div class="metric-label">
                        Top Category
                    </div>

                    <div class="metric-value">
                        {escape(str(dash_category))}
                    </div>

                    <div class="metric-small">
                        <strong>{top_share:.0f}%</strong>
                        of total spending
                    </div>

                </div>

            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # MAIN DASHBOARD GRID
    # --------------------------------------------------------

    render(
        """
        <div style="
            height:2px;
            margin-bottom:12px;
        "></div>
        """
    )


    left_col, right_col = st.columns(
        [1.75, .72],
        gap="small"
    )


    # ========================================================
    # LEFT SIDE
    # ========================================================

    with left_col:

        # ----------------------------------------------------
        # CHART ROW
        # ----------------------------------------------------

        chart_col, payment_col = st.columns(
            [1.3, .95],
            gap="small"
        )


        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        with chart_col:

            max_bar = (
                float(
                    dash_categories.max()
                )
                if not dash_categories.empty
                else 1
            )

            bars = ""


            colors = [
                "#338df7",
                "#4c8cf4",
                "#3f83ee",
                "#3982e8",
                "#5a9bf8",
                "#66b0ff"
            ]


            for i, (
                category,
                amount
            ) in enumerate(
                dash_categories.items()
            ):

                height = (
                    amount
                    / max_bar
                    * 74
                    if max_bar > 0
                    else 5
                )

                height = max(
                    height,
                    6
                )


                bars += f"""
                <div class="bar-column">

                    <div
                        class="bar-value"
                        style="
                            --delay:
                            {i * .12 + .2:.2f}s;
                        "
                    >
                        {money(amount)}
                    </div>

                    <div
                        class="bar-shape"
                        style="
                            --height:
                            {height:.2f}%;
                            --delay:
                            {i * .12 + .15:.2f}s;
                            background:
                            linear-gradient(
                                180deg,
                                {colors[i % len(colors)]},
                                #397ce3
                            );
                        "
                    ></div>

                    <div class="bar-label">
                        {escape(str(category))}
                    </div>

                </div>
                """


            render(
                f"""
                <div class="panel">

                    <div class="panel-header">

                        <div class="panel-title-wrap">

                            <div class="panel-icon">
                                ▥
                            </div>

                            <div>

                                <div class="panel-title">
                                    Spending by Category
                                </div>

                                <div class="panel-subtitle">
                                    Category-wise expense distribution
                                </div>

                            </div>

                        </div>

                        <div style="
                            padding:7px 12px;
                            border:1px solid #e1eafb;
                            border-radius:9px;
                            color:#385681;
                            background:#fff;
                            font-size:9px;
                            font-weight:700;
                        ">
                            Amount
                            <span style="
                                margin-left:8px;
                                color:#1769ff;
                            ">
                                ▾
                            </span>
                        </div>

                    </div>

                    <div class="bar-chart">

                        <div class="chart-area">

                            {bars}

                        </div>

                    </div>

                </div>
                """
            )


        # ----------------------------------------------------
        # DONUT CHART
        # ----------------------------------------------------

        with payment_col:

            if dash_payments.empty:

                donut_svg = ""

                payment_legend = """
                <div style="
                    color:#8b9bb5;
                    font-size:10px;
                ">
                    No payment data
                </div>
                """

            else:

                donut_colors = [
                    "#1769ff",
                    "#7157ef",
                    "#21bfd0",
                    "#58b8f8",
                    "#e84fb5",
                    "#ff9c43"
                ]

                radius = 65

                circumference = (
                    2 * math.pi * radius
                )

                cumulative = 0

                donut_svg = ""

                payment_legend = ""


                for i, (
                    method,
                    amount
                ) in enumerate(
                    dash_payments.items()
                ):

                    fraction = (
                        float(amount)
                        / dash_total
                        if dash_total > 0
                        else 0
                    )

                    dash = (
                        fraction
                        * circumference
                    )

                    offset = (
                        -cumulative
                    )

                    color = (
                        donut_colors[
                            i % len(donut_colors)
                        ]
                    )


                    donut_svg += f"""
                    <circle
                        class="donut-piece"
                        cx="100"
                        cy="100"
                        r="{radius}"
                        stroke="{color}"
                        style="
                            --dash:
                            {dash:.2f}px
                            {circumference:.2f}px;

                            --circ:
                            {circumference:.2f}px;

                            --offset:
                            {offset:.2f}px;

                            --delay:
                            {i * .12:.2f}s;
                        "
                    ></circle>
                    """


                    percent = (
                        fraction
                        * 100
                    )


                    payment_legend += f"""
                    <div class="legend-row">

                        <div
                            class="legend-dot"
                            style="
                                background:
                                {color};
                            "
                        ></div>

                        <div class="legend-name">
                            {escape(str(method))}
                        </div>

                        <div class="legend-percent">
                            {percent:.0f}%
                        </div>

                        <div class="legend-amount">
                            {money(amount)}
                        </div>

                    </div>
                    """


                    cumulative += dash


            render(
                f"""
                <div class="panel">

                    <div class="panel-header">

                        <div class="panel-title-wrap">

                            <div class="panel-icon">
                                ▤
                            </div>

                            <div>

                                <div class="panel-title">
                                    Spending by Payment Method
                                </div>

                                <div class="panel-subtitle">
                                    Payment distribution
                                </div>

                            </div>

                        </div>

                    </div>

                    <div class="donut-area">

                        <svg
                            class="donut-svg"
                            viewBox="0 0 200 200"
                        >

                            <circle
                                class="donut-base"
                                cx="100"
                                cy="100"
                                r="{radius}"
                            ></circle>

                            <g
                                transform="
                                    rotate(-90 100 100)
                                "
                            >

                                {donut_svg}

                            </g>

                            <text
                                x="100"
                                y="97"
                                text-anchor="middle"
                                class="donut-center-value"
                            >
                                {money(dash_total)}
                            </text>

                            <text
                                x="100"
                                y="113"
                                text-anchor="middle"
                                class="donut-center-label"
                            >
                                Total
                            </text>

                        </svg>


                        <div class="legend">

                            {payment_legend}

                        </div>

                    </div>

                </div>
                """
            )


        # ----------------------------------------------------
        # RECENT TRANSACTIONS
        # ----------------------------------------------------

        transaction_rows = ""


        for _, row in filtered_df.head(6).iterrows():

            expense_date = ""

            if pd.notna(
                row["EXPENSEDATE"]
            ):

                expense_date = (
                    pd.to_datetime(
                        row["EXPENSEDATE"]
                    )
                    .strftime(
                        "%d %b %Y"
                    )
                )


            transaction_rows += f"""
            <tr>

                <td>
                    {expense_date}
                </td>

                <td>
                    {escape(
                        str(
                            row["DESCRIPTIONTYPE"]
                        )
                    )}
                </td>

                <td>

                    <span class="category-pill">
                        {escape(
                            str(
                                row["CATEGORY"]
                            )
                        )}
                    </span>

                </td>

                <td>
                    {escape(
                        str(
                            row["PAYMENTMETHOD"]
                        )
                    )}
                </td>

                <td class="transaction-amount">
                    {money(row["AMOUNT"])}
                </td>

            </tr>
            """


        if not transaction_rows:

            transaction_rows = """
            <tr>

                <td
                    colspan="5"
                    style="
                        text-align:center;
                        padding:35px;
                        color:#8191aa;
                    "
                >
                    No transactions found
                </td>

            </tr>
            """


        render(
            f"""
            <div class="panel transactions-panel">

                <div class="panel-header">

                    <div class="panel-title-wrap">

                        <div class="panel-icon">
                            ▣
                        </div>

                        <div>

                            <div class="panel-title">
                                Recent Transactions
                            </div>

                            <div class="panel-subtitle">
                                Latest expense activity
                            </div>

                        </div>

                    </div>

                    <div style="
                        padding:7px 12px;
                        border:1px solid #dce8fa;
                        border-radius:9px;
                        color:#1769ff;
                        font-size:9px;
                        font-weight:700;
                    ">
                        View All →
                    </div>

                </div>


                <table class="transaction-table">

                    <thead>

                        <tr>

                            <th>
                                Date
                            </th>

                            <th>
                                Description
                            </th>

                            <th>
                                Category
                            </th>

                            <th>
                                Payment Method
                            </th>

                            <th>
                                Amount
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {transaction_rows}

                    </tbody>

                </table>

            </div>
            """
        )


    # ========================================================
    # RIGHT SIDE
    # ========================================================

    with right_col:

        top_category_amount = (
            float(
                dash_categories.iloc[0]
            )
            if not dash_categories.empty
            else 0
        )


        top_category_percent = (
            top_category_amount
            / dash_total
            * 100
            if dash_total > 0
            else 0
        )


        render(
            f"""
            <div class="panel insights-panel">

                <div class="panel-header">

                    <div class="panel-title-wrap">

                        <div class="panel-icon">
                            *
                        </div>

                        <div>

                            <div class="panel-title">
                                AI Insights
                            </div>

                            <div class="panel-subtitle">
                                Smart spending observations
                            </div>

                        </div>

                    </div>

                    <div style="
                        padding:6px 10px;
                        border-radius:15px;
                        color:#1769ff;
                        background:#eaf3ff;
                        font-size:8px;
                        font-weight:800;
                    ">
                        Smart
                    </div>

                </div>


                <div class="insight-item"
                     style="--delay:.1s;">

                    <div class="insight-icon">
                        Rs
                    </div>

                    <div class="insight-text">

                        You spent the most on
                        <strong>
                            {escape(str(dash_category))}
                        </strong>
                        ({top_category_percent:.0f}%
                        of your total expenses).

                    </div>

                </div>


                <div class="insight-item"
                     style="--delay:.18s;">

                    <div
                        class="insight-icon"
                        style="
                            background:#e9fbf7;
                            color:#13ad79;
                        "
                    >
                        ↗
                    </div>

                    <div class="insight-text">

                        Your current spending dashboard
                        contains
                        <strong>
                            {dash_count}
                        </strong>
                        recorded transactions.

                    </div>

                </div>


                <div class="insight-item"
                     style="--delay:.26s;">

                    <div
                        class="insight-icon"
                        style="
                            background:#f0edff;
                            color:#7359f5;
                        "
                    >
                        #
                    </div>

                    <div class="insight-text">

                        Your average transaction value
                        is
                        <strong>
                            {money(dash_average)}
                        </strong>.

                    </div>

                </div>


                <div class="insight-item"
                     style="--delay:.34s;">

                    <div
                        class="insight-icon"
                        style="
                            background:#e9f7ff;
                            color:#087bdc;
                        "
                    >
                        +
                    </div>

                    <div class="insight-text">

                        Keep adding expenses to make
                        your spending analytics more
                        detailed.

                    </div>

                </div>


                <div class="ai-decoration">

                    <div class="ai-message">
                        Keep going!
                    </div>

                    <div class="ai-robot"></div>

                </div>

            </div>
            """
        )


        # ----------------------------------------------------
        # QUICK SUMMARY
        # ----------------------------------------------------

        summary_percent = min(
            top_category_percent,
            100
        )


        render(
            f"""
            <div class="panel summary-panel">

                <div class="panel-header">

                    <div class="panel-title-wrap">

                        <div class="panel-icon">
                            !
                        </div>

                        <div>

                            <div class="panel-title">
                                Quick Summary
                            </div>

                        </div>

                    </div>

                </div>


                <div class="summary-body">

                    <div class="summary-line">

                        <div class="summary-icon">
                            Rs
                        </div>

                        <div>

                            You spent
                            <strong>
                                {money(top_category_amount)}
                            </strong>
                            on
                            <strong>
                                {escape(str(dash_category))}
                            </strong>
                            this period.

                        </div>

                    </div>


                    <div class="progress">

                        <div
                            class="progress-value"
                            style="
                                --progress:
                                {summary_percent:.2f}%;
                            "
                        ></div>

                    </div>


                    <div style="
                        margin-top:7px;
                        color:#7488aa;
                        font-size:8px;
                    ">
                        {top_category_percent:.0f}%
                        of total spending
                    </div>

                </div>

            </div>
            """
        )


# ============================================================
# GO TO ADD EXPENSE
# ============================================================

if page == "Dashboard" and st.session_state.get(
    "go_add",
    False
):

    st.session_state["go_add"] = False

    st.rerun()


# ============================================================
# ADD EXPENSE PAGE
# ============================================================

elif page == "Add Expense":

    render(
        """
        <div style="
            margin-bottom:20px;
            animation:fadeUp .6s both;
        ">

            <div style="
                color:#092d6c;
                font-size:25px;
                font-weight:900;
            ">
                Add New Expense
            </div>

            <div style="
                margin-top:5px;
                color:#7b8eac;
                font-size:11px;
            ">
                Add a transaction directly to your ExpenseAI database.
            </div>

        </div>
        """
    )


    with st.form(
        "add_expense_form"
    ):

        st.markdown(
            '<div class="form-card">',
            unsafe_allow_html=True
        )


        c1, c2 = st.columns(
            2,
            gap="large"
        )


        with c1:

            expense_date = st.date_input(
                "Expense Date",
                value=date.today()
            )

            category = st.selectbox(
                "Category",
                [
                    "Food",
                    "Transport",
                    "Entertainment",
                    "Shopping",
                    "Education",
                    "Bills",
                    "Health",
                    "Other"
                ]
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "UPI",
                    "Cash",
                    "Credit Card",
                    "Debit Card",
                    "Net Banking",
                    "Bank Transfer",
                    "Other"
                ]
            )


        with c2:

            amount = st.number_input(
                "Amount",
                min_value=0.01,
                value=250.00,
                step=50.00,
                format="%.2f"
            )

            description = st.text_input(
                "Description",
                placeholder="Example: Bought biryani"
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


        submitted = st.form_submit_button(
            "Save Expense",
            use_container_width=True
        )


    if submitted:

        if not description.strip():

            st.error(
                "Please enter a description."
            )

        elif amount <= 0:

            st.error(
                "Amount must be greater than zero."
            )

        else:

            try:

                insert_expense(
                    expense_date,
                    category,
                    description.strip(),
                    amount,
                    payment_method
                )

                st.success(
                    "Expense added successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "Unable to save expense."
                )

                st.code(
                    str(e)
                )


# ============================================================
# TRANSACTIONS PAGE
# ============================================================

elif page == "Transactions":

    render(
        """
        <div style="
            margin-bottom:20px;
            animation:fadeUp .6s both;
        ">

            <div style="
                color:#092d6c;
                font-size:25px;
                font-weight:900;
            ">
                Transactions
            </div>

            <div style="
                margin-top:5px;
                color:#7b8eac;
                font-size:11px;
            ">
                Search, filter and review every recorded expense.
            </div>

        </div>
        """
    )


    if df.empty:

        st.info(
            "No transactions available."
        )

    else:

        c1, c2, c3 = st.columns(3)


        with c1:

            transaction_category = st.selectbox(
                "Category",
                ["All"]
                + sorted(
                    df["CATEGORY"]
                    .unique()
                    .tolist()
                )
            )


        with c2:

            transaction_payment = st.selectbox(
                "Payment Method",
                ["All"]
                + sorted(
                    df["PAYMENTMETHOD"]
                    .unique()
                    .tolist()
                )
            )


        with c3:

            transaction_search = st.text_input(
                "Search"
            )


        transactions = df.copy()


        if transaction_category != "All":

            transactions = transactions[
                transactions["CATEGORY"]
                == transaction_category
            ]


        if transaction_payment != "All":

            transactions = transactions[
                transactions["PAYMENTMETHOD"]
                == transaction_payment
            ]


        if transaction_search.strip():

            transactions = transactions[
                transactions[
                    "DESCRIPTIONTYPE"
                ]
                .str.contains(
                    transaction_search,
                    case=False,
                    na=False
                )
            ]


        display_df = transactions.copy()


        if not display_df.empty:

            display_df["EXPENSEDATE"] = (
                display_df["EXPENSEDATE"]
                .dt.strftime(
                    "%d %b %Y"
                )
            )

            display_df["AMOUNT"] = (
                display_df["AMOUNT"]
                .apply(money)
            )


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ANALYTICS PAGE
# ============================================================

elif page == "Analytics":

    render(
        """
        <div style="
            margin-bottom:20px;
            animation:fadeUp .6s both;
        ">

            <div style="
                color:#092d6c;
                font-size:25px;
                font-weight:900;
            ">
                Analytics
            </div>

            <div style="
                margin-top:5px;
                color:#7b8eac;
                font-size:11px;
            ">
                Explore your spending patterns through interactive visualizations.
            </div>

        </div>
        """
    )


    if df.empty:

        st.info(
            "Add expenses to generate analytics."
        )

    else:

        analytics_category = (
            df.groupby("CATEGORY")["AMOUNT"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        analytics_payment = (
            df.groupby("PAYMENTMETHOD")["AMOUNT"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        a, b = st.columns(
            2,
            gap="small"
        )


        with a:

            max_value = float(
                analytics_category.max()
            )

            analytics_bars = ""


            for i, (
                category,
                amount
            ) in enumerate(
                analytics_category.items()
            ):

                height = (
                    amount
                    / max_value
                    * 75
                )


                analytics_bars += f"""
                <div class="bar-column">

                    <div
                        class="bar-value"
                        style="
                            --delay:
                            {i*.1:.2f}s;
                        "
                    >
                        {money(amount)}
                    </div>

                    <div
                        class="bar-shape"
                        style="
                            --height:
                            {height:.2f}%;

                            --delay:
                            {i*.1:.15f}s;
                        "
                    ></div>

                    <div class="bar-label">
                        {escape(str(category))}
                    </div>

                </div>
                """


            render(
                f"""
                <div class="panel">

                    <div class="panel-header">

                        <div class="panel-title-wrap">

                            <div class="panel-icon">
                                ▥
                            </div>

                            <div class="panel-title">
                                Category Analytics
                            </div>

                        </div>

                    </div>

                    <div class="bar-chart">

                        <div class="chart-area">

                            {analytics_bars}

                        </div>

                    </div>

                </div>
                """
            )


        with b:

            analytics_total = float(
                analytics_category.sum()
            )

            radius = 65

            circumference = (
                2 * math.pi * radius
            )

            cumulative = 0

            svg = ""

            colors = [
                "#1769ff",
                "#7359f5",
                "#22b9d6",
                "#e94fba",
                "#ff9c43",
                "#43c88c"
            ]


            for i, (
                category,
                amount
            ) in enumerate(
                analytics_category.items()
            ):

                fraction = (
                    amount
                    / analytics_total
                )

                dash = (
                    fraction
                    * circumference
                )

                offset = -cumulative


                svg += f"""
                <circle
                    class="donut-piece"
                    cx="100"
                    cy="100"
                    r="{radius}"
                    stroke="{colors[i % len(colors)]}"
                    style="
                        --dash:
                        {dash:.2f}px
                        {circumference:.2f}px;

                        --circ:
                        {circumference:.2f}px;

                        --offset:
                        {offset:.2f}px;

                        --delay:
                        {i*.12:.2f}s;
                    "
                ></circle>
                """


                cumulative += dash


            render(
                f"""
                <div class="panel">

                    <div class="panel-header">

                        <div class="panel-title-wrap">

                            <div class="panel-icon">
                                ◉
                            </div>

                            <div class="panel-title">
                                Category Distribution
                            </div>

                        </div>

                    </div>

                    <div class="donut-area">

                        <svg
                            class="donut-svg"
                            viewBox="0 0 200 200"
                        >

                            <circle
                                class="donut-base"
                                cx="100"
                                cy="100"
                                r="{radius}"
                            ></circle>

                            <g
                                transform="
                                    rotate(-90 100 100)
                                "
                            >
                                {svg}
                            </g>

                            <text
                                x="100"
                                y="98"
                                text-anchor="middle"
                                class="donut-center-value"
                            >
                                {money(analytics_total)}
                            </text>

                            <text
                                x="100"
                                y="114"
                                text-anchor="middle"
                                class="donut-center-label"
                            >
                                Total
                            </text>

                        </svg>

                    </div>

                </div>
                """
            )


# ============================================================
# INSIGHTS PAGE
# ============================================================

elif page == "Insights":

    render(
        """
        <div style="
            margin-bottom:20px;
            animation:fadeUp .6s both;
        ">

            <div style="
                color:#092d6c;
                font-size:25px;
                font-weight:900;
            ">
                AI Insights
            </div>

            <div style="
                margin-top:5px;
                color:#7b8eac;
                font-size:11px;
            ">
                Intelligent observations generated from your expense data.
            </div>

        </div>
        """
    )


    if df.empty:

        st.info(
            "Add expenses to generate insights."
        )

    else:

        top_category_amount = float(
            category_totals.iloc[0]
        )

        top_category_share = (
            top_category_amount
            / total_expense
            * 100
        )

        largest_row = df.loc[
            df["AMOUNT"].idxmax()
        ]

        largest_amount = float(
            largest_row["AMOUNT"]
        )

        largest_description = (
            str(
                largest_row[
                    "DESCRIPTIONTYPE"
                ]
            )
        )

        largest_category = (
            str(
                largest_row[
                    "CATEGORY"
                ]
            )
        )

        top_payment = (
            payment_totals.index[0]
            if not payment_totals.empty
            else "None"
        )


        render(
            f"""
            <div class="metric-grid">

                <div
                    class="metric-card"
                    style="
                        --accent:#1769ff;
                        --delay:.05s;
                    "
                >

                    <div class="metric-icon">
                        AI
                    </div>

                    <div class="metric-content">

                        <div class="metric-label">
                            Top Category
                        </div>

                        <div class="metric-value">
                            {escape(top_category)}
                        </div>

                        <div class="metric-small">
                            <strong>
                                {top_category_share:.0f}%
                            </strong>
                            of spending
                        </div>

                    </div>

                </div>


                <div
                    class="metric-card"
                    style="
                        --accent:#e94fba;
                        --delay:.12s;
                    "
                >

                    <div class="metric-icon">
                        MAX
                    </div>

                    <div class="metric-content">

                        <div class="metric-label">
                            Largest Expense
                        </div>

                        <div class="metric-value">
                            {money(largest_amount)}
                        </div>

                        <div class="metric-small">
                            {escape(largest_description)}
                        </div>

                    </div>

                </div>


                <div
                    class="metric-card"
                    style="
                        --accent:#12b878;
                        --delay:.19s;
                    "
                >

                    <div class="metric-icon">
                        PM
                    </div>

                    <div class="metric-content">

                        <div class="metric-label">
                            Main Payment
                        </div>

                        <div class="metric-value">
                            {escape(top_payment)}
                        </div>

                        <div class="metric-small">
                            Most used payment method
                        </div>

                    </div>

                </div>


                <div
                    class="metric-card"
                    style="
                        --accent:#7359f5;
                        --delay:.26s;
                    "
                >

                    <div class="metric-icon">
                        AVG
                    </div>

                    <div class="metric-content">

                        <div class="metric-label">
                            Average
                        </div>

                        <div class="metric-value">
                            {money(average_expense)}
                        </div>

                        <div class="metric-small">
                            Per transaction
                        </div>

                    </div>

                </div>

            </div>
            """
        )


        render(
            f"""
            <div class="panel">

                <div class="panel-header">

                    <div class="panel-title-wrap">

                        <div class="panel-icon">
                            AI
                        </div>

                        <div>

                            <div class="panel-title">
                                Smart Spending Observations
                            </div>

                            <div class="panel-subtitle">
                                Generated from your recorded transaction data
                            </div>

                        </div>

                    </div>

                </div>


                <div style="
                    padding:12px;
                ">

                    <div
                        class="insight-item"
                        style="--delay:.1s;"
                    >

                        <div class="insight-icon">
                            01
                        </div>

                        <div class="insight-text">

                            Your highest spending category is
                            <strong>
                                {escape(top_category)}
                            </strong>,
                            accounting for
                            <strong>
                                {top_category_share:.1f}%
                            </strong>
                            of recorded spending.

                        </div>

                    </div>


                    <div
                        class="insight-item"
                        style="--delay:.18s;"
                    >

                        <div class="insight-icon">
                            02
                        </div>

                        <div class="insight-text">

                            Your largest recorded transaction is
                            <strong>
                                {money(largest_amount)}
                            </strong>
                            for
                            <strong>
                                {escape(largest_description)}
                            </strong>
                            under
                            <strong>
                                {escape(largest_category)}
                            </strong>.

                        </div>

                    </div>


                    <div
                        class="insight-item"
                        style="--delay:.26s;"
                    >

                        <div class="insight-icon">
                            03
                        </div>

                        <div class="insight-text">

                            The payment method with the highest
                            recorded spending is
                            <strong>
                                {escape(top_payment)}
                            </strong>.

                        </div>

                    </div>

                </div>

            </div>
            """
        )
