# Related Work {#sec:related_work}

## Active inference and model specification

The free energy principle and discrete active inference supply the background for the distinction between state inference and model specification \cite{friston2010free,dacosta2020active}. Expected free energy balances information gain and outcome preferences under a predictive model \cite{friston2015epistemic}. The variational assumptions behind planning require care: expected free energy is not obtained by simply substituting future observations into the usual variational objective \cite{millidge2021whence}. Our implementation is deliberately limited to categorical models with known likelihood and transition matrices.

Methods and software already address learning, hierarchical models, and practical computation \cite{friston2016active,smith2022step,heins2022pymdp}. Thus, our meta-level interpretation does not introduce model learning to active inference. Its contribution is a classification of specification and monitoring choices, coupled to explicit examples that can be checked computationally.

Recent work studies scale-free generative models, variational planning, and interpretable graph-based agents \cite{friston2025scalefree,devries2025planning,feps2025}. These are distinct technical architectures, not implementations or validation of the quadrants proposed here. We include them to clarify the surrounding research program, without importing their performance claims into our results.

## Monitoring, control, and calibration

The distinction between monitoring and control predates this taxonomy \cite{flavell1979metacognition,nelson1990metamemory}. Confidence, calibration, discrimination, and metacognitive efficiency are different quantities \cite{fleming2014measure}. A concentrated posterior can be confidently wrong under model misspecification. Accordingly, the experiment reports Brier loss and log loss rather than treating posterior concentration as evidence of correctness.

MetaMind and SOFAI provide contemporary examples of metacognitive organization in artificial systems \cite{metamind2025,sofai2025}. Their tasks and mechanisms differ from our binary sensor setting. An architectural analogy does not establish shared statistical behavior or biological equivalence.

## Relation to reinforcement learning and Bayesian decision theory

The difference between specifying outcome preferences and specifying rewards is useful, but it is not an absolute division between inspectable and opaque objectives. If preferences are encoded as $p_C(o)\propto\exp(\beta r(o))$, the expected log-preference term corresponds to expected reward up to a scale and normalization constant. Epistemic value adds a particular information-seeking objective. Active inference and model-based reinforcement learning have operational connections \cite{tschantz2019scaling,sajid2021active}; both require assumptions about observations, actions, and values.

Our question is therefore comparative: which explicit reliability or monitoring mechanism changes behavior under a specified environment and resource budget? The four labels do not determine the answer in advance.

## Safety and information integrity

Objective specification, distribution shift, and oversight are established concerns in AI safety \cite{amodei2016concrete,gabriel2020artificial}. We use the quadrants to organize where an intervention acts: on observations, metadata, monitoring rules, or model revision. We do not infer human susceptibility, attack success probabilities, or alignment guarantees from the taxonomy. The misleading-metadata control is a controlled synthetic failure case, not a deployment security evaluation.
