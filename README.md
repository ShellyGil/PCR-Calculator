# PCR Genotyping Master Mix Calculator 🧬

A modern, mobile-friendly web tool designed to help molecular biologists quickly calculate reagent volumes for PCR genotyping reactions. 

It features real-time updates, automatic dark mode, and a built-in reference for thermal cycling protocols.

## 🚀 Live Demo
**[Click here to use the Calculator](https://shellygil.github.io/PCR-Calculator/)**

## ✨ Features

* **Real-Time Calculation:** Results update instantly as you drag the slider or type numbers.
* **Flexible Inputs:** * Supports **2X** and **5X** reaction mixes.
    * Adjustable **Excess %** (pipetting error margin).
    * Sample count slider (1-96) for quick adjustments.
* **Smart Layout:**
    * **Mobile-First:** Works perfectly on phones inside the lab.
    * **Dark Mode:** Automatically detects system theme (easier on the eyes in dark microscope rooms).
    * **High Visibility:** The "Total Master Mix" volume is highlighted for quick reference.
* **Utilities:**
    * 📋 **Copy to Clipboard:** Formats the recipe for lab notebooks.
    * 💾 **Save to File:** Downloads a `.txt` report.
    * 🌡️ **Protocol Reference:** Expandable dropdown containing standard thermal cycling conditions.

## 📖 How to Use

1.  **Set Sample Count:** Use the slider or the input box to select how many PCR reactions you are running.
2.  **Adjust Excess:** Set your preferred safety margin (default is 10%) to account for pipetting loss.
3.  **Select Mix:** Choose whether you are using a 2X or 5X commercial master mix.
4.  **Prepare:**
    * Look at the **Master Mix** column in the table for total volumes.
    * The large number in the blue box is the total volume of Master Mix you need to pipette.
5.  **Reference:** Click "Protocol & Cycling Conditions" to view standard denaturation, annealing, and extension steps.

## 🛠️ Installation & Deployment

### Option A: Use Online (GitHub Pages)
This project is designed to be hosted on GitHub Pages.
1.  Upload `index.html` to a GitHub repository.
2.  Go to **Settings** > **Pages**.
3.  Select `main` branch as the source and click **Save**.
4.  Share the generated URL with your lab group.

### Option B: Run Locally
No server is required.
1.  Download `index.html`.
2.  Double-click the file to open it in Chrome, Safari, or Edge.

## 🤖 AI Generation History
This tool was created through an iterative dialogue with an AI assistant. Below are the prompts used to evolve the project from a Python script to a responsive web app:

1. "enhance this code to make it way more user friendly: [Original Python Code]"

2. "can this all be as a git page (an actual website) with a cool design where you can use the calculator online."

3. "can you include in the website an option to open the PCR protocol as a drop down?"


## ⚙️ Customization

You can easily modify the constants in the `index.html` file to match your specific lab protocols.

**To change reaction volumes:**
Look for the JavaScript section at the bottom of the file:
```javascript
// --- Constants ---
const PER_SAMPLE_TOTAL = 11.0; // Change total reaction volume here
const PRIMER_VOL = 0.5;        // Change volume per primer here
