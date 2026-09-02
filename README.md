# 🛡️ RWatch

### Risk-based transaction monitoring for financial crime detection

**RWatch** is a portfolio-built financial crime risk monitoring platform that simulates how financial institutions can detect, prioritize, investigate, and make decisions on potentially suspicious customer activity.

The project combines **Product Management, AML/financial crime concepts, transaction monitoring, risk scoring, SQL, Python, PostgreSQL, Streamlit, and product analytics** into an end-to-end working prototype.

> **Disclaimer:** RWatch uses 100% synthetic data and is a portfolio prototype. It is not a production AML, fraud detection, or regulatory compliance system.

---

## 🚀 Live Demo

### [Launch RWatch →](https://rwatch.streamlit.app/)

Explore the live application:

- 📊 Risk monitoring dashboard
- 🚨 Alert queue
- 👤 Customer profiles
- 📈 Risk and product analytics
- 🧑🏽‍💻 Analyst decision workflow

---

# 🎯 The Problem

Financial institutions process large volumes of transactions every day.

The challenge is not simply identifying unusual activity. The bigger challenge is determining:

- Which activity is actually worth investigating?
- Why was a transaction flagged?
- How risky is the customer?
- Which alerts should an analyst investigate first?
- What information does the analyst need to make a decision?
- Are detection rules generating useful signals?
- How do risk thresholds affect analyst workload?

RWatch was built to explore these questions through a practical product and technical implementation.

---

# 💡 The Product

RWatch transforms customer and transaction activity into prioritized risk signals.

```text
Customer & Transaction Data
            ↓
      Detection Rules
            ↓
      Risk Evaluation
            ↓
      Risk Score
            ↓
       Risk Band
            ↓
       Alert Queue
            ↓
   Analyst Investigation
            ↓
     Analyst Decision
            ↓
      Product Analytics
```

The goal is to move from:

> **"Something looks unusual."**

to:

> **"This activity triggered specific risk signals, produced this risk level, and requires an appropriate action."**

---

# ✨ Key Features

## 📊 Risk Monitoring Dashboard

The dashboard provides a high-level view of the monitoring environment.

It includes:

- Open alerts
- Critical alerts
- Customer count
- Transaction volume
- Alert distribution by risk band

---

## 🚨 Alert Queue

The Alert Queue provides an analyst-oriented view of flagged activity.

Analysts can review potentially suspicious activity and investigate alerts based on available customer, transaction, and risk information.

The workflow is built around a core principle:

> **Not every alert deserves the same level of attention.**

Risk-based prioritization helps analysts focus their time where it matters most.

---

## 👤 Customer Risk Profiles

Customer profiles provide additional context during investigations.

Risk evaluation can incorporate factors including:

- Customer risk rating
- PEP status
- Sanctions screening status
- Account opening date
- High-risk country relationships
- Historical transaction behaviour

This helps connect individual transaction activity with the customer's broader risk context.

---

# 🔎 Transaction Monitoring

RWatch uses rule-based detection to identify behavioural patterns that may warrant investigation.

The monitoring framework includes detection scenarios such as:

1. **Velocity anomaly**
2. **Unusual transaction amount vs. customer history**
3. **Deviation from KYC baseline**
4. **New beneficiary + high-value transaction**
5. **Rapid movement of funds**
6. **Geographic anomaly**
7. **Device anomaly**
8. **Unusual transaction frequency vs. baseline**

These rules are designed for simulation and portfolio experimentation rather than production regulatory use.

---

# 🎯 Risk Scoring

RWatch combines risk signals into a numerical risk score.

The project uses a **0–100 risk scoring framework** to support prioritization.

Conceptually:

```text
Customer Risk Factors
          +
Transaction Behaviour
          +
Detection Signals
          +
Contextual Risk
          ↓
      Risk Score
          ↓
       Risk Band
          ↓
Investigation Priority
```

The scoring approach allows alerts to be prioritized rather than treating every detection equally.

---

# ⚖️ Risk Bands

Risk scores can be grouped into bands such as:

| Risk Band | Purpose |
|---|---|
| 🟢 Low | Lower priority activity |
| 🟡 Medium | Requires review |
| 🟠 High | Higher-priority investigation |
| 🔴 Critical | Immediate attention |

The exact thresholds are part of the model experimentation and calibration process.

---

# 🧪 Risk Model Experimentation

One of the key experiments in RWatch was testing how different scoring models affect the overall risk population.

Three model variants were explored:

| Model | Minimum | Maximum | Average | Median |
|---|---:|---:|---:|---:|
| Model 1 | 10 | 40 | 12.10 | 10 |
| Model 2 | 20 | 60 | 22.95 | 20 |
| Model 3 | 15 | 50 | 17.60 | 15 |

The experiments demonstrated an important product trade-off:

> **Changing scoring thresholds can significantly affect alert volume, risk distribution, and analyst workload.**

This makes risk calibration both a technical and product decision.

---

# 🧑🏽‍💻 Analyst Investigation Workflow

RWatch is designed around the analyst workflow rather than detection alone.

The investigation process follows:

```text
Alert
  ↓
Customer Context
  ↓
Transaction Behaviour
  ↓
Risk Signals
  ↓
Risk Score
  ↓
Analyst Decision
```

The prototype supports decision outcomes including:

- Clear
- Escalate
- Restrict

The objective is to demonstrate how a monitoring product can turn detection signals into **actionable risk decisions**.

---

# 📈 Product Analytics

RWatch is instrumented with **Mixpanel** to understand how users interact with the monitoring workflow.

Tracked events include:

```text
alert_viewed
alert_opened
alert_escalated
alert_cleared
alert_restricted
decision_completed
customer_profile_viewed
```

These events can be used to understand:

- Alert engagement
- Investigation behaviour
- Decision activity
- Analyst workflow
- Potential workflow friction
- Risk-band behaviour

This allows RWatch to be evaluated not only as a detection system, but also as a **product used by analysts**.

---

# 📊 Analytics

The analytics layer explores several dimensions of system performance.

### Rule Performance

Which detection rules generate the most alerts?

### Precision Proxy

How effectively do detection rules identify synthetic suspicious activity?

RWatch uses the synthetic ground-truth field:

```text
is_synthetic_suspicious
```

This provides a way to evaluate detection behaviour within the simulated environment.

> This metric is a portfolio evaluation mechanism and should not be interpreted as real-world model performance.

### Risk Distribution

How does the customer and alert population change across risk bands?

### Time-to-Decision

How long does it take to complete an investigation?

These metrics connect technical detection performance with operational product outcomes.

---

# 🏗️ Architecture

```text
                    ┌───────────────────────┐
                    │   Synthetic Dataset   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      PostgreSQL       │
                    │     Risk Database     │
                    └───────────┬───────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
       ┌─────────────────┐             ┌─────────────────┐
       │ Detection Rules │             │ Customer Risk   │
       │ & Risk Scoring  │             │ Factors         │
       └────────┬────────┘             └────────┬────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Risk Scores &       │
                    │       Alerts          │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      Streamlit        │
                    │     Application       │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │ Alert Queue │  │  Customers  │  │  Analytics  │
       └─────────────┘  └─────────────┘  └─────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │       Mixpanel        │
                    │  Product Analytics    │
                    └───────────────────────┘
```

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Application logic and data processing |
| **Streamlit** | Web application and dashboard |
| **PostgreSQL** | Relational database |
| **Supabase** | Cloud PostgreSQL infrastructure |
| **SQLAlchemy** | Database connectivity |
| **Pandas** | Data analysis and transformation |
| **Faker** | Synthetic data generation |
| **Mixpanel** | Product analytics |
| **GitHub** | Version control |
| **Streamlit Community Cloud** | Application deployment |

---

# 🗄️ Data

RWatch uses a synthetic financial activity dataset created specifically for the project.

The database includes entities such as:

- Customers
- Transactions
- Transaction alerts
- Risk scores
- Detection rules
- Customer risk attributes
- Analyst decisions

The dataset was designed to simulate relationships commonly found in a financial crime monitoring environment.

### Synthetic Data Disclaimer

No real customer, transaction, financial, or personally identifiable information is used in this project.

---

# 🧠 Product Thinking Behind RWatch

RWatch was intentionally designed as more than a technical dashboard.

The product decisions were guided by several principles.

### 1. Risk-based prioritization

The system should help analysts prioritize rather than simply generate alerts.

### 2. Explainability

Rule-based signals make it easier to understand why activity was flagged.

### 3. Analyst-first design

Detection is only useful when the analyst can investigate and act on the result.

### 4. Calibration matters

Changing risk thresholds can have a direct impact on alert volume and operational workload.

### 5. Measure the workflow

Product analytics can reveal how users actually interact with the investigation experience.

---

# 🔐 Security & Secrets

Database credentials and other sensitive configuration values are **not stored in the repository**.

RWatch uses environment variables and deployment secrets for database configuration.

The application expects:

```text
RISKWATCH_DB_URL
```

For local development, configure the variable in your environment.

For cloud deployment, the database connection is stored using Streamlit's secrets management.

> Never commit passwords, API keys, database connection strings, or other credentials to GitHub.

---

# ⚙️ Run RWatch Locally

## 1. Clone the repository

```bash
git clone https://github.com/engel-dera/app.git
cd app
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure the database

Set:

```text
RISKWATCH_DB_URL
```

Example format:

```text
postgresql://username:password@host:5432/database
```

Do not commit the actual connection string to GitHub.

## 5. Run Streamlit

```bash
streamlit run app.py
```

The application will be available at the local URL provided by Streamlit.

---

# ☁️ Deployment

RWatch is deployed using:

- **GitHub** → source control
- **Streamlit Community Cloud** → application hosting
- **Supabase** → cloud PostgreSQL database

The production flow is:

```text
GitHub
   ↓
Streamlit Community Cloud
   ↓
Supabase PostgreSQL
```

This means the application does **not** depend on my local computer or local Streamlit terminal being active.

---

# 📁 Project Structure

```text
.
├── app.py
├── alert_queue.py
├── Customers.py
├── analytics.py
├── tracking.py
├── requirements.txt
├── README.md
└── ...
```

### Main files

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application and dashboard |
| `alert_queue.py` | Alert investigation workflow |
| `Customers.py` | Customer profiles and risk information |
| `analytics.py` | Risk and product analytics |
| `tracking.py` | Mixpanel event tracking |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

---

# 🚧 Current Limitations

RWatch is intentionally a portfolio prototype.

It does not provide:

- Real customer data
- Real-time transaction processing
- Production AML compliance
- Regulatory reporting
- Live sanctions screening
- Production fraud detection
- Production-grade authentication
- Production security controls
- Regulatory-approved risk methodology
- Machine-learning fraud detection

The synthetic dataset and evaluation framework exist for demonstration, experimentation, and product learning.

---

# 🔮 Future Improvements

Potential future iterations include:

- Real-time transaction ingestion
- Behavioural customer baselines
- Machine-learning anomaly detection
- Explainable ML risk scoring
- Case management
- Audit trails
- Watchlist and sanctions integrations
- KYC/KYB integrations
- Alert deduplication
- Model monitoring
- Champion/challenger risk models
- Role-based access control
- Advanced analyst productivity metrics
- Automated case escalation
- More sophisticated customer risk modelling

---

# 📚 What This Project Demonstrates

RWatch demonstrates experience across multiple areas.

### Product Management

- Problem definition
- Product requirements
- Risk-based prioritization
- Workflow design
- Product analytics
- Trade-off analysis
- Experimentation
- Feature prioritization

### FinTech & Financial Crime

- Transaction monitoring
- Customer risk profiling
- KYC/KYB concepts
- AML-oriented workflows
- Risk scoring
- Detection rules
- Alert investigation

### Data & SQL

- Relational database design
- SQL queries
- Aggregation
- Joins
- Risk distribution analysis
- Alert analysis
- Synthetic ground truth evaluation

### Python & Engineering

- Python application development
- Database integration
- Data processing
- Synthetic data generation
- Streamlit application development
- API/event instrumentation

### Analytics

- Mixpanel instrumentation
- Event design
- Workflow measurement
- Risk-band analysis
- Detection performance analysis

### Deployment

- Git/GitHub
- Cloud PostgreSQL
- Environment variables
- Secrets management
- Streamlit Community Cloud

---

# 🧭 Project Journey

RWatch was built as an end-to-end product experiment.

The project evolved through:

```text
Problem Definition
       ↓
Product Concept
       ↓
Data & Database Design
       ↓
Detection Rules
       ↓
Risk Scoring
       ↓
Calibration Experiments
       ↓
Analyst Workflow
       ↓
Product Analytics
       ↓
Streamlit Application
       ↓
Cloud Database
       ↓
Public Deployment
```

The project was intentionally built to demonstrate that a product manager can work across **problem discovery, product design, data, analytics, technical implementation, and deployment**.

---

# 👩🏽‍💻 About

RWatch was created as a portfolio project exploring the intersection of:

**Product Management × FinTech × AML × Risk × Data × Analytics × Technology**

The project reflects an interest in building products that make complex financial risk easier to **detect, understand, prioritize, and act on**.

---

# 📫 Connect With Me

### LinkedIn

**[Angel Dera](https://www.linkedin.com/in/angel-dera-nw)**

### Live Product

**[RWatch](https://rwatch.streamlit.app/)**

---

## ⭐ Interested in the project?

Explore the repository, try the live demo, or connect with me to discuss the product decisions and thinking behind RWatch.

---

### Built with Python, PostgreSQL, Streamlit & a lot of curiosity. 🛡️
