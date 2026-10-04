import streamlit as st
import pyodbc
import pandas as pd
import math
from html import escape
from datetime import date

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="ET",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SQL SERVER CONNECTION
# ============================================================

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=JOSH\SQLEXPRESS01;"
    "DATABASE=EXPENSETRACKER;"
    "Trusted_Connection=yes;"
)


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)


def load_expenses():
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
        FROM EXPENSES
        ORDER BY EXPENSEDATE DESC, EXPENSEID DESC
        """

        data = pd.read_sql(query, connection)

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

    return data


def add_expense(expense_date, category, description, amount, payment):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO EXPENSES
        (
            EXPENSEDATE,
            CATEGORY,
            DESCRIPTIONTYPE,
            AMOUNT,
            PAYMENTMETHOD
        )
        VALUES (?, ?, ?, ?, ?)
        """

        cursor.execute(
            query,
            expense_date,
            category,
            description,
            amount,
            payment
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
            "DELETE FROM EXPENSES WHERE EXPENSEID = ?",
            expense_id
        )

        connection.commit()
        cursor.close()

    finally:
        connection.close()


# ============================================================
# GLOBAL CSS
# ============================================================

st.html("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap'
);

/* ==========================================================
   GLOBAL
   ========================================================== */

html,
body,
[data-testid="stAppViewContainer"] {

    font-family:
        Inter,
        Segoe UI,
        Arial,
        sans-serif !important;

}

[data-testid="stAppViewContainer"] {

    background:
        radial-gradient(
            circle at 85% 10%,
            rgba(23,105,255,0.08),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #f8fbff 0%,
            #eef5ff 100%
        );

}

[data-testid="stHeader"] {

    background:transparent !important;

}

[data-testid="stToolbar"] {

    background:transparent !important;

}

#MainMenu {

    visibility:hidden;

}

footer {

    visibility:hidden;

}


/* ==========================================================
   SIDEBAR
   ========================================================== */

[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #ffffff 0%,
            #f5f9ff 100%
        ) !important;

    border-right:
        1px solid #dce8fa !important;

}

[data-testid="stSidebar"] > div:first-child {

    padding-top:18px;

}

[data-testid="stSidebar"] [data-testid="stRadio"] {

    margin-top:5px;

}

[data-testid="stSidebar"] label {

    font-family:Inter,sans-serif !important;

}

[data-testid="stSidebar"] [role="radiogroup"] {

    gap:7px !important;

}

[data-testid="stSidebar"] [role="radiogroup"] label {

    border-radius:13px !important;

    padding:
        10px
        12px !important;

    transition:
        all 0.25s ease !important;

}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {

    background:#edf4ff !important;

    transform:
        translateX(3px);

}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {

    border-radius:12px !important;

    border:
        1px solid #d8e6fb !important;

    background:
        linear-gradient(
            135deg,
            #ffffff,
            #f3f7ff
        ) !important;

    color:#123b76 !important;

    font-weight:700 !important;

    transition:
        all 0.25s ease !important;

    box-shadow:
        0 5px 18px
        rgba(23,105,255,0.07) !important;

}

.stButton > button:hover {

    border-color:#1769ff !important;

    color:#1769ff !important;

    transform:
        translateY(-2px);

    box-shadow:
        0 10px 25px
        rgba(23,105,255,0.14) !important;

}


/* ==========================================================
   INPUTS
   ========================================================== */

[data-baseweb="input"],
[data-baseweb="select"],
[data-baseweb="textarea"] {

    border-radius:12px !important;

}


/* ==========================================================
   ANIMATIONS
   ========================================================== */

@keyframes fadeUp {

    0% {

        opacity:0;

        transform:
            translateY(22px);

    }

    100% {

        opacity:1;

        transform:
            translateY(0);

    }

}

@keyframes fadeIn {

    0% {

        opacity:0;

    }

    100% {

        opacity:1;

    }

}

@keyframes float {

    0%,100% {

        transform:
            translateY(0);

    }

    50% {

        transform:
            translateY(-9px);

    }

}

@keyframes pulse {

    0% {

        box-shadow:
            0 0 0 0
            rgba(32,189,117,0.35);

    }

    70% {

        box-shadow:
            0 0 0 8px
            rgba(32,189,117,0);

    }

    100% {

        box-shadow:
            0 0 0 0
            rgba(32,189,117,0);

    }

}

@keyframes barGrow {

    from {

        transform:
            scaleX(0);

    }

    to {

        transform:
            scaleX(1);

    }

}

@keyframes donutDraw {

    from {

        stroke-dashoffset:
            var(--start);

    }

    to {

        stroke-dashoffset:
            var(--end);

    }

}

@keyframes lineDraw {

    from {

        stroke-dashoffset:1;

    }

    to {

        stroke-dashoffset:0;

    }

}

@keyframes shimmer {

    0% {

        transform:
            translateX(-120%);

    }

    100% {

        transform:
            translateX(120%);

    }

}

</style>
""")


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_expenses()

except Exception as error:

    st.error(
        "Unable to connect to SQL Server. "
        "Please check your SQL Server connection."
    )

    st.stop()


# ============================================================
# DATA PREPARATION
# ============================================================

if df.empty:

    total_expense = 0
    transaction_count = 0
    average_expense = 0
    top_category = "No Data"

    category_totals = pd.Series(dtype=float)
    payment_totals = pd.Series(dtype=float)

else:

    total_expense = float(df["AMOUNT"].sum())

    transaction_count = int(len(df))

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

    if not category_totals.empty:

        top_category = category_totals.index[0]

    else:

        top_category = "No Data"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):

    return f"₹{float(value):,.2f}"


def safe_text(value):

    return escape(str(value))


def render_animated_bar_chart(series, title, badge="BAR", height=360):
    """Render a CSS-animated horizontal bar chart from a pandas Series."""
    if series is None or series.empty:
        st.info("No data available for this chart.")
        return

    series = series.sort_values(ascending=True)
    max_value = float(series.max()) if not series.empty else 0.0

    rows = ""

    for index, (label, value) in enumerate(series.items()):
        value = float(value)
        width = (value / max_value * 100.0) if max_value > 0 else 0.0

        rows += f"""
        <div class="animated-bar-row" style="animation-delay:{index * 0.08}s;">
            <div class="animated-bar-label">
                <span>{safe_text(label)}</span>
                <strong>{money(value)}</strong>
            </div>

            <div class="animated-bar-track">
                <div class="animated-bar-fill"
                     style="width:{width:.2f}%; animation-delay:{index * 0.12}s;">
                </div>
            </div>
        </div>
        """

    st.html(f"""
    <style>
        @keyframes expenseBarGrow {{
            from {{
                transform: scaleX(0);
                opacity: 0.25;
            }}
            to {{
                transform: scaleX(1);
                opacity: 1;
            }}
        }}

        @keyframes expenseRowIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .animated-bar-card {{
            min-height:{height}px;
            padding:26px;
            border-radius:20px;
            background:#ffffff;
            border:1px solid #dce9fa;
            box-shadow:0 12px 35px rgba(23,105,255,0.07);
            animation:fadeUp 0.65s ease-out;
        }}

        .animated-bar-title {{
            display:flex;
            align-items:center;
            gap:12px;
            margin-bottom:28px;
            color:#092f6d;
            font-size:18px;
            font-weight:850;
        }}

        .animated-bar-badge {{
            width:36px;
            height:36px;
            border-radius:11px;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#1769ff;
            background:#edf4ff;
            font-size:10px;
            font-weight:900;
        }}

        .animated-bar-row {{
            margin-bottom:19px;
            animation:expenseRowIn 0.55s ease-out both;
        }}

        .animated-bar-label {{
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:8px;
            color:#47678f;
            font-size:12px;
            font-weight:700;
        }}

        .animated-bar-label strong {{
            color:#092f6d;
            font-size:12px;
        }}

        .animated-bar-track {{
            width:100%;
            height:14px;
            overflow:hidden;
            border-radius:999px;
            background:#eaf1fb;
        }}

        .animated-bar-fill {{
            height:100%;
            min-width:2px;
            border-radius:999px;
            transform-origin:left center;
            background:linear-gradient(90deg,#1769ff,#65b1ff);
            box-shadow:0 4px 12px rgba(23,105,255,0.20);
            animation:expenseBarGrow 1.25s cubic-bezier(.2,.8,.2,1) both;
        }}

        .animated-bar-row:hover .animated-bar-fill {{
            filter:brightness(1.06);
            box-shadow:0 6px 18px rgba(23,105,255,0.30);
        }}
    </style>

    <div class="animated-bar-card">
        <div class="animated-bar-title">
            <div class="animated-bar-badge">{safe_text(badge)}</div>
            <div>{safe_text(title)}</div>
        </div>
        {rows}
    </div>
    """)


# ============================================================
# SIDEBAR BRAND
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.html("""
    <div style="
        padding:
            8px
            7px
            22px
            7px;

        animation:
            fadeIn 0.8s ease-out;
    ">

        <div style="
            display:flex;
            align-items:center;
            gap:12px;
        ">

            <div style="
                width:50px;
                height:50px;

                border-radius:15px;

                background:
                    linear-gradient(
                        135deg,
                        #1769ff,
                        #55a0ff
                    );

                color:white;

                display:flex;
                align-items:center;
                justify-content:center;

                font-size:20px;
                font-weight:900;

                box-shadow:
                    0 10px 25px
                    rgba(23,105,255,0.25);

                animation:
                    float 3s ease-in-out infinite;
            ">
                ET
            </div>

            <div>

                <div style="
                    color:#092f6d;
                    font-size:22px;
                    font-weight:850;
                    letter-spacing:-0.6px;
                ">
                    Expense Tracker
                </div>

                <div style="
                    color:#7890b4;
                    font-size:9px;
                    font-weight:800;
                    letter-spacing:0.6px;
                    margin-top:2px;
                ">
                    SMART SPENDING
                </div>

            </div>

        </div>

    </div>
    """)


    # --------------------------------------------------------
    # WORKSPACE
    # --------------------------------------------------------

    st.html("""
    <div style="
        color:#7890b4;
        font-size:10px;
        font-weight:850;
        letter-spacing:1.5px;
        margin:
            4px
            0
            12px
            4px;
    ">
        WORKSPACE
    </div>
    """)


    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    # The dashboard's Add New Expense button uses this flag to move
    # the sidebar radio to the Add Expense page after rerun.
    if st.session_state.get("go_add", False):
        st.session_state["workspace_page"] = "Add Expense"
        st.session_state["go_add"] = False

    page = st.radio(
        "",
        [
            "Dashboard",
            "Add Expense",
            "Transactions",
            "Analytics",
            "Insights"
        ],
        index=0,
        key="workspace_page",
        label_visibility="collapsed"
    )


    # --------------------------------------------------------
    # REPLAY
    # --------------------------------------------------------

    if st.button(
        "Replay Animations",
        use_container_width=True
    ):

        st.rerun()


    # --------------------------------------------------------
    # SQL CONNECTION
    # --------------------------------------------------------

    st.html("""
    <div style="
        margin-top:28px;

        padding:18px;

        border-radius:18px;

        background:
            linear-gradient(
                145deg,
                #ffffff,
                #f3f7ff
            );

        border:
            1px solid #dce8fb;

        box-shadow:
            0 10px 30px
            rgba(23,105,255,0.08);

        animation:
            fadeUp 1s ease-out;
    ">

        <div style="
            color:#1769ff;
            font-size:12px;
            font-weight:800;
        ">
            LIVE SQL CONNECTION
        </div>

        <div style="
            color:#092f6d;
            font-size:13px;
            font-weight:700;
            margin-top:7px;
        ">
            JOSH\\SQLEXPRESS01
        </div>

        <div style="
            display:flex;
            align-items:center;
            gap:7px;
            margin-top:10px;
            color:#6e86aa;
            font-size:11px;
        ">

            <span style="
                width:7px;
                height:7px;
                background:#20bd75;
                border-radius:50%;

                box-shadow:
                    0 0 0 5px
                    rgba(32,189,117,0.10);

                animation:
                    pulse 1.8s infinite;
            "></span>

            Database connected

        </div>

    </div>
    """)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.html(f"""
    <div style="
        position:relative;
        overflow:hidden;

        min-height:275px;

        padding:
            40px
            50px;

        border-radius:28px;

        background:
            linear-gradient(
                120deg,
                #08285c 0%,
                #103d86 45%,
                #1769d9 100%
            );

        box-shadow:
            0 25px 55px
            rgba(16,61,134,0.22);

        animation:
            fadeUp 0.8s ease-out;
    ">

        <div style="
            position:absolute;
            inset:0;

            background-image:
                linear-gradient(
                    rgba(255,255,255,0.035)
                    1px,
                    transparent 1px
                ),
                linear-gradient(
                    90deg,
                    rgba(255,255,255,0.035)
                    1px,
                    transparent 1px
                );

            background-size:
                36px 36px;

            opacity:0.8;
        "></div>

        <div style="
            position:absolute;

            width:220px;
            height:220px;

            right:-50px;
            bottom:-110px;

            border-radius:50%;

            background:
                rgba(76,174,255,0.25);

            animation:
                float 4s ease-in-out infinite;
        "></div>

        <div style="
            position:absolute;

            width:100px;
            height:100px;

            right:220px;
            top:-55px;

            border-radius:50%;

            background:
                rgba(94,198,255,0.10);
        "></div>

        <div style="
            position:relative;
            z-index:2;
        ">

            <div style="
                display:flex;
                align-items:center;
                gap:10px;

                color:#d7e7ff;

                font-size:12px;
                font-weight:850;

                letter-spacing:1.5px;

                margin-bottom:20px;
            ">

                <span style="
                    width:9px;
                    height:9px;

                    border-radius:50%;

                    background:#42d79b;

                    box-shadow:
                        0 0 0 6px
                        rgba(66,215,155,0.12);

                    animation:
                        pulse 2s infinite;
                "></span>

                SMART PERSONAL FINANCE

            </div>


            <div style="
                display:flex;
                align-items:center;
                gap:18px;
            ">

                <div style="
                    width:70px;
                    height:70px;

                    border-radius:20px;

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    color:white;

                    font-size:30px;
                    font-weight:900;

                    background:
                        rgba(255,255,255,0.14);

                    border:
                        1px solid
                        rgba(255,255,255,0.25);

                    box-shadow:
                        0 15px 30px
                        rgba(0,0,0,0.10);

                    animation:
                        float 3s ease-in-out infinite;
                ">
                    ET
                </div>

                <div style="
                    color:white;

                    font-size:48px;

                    font-weight:900;

                    letter-spacing:-2px;
                ">
                    Expense Tracker
                </div>

            </div>


            <div style="
                color:#c9dcfa;

                font-size:17px;

                line-height:1.65;

                max-width:850px;

                margin-top:18px;
            ">
                Track your expenses, understand spending patterns
                and transform raw transactions into clear financial insights.
            </div>


            <div style="
                display:flex;
                gap:12px;
                flex-wrap:wrap;

                margin-top:24px;
            ">

                <span style="
                    padding:10px 17px;

                    border-radius:999px;

                    color:white;

                    background:
                        rgba(255,255,255,0.11);

                    border:
                        1px solid
                        rgba(255,255,255,0.20);

                    font-size:12px;
                    font-weight:700;
                ">
                    Smart Analytics
                </span>

                <span style="
                    padding:10px 17px;

                    border-radius:999px;

                    color:white;

                    background:
                        rgba(255,255,255,0.11);

                    border:
                        1px solid
                        rgba(255,255,255,0.20);

                    font-size:12px;
                    font-weight:700;
                ">
                    Live SQL Data
                </span>

                <span style="
                    padding:10px 17px;

                    border-radius:999px;

                    color:white;

                    background:
                        rgba(255,255,255,0.11);

                    border:
                        1px solid
                        rgba(255,255,255,0.20);

                    font-size:12px;
                    font-weight:700;
                ">
                    Expense Tracking
                </span>

            </div>

        </div>

    </div>
    """)


    st.write("")


    # --------------------------------------------------------
    # FILTER BAR
    # --------------------------------------------------------

    st.html("""
    <div style="
        margin-bottom:8px;

        color:#092f6d;

        font-size:18px;
        font-weight:850;
    ">
        Financial Overview
    </div>
    """)


    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(
        [1.2, 1.3, 1.3, 1]
    )


    with filter_col1:

        if st.button(
            "＋ Add New Expense",
            use_container_width=True
        ):

            st.session_state["go_add"] = True
            st.rerun()


    with filter_col2:

        selected_category = st.selectbox(
            "Category",
            ["All Categories"]
            + sorted(
                df["CATEGORY"].dropna().unique().tolist()
            )
            if not df.empty
            else ["All Categories"]
        )


    with filter_col3:

        selected_payment = st.selectbox(
            "Payment Method",
            ["All Methods"]
            + sorted(
                df["PAYMENTMETHOD"].dropna().unique().tolist()
            )
            if not df.empty
            else ["All Methods"]
        )


    with filter_col4:

        search_text = st.text_input(
            "Search description...",
            placeholder="Search..."
        )


    # --------------------------------------------------------
    # FILTER DATA
    # --------------------------------------------------------

    filtered_df = df.copy()

    if selected_category != "All Categories":

        filtered_df = filtered_df[
            filtered_df["CATEGORY"]
            == selected_category
        ]


    if selected_payment != "All Methods":

        filtered_df = filtered_df[
            filtered_df["PAYMENTMETHOD"]
            == selected_payment
        ]


    if search_text.strip():

        filtered_df = filtered_df[
            filtered_df[
                "DESCRIPTIONTYPE"
            ]
            .astype(str)
            .str.contains(
                search_text,
                case=False,
                na=False
            )
        ]


    # ========================================================
    # METRIC CARDS
    # ========================================================

    metric1, metric2, metric3, metric4 = st.columns(4)


    with metric1:

        st.html(f"""
        <div style="
            min-height:150px;

            padding:24px;

            border-radius:18px;

            background:
                linear-gradient(
                    145deg,
                    #ffffff,
                    #f5fbff
                );

            border:
                1px solid #d9ebf7;

            box-shadow:
                0 10px 28px
                rgba(32,189,117,0.07);

            animation:
                fadeUp 0.8s ease-out;
        ">

            <div style="
                width:48px;
                height:48px;

                border-radius:50%;

                background:
                    linear-gradient(
                        135deg,
                        #37d889,
                        #10ae67
                    );

                color:white;

                display:flex;
                align-items:center;
                justify-content:center;

                font-size:19px;
                font-weight:900;

                box-shadow:
                    0 8px 18px
                    rgba(16,174,103,0.25);
            ">
                Rs
            </div>

            <div style="
                color:#123b76;

                font-size:13px;
                font-weight:700;

                margin-top:15px;
            ">
                Total Expense
            </div>

            <div style="
                color:#082f6d;

                font-size:29px;
                font-weight:900;

                margin-top:5px;

                letter-spacing:-1px;
            ">
                {money(total_expense)}
            </div>

            <div style="
                height:4px;

                border-radius:20px;

                margin-top:14px;

                background:
                    linear-gradient(
                        90deg,
                        #48d990,
                        #1769ff
                    );
            "></div>

        </div>
        """)


    with metric2:

        st.html(f"""
        <div style="
            min-height:150px;

            padding:24px;

            border-radius:18px;

            background:
                linear-gradient(
                    145deg,
                    #ffffff,
                    #f7f5ff
                );

            border:
                1px solid #e1dcff;

            box-shadow:
                0 10px 28px
                rgba(109,79,255,0.07);

            animation:
                fadeUp 0.95s ease-out;
        ">

            <div style="
                width:48px;
                height:48px;

                border-radius:50%;

                background:
                    linear-gradient(
                        135deg,
                        #9b7cff,
                        #6848ee
                    );

                color:white;

                display:flex;
                align-items:center;
                justify-content:center;

                font-size:20px;
                font-weight:900;
            ">
                #
            </div>

            <div style="
                color:#123b76;
                font-size:13px;
                font-weight:700;
                margin-top:15px;
            ">
                Transactions
            </div>

            <div style="
                color:#082f6d;
                font-size:29px;
                font-weight:900;
                margin-top:5px;
            ">
                {transaction_count}
            </div>

            <div style="
                height:4px;
                border-radius:20px;
                margin-top:14px;

                background:
                    linear-gradient(
                        90deg,
                        #9b7cff,
                        #1769ff
                    );
            "></div>

        </div>
        """)


    with metric3:

        st.html(f"""
        <div style="
            min-height:150px;

            padding:24px;

            border-radius:18px;

            background:
                linear-gradient(
                    145deg,
                    #ffffff,
                    #f4f9ff
                );

            border:
                1px solid #d8e9ff;

            box-shadow:
                0 10px 28px
                rgba(23,105,255,0.07);

            animation:
                fadeUp 1.1s ease-out;
        ">

            <div style="
                width:48px;
                height:48px;

                border-radius:50%;

                background:
                    linear-gradient(
                        135deg,
                        #55a5ff,
                        #1769ff
                    );

                color:white;

                display:flex;
                align-items:center;
                justify-content:center;

                font-size:14px;
                font-weight:900;
            ">
                AVG
            </div>

            <div style="
                color:#123b76;
                font-size:13px;
                font-weight:700;
                margin-top:15px;
            ">
                Average Expense
            </div>

            <div style="
                color:#082f6d;
                font-size:29px;
                font-weight:900;
                margin-top:5px;
            ">
                {money(average_expense)}
            </div>

            <div style="
                height:4px;
                border-radius:20px;
                margin-top:14px;

                background:
                    linear-gradient(
                        90deg,
                        #55a5ff,
                        #1769ff
                    );
            "></div>

        </div>
        """)


    with metric4:

        top_value = (
            category_totals.iloc[0]
            if not category_totals.empty
            else 0
        )

        top_percentage = (
            (top_value / total_expense * 100)
            if total_expense > 0
            else 0
        )

        st.html(f"""
        <div style="
            min-height:150px;

            padding:24px;

            border-radius:18px;

            background:
                linear-gradient(
                    145deg,
                    #ffffff,
                    #fff7fc
                );

            border:
                1px solid #f2dff0;

            box-shadow:
                0 10px 28px
                rgba(236,72,153,0.07);

            animation:
                fadeUp 1.25s ease-out;
        ">

            <div style="
                width:48px;
                height:48px;

                border-radius:50%;

                background:
                    linear-gradient(
                        135deg,
                        #ff7cc3,
                        #d83291
                    );

                color:white;

                display:flex;
                align-items:center;
                justify-content:center;

                font-size:20px;
                font-weight:900;
            ">
                TOP
            </div>

            <div style="
                color:#123b76;
                font-size:13px;
                font-weight:700;
                margin-top:15px;
            ">
                Top Category
            </div>

            <div style="
                color:#082f6d;
                font-size:24px;
                font-weight:900;
                margin-top:7px;
            ">
                {safe_text(top_category)}
            </div>

            <div style="
                color:#7188aa;
                font-size:11px;
                margin-top:7px;
            ">
                {top_percentage:.0f}% of total spending
            </div>

        </div>
        """)


    st.write("")


    # ========================================================
    # CHARTS
    # ========================================================

    chart_left, chart_right = st.columns(
        [1.55, 1]
    )


    # --------------------------------------------------------
    # CATEGORY BAR CHART
    # --------------------------------------------------------

    with chart_left:

        if category_totals.empty:

            st.info("No category data available.")

        else:

            max_category = float(
                category_totals.max()
            )

            bar_rows = ""

            bar_colors = [
                "#1769ff",
                "#4b8cff",
                "#55a5ff",
                "#6b72ff",
                "#8d65ff",
                "#a956ef"
            ]

            for index, (category, amount) in enumerate(
                category_totals.items()
            ):

                width = (
                    amount / max_category * 100
                    if max_category > 0
                    else 0
                )

                color = bar_colors[
                    index % len(bar_colors)
                ]

                bar_rows += f"""
                <div style="
                    margin-bottom:20px;
                ">

                    <div style="
                        display:flex;
                        justify-content:space-between;

                        color:#47678f;

                        font-size:12px;
                        font-weight:700;

                        margin-bottom:8px;
                    ">

                        <span>
                            {safe_text(category)}
                        </span>

                        <span style="
                            color:#092f6d;
                        ">
                            {money(amount)}
                        </span>

                    </div>

                    <div style="
                        width:100%;
                        height:13px;

                        background:#eaf1fb;

                        border-radius:20px;

                        overflow:hidden;
                    ">

                        <div style="
                            width:{width}%;

                            height:100%;

                            background:
                                linear-gradient(
                                    90deg,
                                    {color},
                                    #65b1ff
                                );

                            border-radius:20px;

                            transform-origin:left;

                            animation:
                                barGrow
                                1.2s
                                cubic-bezier(
                                    .2,
                                    .8,
                                    .2,
                                    1
                                )
                                forwards;

                            animation-delay:
                                {index * 0.12}s;
                        "></div>

                    </div>

                </div>
                """


            st.html(f"""
            <div style="
                min-height:390px;

                padding:26px;

                border-radius:20px;

                background:white;

                border:
                    1px solid #dce9fa;

                box-shadow:
                    0 12px 35px
                    rgba(23,105,255,0.07);

                animation:
                    fadeUp 1.3s ease-out;
            ">

                <div style="
                    display:flex;
                    align-items:center;
                    gap:12px;

                    margin-bottom:27px;
                ">

                    <div style="
                        width:36px;
                        height:36px;

                        border-radius:11px;

                        display:flex;
                        align-items:center;
                        justify-content:center;

                        color:#1769ff;

                        background:#edf4ff;

                        font-size:11px;
                        font-weight:900;
                    ">
                        BAR
                    </div>

                    <div style="
                        color:#092f6d;

                        font-size:18px;
                        font-weight:850;
                    ">
                        Spending by Category
                    </div>

                </div>

                {bar_rows}

            </div>
            """)


    # --------------------------------------------------------
    # PAYMENT DONUT
    # --------------------------------------------------------

    with chart_right:

        if payment_totals.empty:

            st.info("No payment data available.")

        else:

            total_payment = float(
                payment_totals.sum()
            )

            radius = 78

            circumference = (
                2 *
                math.pi *
                radius
            )

            colors = [
                "#1769ff",
                "#7257ef",
                "#25b9c9",
                "#45c982",
                "#f1a92b",
                "#e85ca8"
            ]

            # Build a CSS conic-gradient instead of SVG stroke segments.
            # This renders reliably inside Streamlit's HTML component.
            gradient_parts = []
            cumulative_percent = 0.0
            legend = ""

            for index, (method, amount) in enumerate(
                payment_totals.items()
            ):

                fraction = (
                    amount / total_payment
                    if total_payment > 0
                    else 0
                )

                percentage = (
                    amount /
                    total_payment *
                    100
                    if total_payment > 0
                    else 0
                )

                color = colors[
                    index % len(colors)
                ]

                start_percent = cumulative_percent
                end_percent = (
                    cumulative_percent + percentage
                )

                gradient_parts.append(
                    f"{color} {start_percent:.2f}% {end_percent:.2f}%"
                )

                cumulative_percent = end_percent

                legend += f"""
                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;

                    margin-bottom:12px;

                    font-size:11px;
                ">

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:8px;
                    ">

                        <span style="
                            width:9px;
                            height:9px;

                            border-radius:50%;

                            background:{color};
                        "></span>

                        <span style="
                            color:#47678f;
                            font-weight:600;
                        ">
                            {safe_text(method)}
                        </span>

                    </div>

                    <div style="
                        color:#092f6d;
                        font-weight:800;
                    ">
                        {percentage:.0f}%
                    </div>

                </div>
                """


            donut_gradient = ", ".join(gradient_parts)

            st.html(f"""
            <div style="
                min-height:390px;

                padding:26px;

                border-radius:20px;

                background:white;

                border:
                    1px solid #dce9fa;

                box-shadow:
                    0 12px 35px
                    rgba(23,105,255,0.07);

                animation:
                    fadeUp 1.45s ease-out;
            ">

                <div style="
                    display:flex;
                    align-items:center;
                    gap:12px;

                    margin-bottom:12px;
                ">

                    <div style="
                        width:36px;
                        height:36px;

                        border-radius:11px;

                        display:flex;
                        align-items:center;
                        justify-content:center;

                        color:#1769ff;

                        background:#edf4ff;

                        font-size:10px;
                        font-weight:900;
                    ">
                        PIE
                    </div>

                    <div style="
                        color:#092f6d;

                        font-size:18px;
                        font-weight:850;
                    ">
                        Spending by Payment Method
                    </div>

                </div>


                <div style="
                    display:flex;
                    align-items:center;
                    gap:25px;

                    margin-top:20px;
                ">

                    <div style="
                        position:relative;

                        width:220px;
                        height:220px;
                        flex-shrink:0;
                    ">

                        <div style="
                            width:220px;
                            height:220px;
                            border-radius:50%;

                            background:
                                conic-gradient(
                                    from -90deg,
                                    {donut_gradient}
                                );

                            display:flex;
                            align-items:center;
                            justify-content:center;

                            box-shadow:
                                0 10px 24px
                                rgba(23,105,255,0.10);

                            animation:
                                donutDraw 1.2s
                                cubic-bezier(.2,.8,.2,1)
                                forwards;
                        ">

                            <div style="
                                width:150px;
                                height:150px;
                                border-radius:50%;
                                background:white;

                                display:flex;
                                flex-direction:column;
                                align-items:center;
                                justify-content:center;
                            ">

                                <div style="
                                    color:#092f6d;
                                    font-size:20px;
                                    font-weight:900;
                                ">
                                    {money(total_payment)}
                                </div>

                                <div style="
                                    color:#7890b4;
                                    font-size:10px;
                                    margin-top:3px;
                                ">
                                    Total
                                </div>

                            </div>

                        </div>

                    </div>


                    <div style="
                        flex:1;
                    ">
                        {legend}
                    </div>

                </div>

            </div>
            """)


    st.write("")


    # ========================================================
    # RECENT TRANSACTIONS
    # ========================================================

    st.html("""
    <div style="
        color:#092f6d;

        font-size:18px;
        font-weight:850;

        margin-bottom:12px;
    ">
        Recent Transactions
    </div>
    """)


    recent = filtered_df.head(6)


    if recent.empty:

        st.info("No transactions found.")

    else:

        table_rows = ""

        for index, row in recent.iterrows():

            transaction_date = (
                row["EXPENSEDATE"].strftime(
                    "%d %b %Y"
                )
                if pd.notna(
                    row["EXPENSEDATE"]
                )
                else "-"
            )

            category = safe_text(
                row["CATEGORY"]
            )

            description = safe_text(
                row["DESCRIPTIONTYPE"]
            )

            payment = safe_text(
                row["PAYMENTMETHOD"]
            )

            amount = money(
                row["AMOUNT"]
            )

            table_rows += f"""
            <tr>

                <td>
                    {transaction_date}
                </td>

                <td>
                    {description}
                </td>

                <td>
                    <span style="
                        display:inline-block;

                        padding:
                            5px
                            10px;

                        border-radius:999px;

                        color:#1769ff;

                        background:#edf4ff;

                        font-size:10px;
                        font-weight:800;
                    ">
                        {category}
                    </span>
                </td>

                <td>
                    {payment}
                </td>

                <td style="
                    font-weight:850;
                    color:#092f6d;
                ">
                    {amount}
                </td>

            </tr>
            """


        st.html(f"""
        <div style="
            overflow:hidden;

            border-radius:20px;

            background:white;

            border:
                1px solid #dce9fa;

            box-shadow:
                0 12px 35px
                rgba(23,105,255,0.07);

            animation:
                fadeUp 1.6s ease-out;
        ">

            <table style="
                width:100%;

                border-collapse:collapse;

                font-family:
                    Inter,
                    Segoe UI,
                    sans-serif;
            ">

                <thead>

                    <tr style="
                        background:#f5f8fd;
                    ">

                        <th style="
                            padding:14px;
                            text-align:left;
                            color:#7188aa;
                            font-size:10px;
                        ">
                            DATE
                        </th>

                        <th style="
                            padding:14px;
                            text-align:left;
                            color:#7188aa;
                            font-size:10px;
                        ">
                            DESCRIPTION
                        </th>

                        <th style="
                            padding:14px;
                            text-align:left;
                            color:#7188aa;
                            font-size:10px;
                        ">
                            CATEGORY
                        </th>

                        <th style="
                            padding:14px;
                            text-align:left;
                            color:#7188aa;
                            font-size:10px;
                        ">
                            PAYMENT
                        </th>

                        <th style="
                            padding:14px;
                            text-align:left;
                            color:#7188aa;
                            font-size:10px;
                        ">
                            AMOUNT
                        </th>

                    </tr>

                </thead>

                <tbody>

                    {table_rows}

                </tbody>

            </table>

        </div>
        """)


# ============================================================
# ADD EXPENSE
# ============================================================

elif page == "Add Expense":

    st.html("""
    <div style="
        padding:32px;

        border-radius:25px;

        background:
            linear-gradient(
                120deg,
                #092f6d,
                #1769ff
            );

        color:white;

        box-shadow:
            0 20px 45px
            rgba(23,105,255,0.20);

        animation:
            fadeUp 0.7s ease-out;
    ">

        <div style="
            font-size:12px;
            font-weight:800;
            letter-spacing:1.3px;
            opacity:0.8;
        ">
            EXPENSE MANAGEMENT
        </div>

        <div style="
            font-size:34px;
            font-weight:900;
            margin-top:8px;
        ">
            Add New Expense
        </div>

        <div style="
            margin-top:8px;
            color:#d8e7ff;
        ">
            Add a transaction directly to your SQL Server database.
        </div>

    </div>
    """)


    st.write("")


    categories = [
        "Food",
        "Transport",
        "Entertainment",
        "Shopping",
        "Education",
        "Bills",
        "Health",
        "Other"
    ]

    payment_methods = [
        "UPI",
        "Cash",
        "Card",
        "Net Banking"
    ]


    with st.form(
        "expense_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)


        with col1:

            expense_date = st.date_input(
                "Expense Date",
                value=date.today()
            )

            category = st.selectbox(
                "Category",
                categories
            )

            description = st.text_input(
                "Description",
                placeholder="Example: Lunch at college"
            )


        with col2:

            amount = st.number_input(
                "Amount",
                min_value=0.01,
                step=10.0,
                format="%.2f"
            )

            payment = st.selectbox(
                "Payment Method",
                payment_methods
            )


        st.write("")


        submitted = st.form_submit_button(
            "Add Expense",
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

                    add_expense(
                        expense_date,
                        category,
                        description.strip(),
                        amount,
                        payment
                    )

                    st.success(
                        "Expense added successfully."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "Unable to add expense."
                    )


# ============================================================
# TRANSACTIONS
# ============================================================

elif page == "Transactions":

    st.html("""
    <div style="animation:fadeUp 0.7s ease-out;">

        <div style="
            color:#1769ff;
            font-size:11px;
            font-weight:850;
            letter-spacing:1.4px;
        ">
            TRANSACTION CENTER
        </div>

        <div style="
            color:#092f6d;
            font-size:34px;
            font-weight:900;
            margin-top:5px;
        ">
            All Transactions
        </div>

        <div style="
            color:#7890b4;
            margin-top:5px;
        ">
            View, manage and delete your recorded expenses.
        </div>

    </div>
    """)

    st.write("")

    if df.empty:

        st.info("No transactions available.")

    else:

        transaction_view = df.copy()

        transaction_view["EXPENSEDATE"] = (
            transaction_view["EXPENSEDATE"]
            .dt.strftime("%d %b %Y")
        )

        transaction_view["AMOUNT"] = (
            transaction_view["AMOUNT"]
            .apply(money)
        )

        transaction_view = transaction_view.rename(
            columns={
                "EXPENSEID": "ID",
                "EXPENSEDATE": "Date",
                "CATEGORY": "Category",
                "DESCRIPTIONTYPE": "Description",
                "AMOUNT": "Amount",
                "PAYMENTMETHOD": "Payment Method"
            }
        )

        st.dataframe(
            transaction_view,
            use_container_width=True,
            hide_index=True
        )

        st.write("")

        # --------------------------------------------------------
        # DELETE EXPENSE SECTION
        # --------------------------------------------------------

        st.html("""
        <div style="
            padding:24px;
            border-radius:20px;
            background:linear-gradient(145deg,#ffffff,#fff7f7);
            border:1px solid #f2dada;
            box-shadow:0 12px 30px rgba(220,53,69,0.06);
            animation:fadeUp 0.8s ease-out;
        ">
            <div style="
                color:#c62828;
                font-size:11px;
                font-weight:850;
                letter-spacing:1.4px;
            ">
                EXPENSE MANAGEMENT
            </div>

            <div style="
                color:#092f6d;
                font-size:24px;
                font-weight:900;
                margin-top:5px;
            ">
                Delete Transaction
            </div>

            <div style="
                color:#7890b4;
                font-size:13px;
                margin-top:5px;
            ">
                Select a transaction ID below to permanently remove it from SQL Server.
            </div>
        </div>
        """)

        st.write("")

        delete_col1, delete_col2 = st.columns([2, 1])

        with delete_col1:

            delete_options = df[
                [
                    "EXPENSEID",
                    "EXPENSEDATE",
                    "CATEGORY",
                    "DESCRIPTIONTYPE",
                    "AMOUNT",
                    "PAYMENTMETHOD"
                ]
            ].copy()

            delete_options["DISPLAY"] = delete_options.apply(
                lambda row:
                    f'#{int(row["EXPENSEID"])} | '
                    f'{row["EXPENSEDATE"].strftime("%d %b %Y")} | '
                    f'{row["CATEGORY"]} | '
                    f'{row["DESCRIPTIONTYPE"]} | '
                    f'₹{float(row["AMOUNT"]):,.2f} | '
                    f'{row["PAYMENTMETHOD"]}',
                axis=1
            )

            selected_display = st.selectbox(
                "Choose transaction to delete",
                delete_options["DISPLAY"].tolist(),
                key="delete_transaction_select"
            )

            selected_id = int(
                delete_options.loc[
                    delete_options["DISPLAY"] == selected_display,
                    "EXPENSEID"
                ].iloc[0]
            )

        with delete_col2:

            st.write("")

            delete_clicked = st.button(
                "Delete Selected Transaction",
                use_container_width=True,
                key="delete_selected_transaction"
            )

        if delete_clicked:

            try:

                delete_expense(selected_id)

                st.success(
                    f"Transaction #{selected_id} deleted successfully."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    "Unable to delete the selected transaction."
                )

# ============================================================
# ANALYTICS
# ============================================================

elif page == "Analytics":

    st.html("""
    <div style="
        animation:
            fadeUp 0.7s ease-out;
    ">

        <div style="
            color:#1769ff;
            font-size:11px;
            font-weight:850;
            letter-spacing:1.4px;
        ">
            SPENDING ANALYTICS
        </div>

        <div style="
            color:#092f6d;
            font-size:34px;
            font-weight:900;
            margin-top:5px;
        ">
            Financial Analytics
        </div>

        <div style="
            color:#7890b4;
            margin-top:5px;
        ">
            Understand how your money is distributed.
        </div>

    </div>
    """)


    st.write("")


    if df.empty:

        st.info("Add some expenses to see analytics.")

    else:

        analytics_category = (
            df.groupby("CATEGORY")["AMOUNT"]
            .sum()
            .sort_values(ascending=False)
        )

        analytics_payment = (
            df.groupby("PAYMENTMETHOD")["AMOUNT"]
            .sum()
            .sort_values(ascending=False)
        )


        col1, col2 = st.columns(2)


        with col1:

            st.html("""
            <div style="
                padding:22px;

                border-radius:20px;

                background:white;

                border:
                    1px solid #dce9fa;

                box-shadow:
                    0 12px 30px
                    rgba(23,105,255,0.07);
            ">

                <div style="
                    color:#092f6d;
                    font-size:18px;
                    font-weight:850;
                ">
                    Category Distribution
                </div>

            </div>
            """)

            render_animated_bar_chart(
                analytics_category,
                "Category Distribution",
                "BAR",
                390
            )


        with col2:

            st.html("""
            <div style="
                padding:22px;

                border-radius:20px;

                background:white;

                border:
                    1px solid #dce9fa;

                box-shadow:
                    0 12px 30px
                    rgba(23,105,255,0.07);
            ">

                <div style="
                    color:#092f6d;
                    font-size:18px;
                    font-weight:850;
                ">
                    Payment Method Distribution
                </div>

            </div>
            """)

            render_animated_bar_chart(
                analytics_payment,
                "Payment Method Distribution",
                "PAY",
                390
            )


# ============================================================
# INSIGHTS
# ============================================================

elif page == "Insights":

    st.html("""
    <div style="
        animation:
            fadeUp 0.7s ease-out;
    ">

        <div style="
            color:#1769ff;
            font-size:11px;
            font-weight:850;
            letter-spacing:1.4px;
        ">
            INTELLIGENT INSIGHTS
        </div>

        <div style="
            color:#092f6d;
            font-size:34px;
            font-weight:900;
            margin-top:5px;
        ">
            Spending Insights
        </div>

        <div style="
            color:#7890b4;
            margin-top:5px;
        ">
            Simple observations generated from your expense data.
        </div>

    </div>
    """)


    st.write("")


    if df.empty:

        st.info(
            "Add expenses to generate insights."
        )

    else:

        largest_row = df.loc[
            df["AMOUNT"].idxmax()
        ]

        largest_description = safe_text(
            largest_row["DESCRIPTIONTYPE"]
        )

        largest_amount = money(
            largest_row["AMOUNT"]
        )

        top_amount = (
            category_totals.iloc[0]
            if not category_totals.empty
            else 0
        )

        top_share = (
            top_amount /
            total_expense *
            100
            if total_expense > 0
            else 0
        )

        most_used_payment = (
            payment_totals.index[0]
            if not payment_totals.empty
            else "None"
        )


        insight1, insight2, insight3 = st.columns(3)


        with insight1:

            st.html(f"""
            <div style="
                min-height:190px;

                padding:25px;

                border-radius:20px;

                background:
                    linear-gradient(
                        145deg,
                        #ffffff,
                        #f1f7ff
                    );

                border:
                    1px solid #dce9fa;

                box-shadow:
                    0 12px 30px
                    rgba(23,105,255,0.07);

                animation:
                    fadeUp 0.8s ease-out;
            ">

                <div style="
                    width:45px;
                    height:45px;

                    border-radius:14px;

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    color:#1769ff;

                    background:#eaf2ff;

                    font-weight:900;
                ">
                    TOP
                </div>

                <div style="
                    color:#092f6d;

                    font-size:17px;
                    font-weight:850;

                    margin-top:18px;
                ">
                    Highest Spending Category
                </div>

                <div style="
                    color:#1769ff;

                    font-size:24px;
                    font-weight:900;

                    margin-top:7px;
                ">
                    {safe_text(top_category)}
                </div>

                <div style="
                    color:#7890b4;

                    font-size:12px;

                    margin-top:5px;
                ">
                    {top_share:.1f}% of your total spending
                </div>

            </div>
            """)


        with insight2:

            st.html(f"""
            <div style="
                min-height:190px;

                padding:25px;

                border-radius:20px;

                background:
                    linear-gradient(
                        145deg,
                        #ffffff,
                        #f8f4ff
                    );

                border:
                    1px solid #e6ddff;

                box-shadow:
                    0 12px 30px
                    rgba(109,79,255,0.07);

                animation:
                    fadeUp 1s ease-out;
            ">

                <div style="
                    width:45px;
                    height:45px;

                    border-radius:14px;

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    color:#704cf0;

                    background:#f0ebff;

                    font-weight:900;
                ">
                    MAX
                </div>

                <div style="
                    color:#092f6d;

                    font-size:17px;
                    font-weight:850;

                    margin-top:18px;
                ">
                    Largest Transaction
                </div>

                <div style="
                    color:#704cf0;

                    font-size:24px;
                    font-weight:900;

                    margin-top:7px;
                ">
                    {largest_amount}
                </div>

                <div style="
                    color:#7890b4;

                    font-size:12px;

                    margin-top:5px;
                ">
                    {largest_description}
                </div>

            </div>
            """)


        with insight3:

            st.html(f"""
            <div style="
                min-height:190px;

                padding:25px;

                border-radius:20px;

                background:
                    linear-gradient(
                        145deg,
                        #ffffff,
                        #f0fffa
                    );

                border:
                    1px solid #d6f3e7;

                box-shadow:
                    0 12px 30px
                    rgba(32,189,117,0.07);

                animation:
                    fadeUp 1.2s ease-out;
            ">

                <div style="
                    width:45px;
                    height:45px;

                    border-radius:14px;

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    color:#16a66b;

                    background:#e5faf1;

                    font-weight:900;
                ">
                    PAY
                </div>

                <div style="
                    color:#092f6d;

                    font-size:17px;
                    font-weight:850;

                    margin-top:18px;
                ">
                    Most Used Payment
                </div>

                <div style="
                    color:#16a66b;

                    font-size:24px;
                    font-weight:900;

                    margin-top:7px;
                ">
                    {safe_text(most_used_payment)}
                </div>

                <div style="
                    color:#7890b4;

                    font-size:12px;

                    margin-top:5px;
                ">
                    Most frequent payment method
                </div>

            </div>
            """)


# ============================================================
# END
# ============================================================