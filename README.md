# Depression Risk Screening: A Hybrid Analytical Approach

## Executive Summary
This project addresses the critical challenge of under-diagnosed depression in the general population. By analyzing 20,000+ records from the National Health and Nutrition Examination Survey (NHANES), we developed a high-sensitivity screening protocol capable of identifying at-risk individuals who might otherwise be overlooked in primary care.

**Our Philosophy:** Data tells a story, but only if you listen with the right tools.
> "I used a hybrid analytical approach: Machine Learning to identify critical signals among 50+ variables, followed by traditional statistical visualization to uncover the 'human story' behind the data."

![Depression Prevalence](plots/depression.png)
*Figure 1: Distribution of depression risk in the study cohort based on PHQ-9 scores.*

---

## 1. Machine Learning: Signal Detection
To navigate the complexity of 50+ physiological and socioeconomic variables, we employed an ensemble of Machine Learning algorithms, including Random Forest and XGBoost. This was not about "black box" prediction, but about **feature discovery**.

Using Random Forest feature importance analysis, we isolated the primary drivers of depression risk from the noise.

![Feature Importance](plots/feature_importance.png)
*Figure 2: Top predictive features identified by the Random Forest model. Note the dominance of General Health, Sleep, and Socioeconomic factors.*

---

## 2. Statistical Analysis: The Human Story
Once the key signals were identified by the algorithms, we switched to targeted statistical analysis to understand the *nature* of these relationships.

### The Socioeconomic Gradient
Wealth is often cited as a buffer against mental health struggles. Our data quantifies this protective effect, showing a stark, linear gradient: as the Poverty Income Ratio increases, depression prevalence plummets.

![Wealth Gradient](plots/wealth_Depression_Gradient.png)
*Figure 3: The inverse relationship between household wealth (Poverty Income Ratio) and depression prevalence.*

### The Role of Sleep
Sleep quality emerged as a top-tier predictor in our ML models. The statistical breakdown confirms a massive disparity: individuals with doctor-confirmed sleep trouble have a drastically higher prevalence of depression compared to good sleepers.

![Sleep Analysis](plots/Sleep_Trouble.png)
*Figure 4: Prevalence of depression among individuals with and without reported sleep disorders.*

### Social Structure: Marriage
Social support systems play a pivotal role in mental resilience. Our analysis suggests that the stability often associated with marriage correlates with the lowest risk profile, whereas separated and widowed individuals face significantly higher risks.

![Marital Status](plots/marital_Status_Impact.png)
*Figure 5: Depression rates across different marital statuses.*

---

## 3. The "Curious Case": Mercury
In our broad exploratory analysis, we uncovered a counter-intuitive correlation: higher blood mercury levels were associated with *lower* depression rates. 

While initially puzzling, this is likely a **confounding variable** representing diet and wealth. High mercury levels are often linked to high consumption of expensive seafood (e.g., tuna, swordfish), which is a diet characteristic of higher socio-economic status. Thus, mercury acts as a proxy for wealth, which we already established is protective.

![Mercury Analysis](plots/mercury_Analysis.png)
*Figure 6: The unexpected inverse correlation between blood mercury levels and depression, likely mediated by socioeconomic status.*

---

## Conclusion
Depression is a complex, multifaceted disease with no single cause. Through this project, we have successfully identified several significant correlations—ranging from sleep hygiene to economic stability—that can aid in early screening.

**Crucial Note:** It is vital to interpret these findings with scientific rigor. While we have established strong predictive correlations, **correlation is not causation**. These markers serve as flags for risk, not necessarily as root causes, but they provide invaluable guidance for targeted intervention and further clinical study.