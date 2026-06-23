# Reliability Study

A Jupyter-based workflow for generating and analyzing synthetic semiconductor reliability data. The project simulates accelerated life tests (ALT), fits Weibull distributions to failure data, and produces standard reliability plots including Kaplan–Meier survival curves, Weibull probability plots, and Arrhenius acceleration analysis.

## Project Structure

```
Reliability_study/
├── data_generation.ipynb      # Generate synthetic reliability dataset
├── reliability_analysis.ipynb # Fit models and create plots
├── reliability_dataset1.csv   # Primary dataset used by analysis notebook
├── requirements.txt           # Python dependencies
└── README.md
```

## Workflow

### 1. Generate data

Open and run `data_generation.ipynb`. It creates `reliability_dataset1.csv` with simulated device failure records under multiple stress conditions.

The generator models:

- **HTOL** (High Temperature Operating Life) — 100, 125, 150 °C at 4.0 V, 4.5 V and 5.0 V
- **THB** (Temperature Humidity Bias) — 85 °C at 40%, 60%, and 80% humidity
- **TC** (Temperature Cycling) — −40 °C and 125 °C

Failure times follow a 2-parameter Weibull distribution. Stress acceleration uses an Arrhenius temperature model, with additional voltage and humidity multipliers. Batch-to-batch and device-to-device variation are included to produce realistic scatter in probability plots.

### 2. Analyze data

Open and run `reliability_analysis.ipynb` from top to bottom. The notebook:

1. Loads `reliability_dataset1.csv`
2. Fits a 2-parameter Weibull distribution per test group (test type, temperature, voltage, humidity)
3. Computes **Beta** (shape), **Eta** (scale), **MTTF**, and hazard trend (decreasing / constant / increasing)
4. Produces plots:
  - Kaplan–Meier survival curves by test type and temperature
  - Weibull probability plot for a selected HTOL condition (150 °C, 5.0 V)
  - Beta vs. temperature
  - Eta vs. temperature
  - Arrhenius analysis (ln(Eta) vs. 1/T) for HTOL data

## Dataset Schema


| Column                 | Description                                              |
| ---------------------- | -------------------------------------------------------- |
| `Device_ID`            | Unique device identifier                                 |
| `Test_Type`            | Test program (`HTOL`, `THB`, `TC`)                       |
| `Stress_Temperature_C` | Stress temperature (°C)                                  |
| `Stress_Voltage_V`     | Applied voltage (V)                                      |
| `Humidity_Percent`     | Relative humidity (%)                                    |
| `Failure_Time_Hours`   | Observed failure or censoring time (hours)               |
| `Censored`             | `1` if the device survived to test end, `0` if it failed |
| `Batch_ID`             | Manufacturing batch (`B1`–`B4`)                          |


## Requirements

- Python 3.10+
- [Jupyter](https://jupyter.org/) or VS Code / Cursor with notebook support

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage Notes

- Run `data_generation.ipynb` first if you need a fresh dataset, or use the included `reliability_dataset1.csv` directly.
- In `reliability_analysis.ipynb`, run all cells in order so that `df` and `result` are defined before plotting.
- Weibull groups require at least 5 failures; groups with fewer failures are skipped during fitting.
- The synthetic data intentionally includes variability, so Weibull probability plots may show moderate deviation from ideal linear behavior—similar to real semiconductor datasets.

## Key Libraries


| Library            | Purpose                                           |
| ------------------ | ------------------------------------------------- |
| `pandas` / `numpy` | Data handling and numerical computation           |
| `matplotlib`       | Plotting                                          |
| `scipy`            | Gamma function for MTTF calculation               |
| `lifelines`        | Kaplan–Meier survival analysis                    |
| `reliability`      | 2-parameter Weibull fitting and probability plots |


