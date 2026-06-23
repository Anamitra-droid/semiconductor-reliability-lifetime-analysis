"""Add self-explanatory comments and markdown intros to project notebooks."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def set_source(cell, lines):
    if isinstance(lines, str):
        lines = [lines]
    cell["source"] = [line if line.endswith("\n") else line + "\n" for line in lines]


def insert_cell(cells, index, cell_type, source):
    cell = {"cell_type": cell_type, "metadata": {}, "source": []}
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    set_source(cell, source)
    cells.insert(index, cell)


def update_data_generation(nb):
    cells = nb["cells"]

    insert_cell(
        cells,
        0,
        "markdown",
        [
            "# Synthetic Reliability Data Generation",
            "",
            "This notebook simulates semiconductor accelerated life test (ALT) data for three test programs:",
            "",
            "- **HTOL** — high-temperature operating life at multiple temperatures and voltages",
            "- **THB** — temperature-humidity bias at multiple humidity levels",
            "- **TC** — temperature cycling between cold and hot extremes",
            "",
            "Failure times follow a 2-parameter Weibull distribution. Temperature acceleration uses the Arrhenius model; voltage and humidity apply additional stress multipliers. Batch-to-batch and device-to-device scatter are included to mimic real manufacturing variation.",
        ],
    )

    set_source(
        cells[1],
        [
            "# --- Imports and physical constants ---",
            "import math",
            "import numpy as np",
            "import pandas as pd",
            "",
            "# Boltzmann constant (eV/K) used in the Arrhenius acceleration model",
            "K_B = 8.617333262145e-5",
            "",
            "",
            "def voltage_factor(voltage):",
            '    """Return a scale multiplier that shortens life as voltage rises above 3.3 V."""',
            "    return 1 / (1 + 0.15 * (voltage - 3.3))",
            "",
            "",
            "def humidity_factor(humidity):",
            '    """Return a scale multiplier that shortens life as relative humidity increases."""',
            "    return 1 / (1 + 0.03 * humidity)",
            "",
            "",
            "def generate_reliability_data():",
            '    """',
            "    Build a synthetic reliability dataset with censored and failed devices.",
            "",
            "    Each unique combination of test type, temperature, voltage, and humidity",
            "    gets 800 devices. Failure times are drawn from Weibull(eta, beta) with",
            "    right-censoring at the test end time.",
            '    """',
            "    # Fixed seed for reproducible datasets across runs",
            "    rng = np.random.default_rng(2026)",
            "",
            "    batches = [\"B1\", \"B2\", \"B3\", \"B4\"]",
            "",
            "    # Each manufacturing batch shifts characteristic life by a random factor",
            "    batch_effect = {batch: rng.normal(1.0, 0.08) for batch in batches}",
            "",
            "    # Test matrix: stress levels, censoring horizon, and Weibull shape per program",
            "    tests = {",
            "        \"HTOL\": {",
            "            \"temperatures\": [100, 125, 150],",
            "            \"voltages\": [4, 4.5, 5.0],",
            "            \"humidity\": [40],",
            "            \"test_end\": 2000,",
            "            \"beta\": 2.2,",
            "        },",
            "        \"THB\": {",
            "            \"temperatures\": [85],",
            "            \"voltages\": [3.3],",
            "            \"humidity\": [40, 60, 80],",
            "            \"test_end\": 1500,",
            "            \"beta\": 1.9,",
            "        },",
            "        \"TC\": {",
            "            \"temperatures\": [-40, 125],",
            "            \"voltages\": [0.0],",
            "            \"humidity\": [40],",
            "            \"test_end\": 1200,",
            "            \"beta\": 1.8,",
            "        },",
            "    }",
            "",
            "    # Reference conditions for Arrhenius scaling (125 C -> 398.15 K)",
            "    activation_energy = 0.45",
            "    reference_temperature = 398.15",
            "    reference_eta = 2000",
            "",
            "    all_rows = []",
            "    device_number = 1",
            "",
            "    for test_name, test_info in tests.items():",
            "        beta = test_info[\"beta\"]",
            "",
            "        for temperature_c in test_info[\"temperatures\"]:",
            "            temperature_k = temperature_c + 273.15",
            "",
            "            # Higher temperature -> larger acceleration -> shorter characteristic life",
            "            acceleration_factor = math.exp(",
            "                (activation_energy / K_B)",
            "                * ((1 / temperature_k) - (1 / reference_temperature))",
            "            )",
            "",
            "            for humidity in test_info[\"humidity\"]:",
            "                for voltage in test_info[\"voltages\"]:",
            "                    # TC uses mechanical/thermal cycling; disable Arrhenius scaling",
            "                    if test_name == \"TC\":",
            "                        acceleration_factor = 1.0",
            "                        voltage_multiplier = 1.0 if voltage == 0 else voltage_factor(voltage)",
            "                        base_eta = (",
            "                            reference_eta",
            "                            * acceleration_factor",
            "                            * voltage_multiplier",
            "                            * humidity_factor(humidity)",
            "                        )",
            "                    else:",
            "                        base_eta = (",
            "                            reference_eta",
            "                            * acceleration_factor",
            "                            * voltage_factor(voltage)",
            "                            * humidity_factor(humidity)",
            "                        )",
            "",
            "                    # Simulate 800 devices per stress combination",
            "                    for _ in range(800):",
            "                        batch = rng.choice(batches)",
            "",
            "                        # Apply batch and per-device scatter to the group eta",
            "                        actual_eta = base_eta * batch_effect[batch] * rng.normal(1.0, 0.06)",
            "",
            "                        # Inverse-CDF sampling for Weibull failure time",
            "                        random_probability = rng.random()",
            "                        failure_time = actual_eta * (-np.log(1 - random_probability)) ** (1 / beta)",
            "",
            "                        test_end_time = test_info[\"test_end\"]",
            "                        censored = int(failure_time >= test_end_time)",
            "",
            "                        row = {",
            "                            \"Device_ID\": f\"D{device_number:04d}\",",
            "                            \"Test_Type\": test_name,",
            "                            \"Stress_Temperature_C\": temperature_c,",
            "                            \"Stress_Voltage_V\": voltage,",
            "                            \"Humidity_Percent\": humidity,",
            "                            \"Failure_Time_Hours\": min(failure_time, test_end_time),",
            "                            \"Censored\": censored,",
            "                            \"Batch_ID\": batch,",
            "                        }",
            "",
            "                        all_rows.append(row)",
            "                        device_number += 1",
            "",
            "    return pd.DataFrame(all_rows)",
        ],
    )

    set_source(
        cells[2],
        [
            "# Generate the full synthetic dataset and export it for the analysis notebook",
            "df = generate_reliability_data()",
            "",
            'df.to_csv("reliability_dataset1.csv", index=False)',
            "",
            'print("CSV file saved successfully.")',
            'print(f"Rows: {len(df):,} | Failed: {(df[\"Censored\"] == 0).sum():,} | Censored: {(df[\"Censored\"] == 1).sum():,}")',
        ],
    )


def update_reliability_analysis(nb):
    cells = nb["cells"]

    insert_cell(
        cells,
        0,
        "markdown",
        [
            "# Reliability Data Analysis",
            "",
            "This notebook loads the synthetic ALT dataset, fits a 2-parameter Weibull model to each unique stress group, and produces standard reliability visualizations:",
            "",
            "1. Kaplan-Meier survival curves",
            "2. Weibull probability plots for selected HTOL conditions",
            "3. Beta and Eta trends versus temperature",
            "4. Arrhenius analysis for HTOL data",
            "",
            "Run all cells in order from top to bottom.",
        ],
    )

    set_source(
        cells[1],
        [
            "# --- Library imports ---",
            "# pandas/numpy: tabular data and numerics",
            "# matplotlib: plotting",
            "# scipy.gamma: MTTF calculation for Weibull distributions",
            "# reliability: 2-parameter Weibull fitting and probability plots",
            "# lifelines: Kaplan-Meier survival estimation",
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "from scipy.special import gamma",
            "import os",
            "from reliability.Fitters import Fit_Weibull_2P",
            "from lifelines import KaplanMeierFitter",
        ],
    )

    set_source(
        cells[2],
        [
            "# Load the dataset produced by data_generation.ipynb",
            "df = pd.read_csv(\"reliability_dataset1.csv\")",
            "",
            "# Re-save to normalize formatting (no index column)",
            "df.to_csv(\"reliability_dataset1.csv\", index=False)",
            "",
            "print(\"Loaded columns:\", list(df.columns))",
            "print(f\"Devices: {len(df):,}\")",
            "print(os.listdir())",
        ],
    )

    set_source(
        cells[3],
        [
            "def fit_groups(df):",
            '    """',
            "    Fit a 2-parameter Weibull distribution to each unique stress group.",
            "",
            "    Groups are defined by test type, temperature, voltage, and humidity.",
            "    Groups with fewer than 5 observed failures are skipped.",
            '    """',
            "    results = []",
            "",
            "    groups = df.groupby(",
            "        [",
            '            "Test_Type",',
            '            "Stress_Temperature_C",',
            '            "Stress_Voltage_V",',
            '            "Humidity_Percent",',
            "        ]",
            "    )",
            "",
            "    for (test_name, temp, voltage, humidity), group_data in groups:",
            "        # Separate observed failures from right-censored survivors",
            "        failures = group_data.loc[",
            '            group_data["Censored"] == 0, "Failure_Time_Hours"',
            "        ].values",
            "",
            "        censored = group_data.loc[",
            '            group_data["Censored"] == 1, "Failure_Time_Hours"',
            "        ].values",
            "",
            "        if len(failures) < 5:",
            "            continue",
            "",
            "        weibull_fit = Fit_Weibull_2P(",
            "            failures=failures,",
            "            right_censored=censored,",
            "            show_probability_plot=False,",
            "            print_results=False,",
            "        )",
            "",
            "        result_table = weibull_fit.results",
            "",
            "        # In the reliability package, Alpha is the Weibull scale parameter (eta)",
            "        eta = float(",
            "            result_table.loc[",
            '                result_table["Parameter"] == "Alpha", "Point Estimate"',
            "            ].values[0]",
            "        )",
            "",
            "        beta = float(",
            "            result_table.loc[",
            '                result_table["Parameter"] == "Beta", "Point Estimate"',
            "            ].values[0]",
            "        )",
            "",
            "        # Mean time to failure for a 2-parameter Weibull",
            "        mttf = eta * gamma(1 + 1 / beta)",
            "",
            "        # Classify failure-rate behavior from the shape parameter",
            "        if beta < 0.9:",
            "            hazard = \"Decreasing\"",
            "        elif beta <= 1.1:",
            "            hazard = \"Constant\"",
            "        else:",
            "            hazard = \"Increasing\"",
            "",
            "        summary = {",
            '            "Test_Type": test_name,',
            '            "Temp_C": temp,',
            '            "Volt_V": voltage,',
            '            "Humidity_%": humidity,',
            '            "Total_Devices": len(group_data),',
            '            "Failed_Devices": len(failures),',
            '            "Censored_Devices": len(censored),',
            '            "Beta": beta,',
            '            "Eta": eta,',
            '            "MTTF": mttf,',
            '            "Hazard": hazard,',
            "        }",
            "",
            "        results.append(summary)",
            "",
            "    return pd.DataFrame(results)",
            "",
            "",
            "# Fit all qualifying groups and display the summary table",
            "result = fit_groups(df)",
            "print(result)",
        ],
    )

    set_source(
        cells[4],
        [
            "# Inspect THB results sorted by humidity to compare moisture stress levels",
            "result[result[\"Test_Type\"] == \"THB\"].sort_values(\"Humidity_%\")",
        ],
    )

    set_source(
        cells[5],
        [
            "## Kaplan-Meier Survival Analysis",
            "",
            "Non-parametric survival curves grouped by test type and temperature. Censored devices contribute survival information up to the test end time without counting as failures.",
        ],
    )

    set_source(
        cells[6],
        [
            "def plot_survival_curve(df):",
            '    """Plot Kaplan-Meier survival curves for each test type and temperature."""',
            "    km = KaplanMeierFitter()",
            "",
            "    plt.figure(figsize=(8, 5))",
            "",
            "    groups = df.groupby([\"Test_Type\", \"Stress_Temperature_C\"])",
            "",
            "    for (test_type, temp), group_data in groups:",
            "        survival_time = group_data[\"Failure_Time_Hours\"]",
            "",
            "        # lifelines expects 1 for failure observed, 0 for censored",
            "        event_data = 1 - group_data[\"Censored\"]",
            "",
            "        label_name = f\"{test_type} {temp}\u00b0C\"",
            "",
            "        km.fit(",
            "            durations=survival_time,",
            "            event_observed=event_data,",
            "            label=label_name,",
            "        )",
            "        km.plot()",
            "",
            "    plt.title(\"Kaplan-Meier Survival Curve\")",
            "    plt.xlabel(\"Time (Hours)\")",
            "    plt.ylabel(\"Survival Probability\")",
            "    plt.grid(True)",
            "    plt.show()",
            "",
            "",
            "plot_survival_curve(df)",
        ],
    )

    set_source(
        cells[7],
        [
            "## Weibull Probability Plot",
            "",
            "A linearized probability plot checks how well the failure data follow a Weibull distribution. Points near a straight line indicate a good fit.",
        ],
    )

    set_source(
        cells[8],
        [
            "def show_weibull_probability_plot(df, temperature, voltage):",
            '    """Fit and plot a Weibull probability plot for one HTOL stress condition."""',
            "    selected_data = df[",
            '        (df["Test_Type"] == "HTOL")',
            '        & (df["Stress_Temperature_C"] == temperature)',
            '        & (df["Stress_Voltage_V"] == voltage)',
            "    ]",
            "",
            "    failures = selected_data.loc[",
            '        selected_data["Censored"] == 0, "Failure_Time_Hours"',
            "    ].values",
            "",
            "    censored = selected_data.loc[",
            '        selected_data["Censored"] == 1, "Failure_Time_Hours"',
            "    ].values",
            "",
            "    Fit_Weibull_2P(",
            "        failures=failures,",
            "        right_censored=censored,",
            "        show_probability_plot=True,",
            "        print_results=False,",
            "    )",
            "",
            "    plt.show()",
            "",
            "",
            "# HTOL at the hottest temperature and highest voltage (most aggressive stress)",
            "show_weibull_probability_plot(df, temperature=150, voltage=5.0)",
        ],
    )

    set_source(
        cells[9],
        [
            "# HTOL at a milder stress condition for comparison with the plot above",
            "show_weibull_probability_plot(df, temperature=100, voltage=4)",
        ],
    )

    set_source(
        cells[10],
        [
            "## Notes on Plot Scatter",
            "",
            "The generated dataset intentionally incorporates batch-to-batch and device-to-device variability. Weibull probability plots may therefore show moderate deviations from ideal linear behavior, especially at low failure probabilities, similar to practical semiconductor reliability datasets.",
        ],
    )

    set_source(
        cells[11],
        [
            "## Beta vs Temperature",
            "",
            "Beta is the Weibull shape parameter. Values above 1 indicate an increasing failure rate over time (wear-out behavior).",
        ],
    )

    set_source(
        cells[12],
        [
            "def plot_beta_vs_temperature(result):",
            '    """Plot fitted Weibull beta (shape) versus stress temperature by test program."""',
            "    plt.figure(figsize=(8, 5))",
            "",
            "    for test_type, group_data in result.groupby(\"Test_Type\"):",
            "        plt.plot(",
            '            group_data["Temp_C"],',
            '            group_data["Beta"],',
            '            marker="o",',
            "            label=test_type,",
            "        )",
            "",
            "    plt.title(\"Weibull Beta vs Temperature\")",
            "    plt.xlabel(\"Temperature (\u00b0C)\")",
            "    plt.ylabel(\"Beta\")",
            "    plt.grid(True)",
            "    plt.legend()",
            "    plt.show()",
            "",
            "",
            "plot_beta_vs_temperature(result)",
        ],
    )

    set_source(
        cells[13],
        [
            "## Eta vs Temperature",
            "",
            "Eta is the Weibull scale parameter (characteristic life). Lower eta at higher temperature reflects accelerated failure under thermal stress.",
        ],
    )

    set_source(
        cells[14],
        [
            "def plot_eta_vs_temperature(result):",
            '    """Plot fitted Weibull eta (scale) versus stress temperature by test program."""',
            "    plt.figure(figsize=(8, 5))",
            "",
            "    for test_type, group_data in result.groupby(\"Test_Type\"):",
            "        plt.plot(",
            '            group_data["Temp_C"],',
            '            group_data["Eta"],',
            '            marker="o",',
            "            label=test_type,",
            "        )",
            "",
            "    plt.title(\"Weibull Eta vs Temperature\")",
            "    plt.xlabel(\"Temperature (\u00b0C)\")",
            "    plt.ylabel(\"Eta (Hours)\")",
            "    plt.grid(True)",
            "    plt.legend()",
            "    plt.show()",
            "",
            "",
            "plot_eta_vs_temperature(result)",
        ],
    )

    set_source(
        cells[15],
        [
            "## Arrhenius Analysis",
            "",
            "For HTOL data, plotting ln(eta) versus 1/T should be approximately linear when temperature acceleration follows the Arrhenius model.",
        ],
    )

    set_source(
        cells[16],
        [
            "def plot_arrhenius_analysis(result_table):",
            '    """',
            "    Linearize HTOL eta values on an Arrhenius plot: ln(eta) vs 1/T.",
            "",
            "    A straight-line fit estimates the temperature dependence of characteristic life.",
            '    """',
            "    htol_data = result_table[result_table[\"Test_Type\"] == \"HTOL\"].copy()",
            "    htol_data[\"Temp_K\"] = htol_data[\"Temp_C\"] + 273.15",
            "",
            "    inverse_temperature = 1 / htol_data[\"Temp_K\"]",
            "    log_eta = np.log(htol_data[\"Eta\"])",
            "",
            "    # First-order polynomial fit: ln(eta) = slope * (1/T) + intercept",
            "    coefficients = np.polyfit(inverse_temperature, log_eta, 1)",
            "    slope, intercept = coefficients[0], coefficients[1]",
            "",
            "    x_fit = np.linspace(inverse_temperature.min(), inverse_temperature.max(), 100)",
            "    y_fit = slope * x_fit + intercept",
            "",
            "    plt.figure(figsize=(7, 5))",
            "    plt.scatter(inverse_temperature, log_eta, label=\"HTOL Data\")",
            "    plt.plot(x_fit, y_fit, label=\"Arrhenius Fit\")",
            "    plt.title(\"Arrhenius Analysis\")",
            "    plt.xlabel(\"1 / Temperature (1/K)\")",
            "    plt.ylabel(\"ln(Eta)\")",
            "    plt.grid(True)",
            "    plt.legend()",
            "    plt.show()",
            "",
            "    print(\"Intercept =\", intercept)",
            "    print(\"Slope =\", slope)",
            "",
            "",
            "# Re-fit before plotting so this cell can be run independently",
            "result = fit_groups(df)",
            "plot_arrhenius_analysis(result)",
        ],
    )


def main():
    for name, updater in [
        ("data_generation.ipynb", update_data_generation),
        ("reliability_analysis.ipynb", update_reliability_analysis),
    ]:
        path = ROOT / name
        with open(path, encoding="utf-8") as f:
            nb = json.load(f)

        updater(nb)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")

        print(f"Updated {name}")


if __name__ == "__main__":
    main()
