# MARC: Multi-Agent LLM Failure Annotation

Welcome! Thank you for participating as an independent annotator for this research project on multi-agent LLM systems.

This interactive web tool lets you inspect 16 multi-agent conversation traces (`T01` through `T16`) and evaluate whether any inter-agent coordination breakdowns occurred.

---

## 🚀 How to Run the App

### Option A: Using Streamlit Cloud (In Your Browser)
If the author has provided a web link (e.g., `https://<app-name>.streamlit.app`), simply open it in Chrome, Edge, or Firefox. No installation needed!

### Option B: Running Locally on Your Machine
1. **Clone or download this repository:**
   ```bash
   git clone <repo-url>
   cd marc-peer-annotation
   ```

2. **Install dependencies (Python 3.10+):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the web application:**
   ```bash
   streamlit run peer_annotate.py
   ```
   The application will open automatically in your browser at `http://localhost:8501`.

---

## 📋 Annotation Guidelines

For each trace (`T01` to `T16`), review the **Initial Task Goal** and the **Conversation Turns**. Then answer the four questions at the bottom of the page:

### 1. Did a failure occur?
* **Yes**: The agents failed to complete the task or experienced a critical breakdown.
* **No**: The agents successfully and correctly achieved the user's initial goal.
* **Not sure**: Ambiguous or partial success.

### 2. Failure Mode Classification (if a failure occurred)
Select the category that best explains the breakdown:

* **`FM-2.3` — Task Derailment:**
  An agent veers off-topic, forgets the user's primary goal, or pursues an unrequested task.
* **`FM-2.4` — Information Withholding:**
  An agent has necessary data, rules, or context but fails to pass it to the next agent, causing downstream errors.
* **`FM-2.6` — Reasoning–Action Mismatch:**
  An agent's stated thought/reasoning contradicts the actual action, tool call, or code it produces.
* **`None / Not sure`**: No failure occurred, or the failure does not fit the categories above.

### 3. Onset Turn Index
Enter the integer turn number where the failure **first became clearly observable** (e.g., Turn 4).

### 4. Notes (Optional)
A brief sentence explaining what went wrong (e.g., *"Agent B ignored the constraint to write terminal code and built a GUI instead"*).

---

## 💾 Saving & Submitting Your Answers

* **Saving as you go:** Click **"💾 Save & next"** after each trace.
* **Downloading your final answers:**
  When finished (or when taking a break), open the sidebar on the left and click:
  👉 **`📥 Download answers (.csv)`**
* **Resuming later:**
  If you return in a new session, use the **`📤 Upload previous peer_answers.csv`** button in the sidebar to restore your progress.
* **Submission:** Email or send the downloaded `peer_answers.csv` back to the researcher.

> [!NOTE]
> Please do not discuss your annotations with the author until all 16 traces are submitted, to ensure unbiased inter-rater evaluation.
