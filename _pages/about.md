---
layout: about
title: About
permalink: /
subtitle: Ph.D. Student in Computer Science, <a href='https://www.cs.fsu.edu/'>Florida State University</a>. Advised by <a href='https://guangwang.me/'>Prof. Guang Wang</a>.

profile:
  align: right
  image: prof_pic.jpg
  image_alt: Portrait of Dahai Yu # without this, the alt text is the file name
  image_circular: false # crops the image to make it circular
  more_info: >
    <p>Dept. of Computer Science</p>
    <p>Florida State University</p>
    <p>Tallahassee, FL 32306, USA</p>
    <p><a href="mailto:dahai.yu@fsu.edu">dahai.yu@fsu.edu</a></p>

selected_papers: true # includes a list of papers marked as "selected={true}"
social: false # icons live in the navbar instead (see enable_navbar_social)

announcements:
  enabled: true # includes a list of news items
  scrollable: true # adds a vertical scroll bar if there are more than 3 news items
  limit: 5 # leave blank to include all the news in the `_news` folder

latest_posts:
  enabled: false
  scrollable: true
  limit: 3
---

I am a Computer Science Ph.D. student at **Florida State University**, advised by [Prof. Guang Wang](https://guangwang.me/). Before coming to FSU, I received my B.S. in Big Data Management and Application from the **Department of Information Management, Peking University**, where I worked with Prof. Bolin Hua on text mining for scientific literature.

My research builds **trustworthy machine learning systems for the physical world**. Concretely, I work on uncertainty quantification for spatiotemporal prediction, generative models for mobility and energy data, and decision-making pipelines that stay reliable when the downstream stakes are high — energy demand, healthcare access, and post-disaster power restoration.

Recurring threads in my work:

- **Uncertainty-aware spatiotemporal prediction.** Graph neural networks and selective state space models that report calibrated uncertainty alongside their point predictions ([UQGNN](/publications/#yu2025uqgnn), [TrustEnergy](/publications/#yu2026trustenergy), [HealthMamba](/publications/#yu2026healthmamba), [EnergyMamba](/publications/#yu2026energymamba)).
- **Generative models for urban and energy data.** Diffusion models that synthesize or repair mobility traces, human activity, and utility readings when real data is scarce, private, or incomplete ([SynHAT](/publications/#xu2026synhat), [MobiDiff](/publications/#xu2026mobidiff), [MBDiff](/publications/#xu2026mbdiff), [SynEnergy](/publications/#jiang2026synenergy), [E4GEN](/publications/#jiang2026e4gen)).
- **Uncertainty quantification for LLM reasoning.** Estimating when a fluent reasoning trace should be trusted, using answer re-elicitation and symbolic verification ([TrAC](/publications/#yu2026trac), [SymboUQ](/publications/#yu2026symbouq)).
- **From prediction to decisions.** Predict-then-optimize pipelines where the uncertainty estimate actually changes the allocation — e.g. [equitable post-disaster power restoration](/publications/#jiang2025epopr).

My work has appeared at AAAI, IJCAI, ACM SIGKDD, ACM SIGSPATIAL, and ACM IMWUT (UbiComp), and I received the **Dean's Award for Doctoral Excellence** from Florida State University in 2026, and the **Challenge Cup Second Prize** and a **Third Prize Scholarship** at Peking University. I am always happy to talk about spatiotemporal foundation models, calibration, or urban data — feel free to reach out.
